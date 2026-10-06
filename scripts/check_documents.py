"""Valida PDFs pela API em uma biblioteca isolada.

Sem caminhos, usa os dois PDFs fictícios do projeto.
Use --preflight-only para conferir a leitura sem chamar o Gemini.
Resultados e checkpoints ficam em tmp/document-checks/.
"""
import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from starlette.testclient import TestClient
from backend.app import app, tasks
from backend import storage
from backend.documents import read_document
from backend.agents import split_pages, configured


async def tick():
    if tasks:
        await asyncio.wait(list(tasks), timeout=15)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", type=Path, nargs="*", default=[
        ROOT / "Projeto_Final_Artefatos/exemplos/Apolice_Aurora_Ficticia.pdf",
        ROOT / "Projeto_Final_Artefatos/exemplos/Apolice_Vertice_Ficticia.pdf",
    ])
    parser.add_argument("--data-dir", type=Path, default=ROOT / "tmp/document-checks")
    parser.add_argument("--preflight-only", action="store_true", help="Não faz chamadas à IA.")
    args = parser.parse_args()
    args.data_dir.mkdir(parents=True, exist_ok=True)
    os.environ["DATA_DIR"] = str(args.data_dir.resolve())
    rows = []
    if not args.preflight_only and not configured():
        parser.error("Configure GEMINI_API_KEY no .env local.")
    with TestClient(app) as client:
        for path in args.files:
            data = path.read_bytes()
            row = {"filename": path.name}
            try:
                pages, mime = read_document(data, path.name)
                chunks = split_pages(pages)
                row.update(pages=len(pages), characters=sum(len(p['text']) for p in pages),
                           chunks=len(chunks), preflight="pass")
            except ValueError as exc:
                row.update(preflight="fail", error=str(exc))
                rows.append(row)
                print(json.dumps(row, ensure_ascii=False), flush=True)
                continue
            print(json.dumps(row, ensure_ascii=False), flush=True)
            if not args.preflight_only:
                previous = next((p for p in storage.all_items("policies")
                                 if not p["demo"] and p["filename"] == path.name
                                 and Path(p["file_path"]).exists() and Path(p["file_path"]).read_bytes() == data), None)
                if previous:
                    item_id = previous["id"]
                    if previous["status"] == "error":
                        response = client.post(f"/api/policies/{item_id}/retry")
                    else:
                        response = client.get(f"/api/policies/{item_id}")
                else:
                    response = client.post("/api/upload", files={"file": (path.name, data, mime)})
                    item_id = response.json().get("id")
                row["http"] = response.status_code
                if not item_id or response.status_code >= 400:
                    row.update(status="rejected", error=response.json().get("error"))
                else:
                    while True:
                        detail = client.get(f"/api/policies/{item_id}").json()
                        if detail["status"] in ("ready", "error"):
                            break
                        client.portal.call(tick)
                        print(json.dumps({"filename": path.name, "progress": client.get(f"/api/policies/{item_id}").json().get("progress")}, ensure_ascii=False), flush=True)
                    row.update(id=item_id, status=detail["status"], error=detail.get("error"),
                               models_used=detail.get("models_used", []), progress=detail.get("progress"),
                               facts=detail["facts"], warnings=detail["warnings"])
                    if row["status"] == "ready":
                        row["source_identical"] = client.get(f"/api/policies/{item_id}/source").content == data
                print(json.dumps({k: v for k, v in row.items() if k not in ("facts", "warnings")}, ensure_ascii=False), flush=True)
            rows.append(row)
            (args.data_dir / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))
        ids = list(dict.fromkeys(row["id"] for row in rows if row.get("status") == "ready"))
        if len(ids) >= 2:
            response = client.post("/api/comparisons", json={"policy_ids": ids[:4]})
            response.raise_for_status()
            comparison = response.json()
            (args.data_dir / "comparison.json").write_text(json.dumps(comparison, ensure_ascii=False, indent=2))
            exported = client.get(f"/api/comparisons/{comparison['id']}/export?format=json")
            assert exported.json()["rows"] == comparison["rows"]
            pdf = client.get(f"/api/comparisons/{comparison['id']}/export")
            assert pdf.content.startswith(b"%PDF"), "Exportação PDF inválida"
            print("Comparação e exportações JSON/PDF: OK", flush=True)
    (args.data_dir / "results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0 if all(row.get("status", row.get("preflight")) in ("ready", "pass") for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
