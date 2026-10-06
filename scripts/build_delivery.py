"""Gera PDFs didáticos, relatório técnico e ZIP por lista explícita de fontes."""
import argparse
import json
import re
import sys
from html import escape
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import pymupdf
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Preformatted

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from backend.demo import demo_pages
from backend.reports import sample_pdf, styles, footer

OUT = ROOT / "Projeto_Final_Artefatos"

def build_pdfs(report_only=False):
    OUT.mkdir(exist_ok=True)
    examples = OUT / "exemplos"
    examples.mkdir(exist_ok=True)
    for i, name in enumerate([] if report_only else ["Aurora", "Vertice"]):
        data = sample_pdf(demo_pages(i))
        (examples / f"Apolice_{name}_Ficticia.pdf").write_bytes(data)
        if i == 0:
            with pymupdf.open(stream=data, filetype="pdf") as doc:
                doc[0].get_pixmap(matrix=pymupdf.Matrix(1.6, 1.6)).save(str(examples / "Apolice_Aurora_Pagina_1.png"))
    s = styles()
    s["BodyText"].fontSize = 10
    s["BodyText"].leading = 14
    s["BodyText"].spaceAfter = 8
    s["Heading2"].spaceBefore = 17
    s["Heading2"].spaceAfter = 10
    s["Heading2"].keepWithNext = True
    s["Heading2"].textColor = colors.HexColor("#284e3b")
    code = ParagraphStyle("Code", fontName="Courier", fontSize=8, leading=12, backColor=colors.HexColor("#f0f3eb"), borderPadding=10, spaceAfter=14)
    bufpath = OUT / "InsurMinds_Relatorio_Tecnico.pdf"
    doc = SimpleDocTemplate(str(bufpath), pagesize=A4, leftMargin=48, rightMargin=48, topMargin=43, bottomMargin=45, title="InsurMinds - Relatório Técnico", author="Equipe InsurMinds")
    story = [Spacer(1, 70), Paragraph("INSURMINDS", s["Brand"]), Paragraph(escape("Plataforma inteligente para análise e comparação de apólices D&O"), s["Title"]), Spacer(1, 22), Paragraph("Relatório técnico | Projeto Final I2A2 2026", s["Heading2"]), Paragraph("Revisado em: 06/10/2026", s["BodyText"]), Spacer(1, 34), Paragraph("MVP local com extração estruturada por IA, evidências por página e comparação documental reproduzível.", s["BodyText"]), Spacer(1, 25), Paragraph("Equipe InsurMinds: Victor Hugo Araujo, João Carlos Mendonça, Adriéli Zacharias e Bruno Veiga.", s["BodyText"]), Paragraph("Situação da validação: dois PDFs fictícios foram analisados pelo Gemini 3.8 Flash: 16 critérios com evidências verificadas em cada documento; comparação com 10 diferenças e exportações PDF/JSON aprovadas. A interpretação dos valores é conferida pelo usuário. O repositório está público.", s["BodyText"]), PageBreak()]
    content = (ROOT / "docs" / "ARQUITETURA.md").read_text(encoding="utf-8")
    content = re.sub(r"```mermaid.*?```", "```\nInterface React\n    API Starlette\n        Recepção e leitura PDF / imagem\n        Extração multimodal Gemini\n        Validação de dados e evidências\n    SQLite e arquivos locais\n        Comparação de critérios\n        PDF / JSON e consulta contextual\n```", content, flags=re.S)
    blocks = re.split(r"\n\s*\n", content)
    for block in blocks:
        block = block.strip()
        if block.startswith("# "):
            story.append(Paragraph(escape(block[2:]), s["Title"]))
        elif block.startswith("## "):
            story.append(Paragraph(escape(block[3:]), s["Heading2"]))
        elif block.startswith("```"):
            story.append(Preformatted(block.strip('`\n'), code))
        else:
            clean = re.sub(r"`([^`]+)`", r"\1", block)
            for paragraph in clean.split("\n") if re.match(r"(?:\d+\.|-) ", clean) else [clean.replace("\n", " ")]:
                story.append(Paragraph(escape(paragraph), s["BodyText"]))
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    preview = ROOT / "tmp" / "pdfs"
    preview.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(bufpath) as pdf:
        for i, p in enumerate(pdf):
            p.get_pixmap(matrix=pymupdf.Matrix(1.1, 1.1)).save(str(preview / f"report-{i + 1}.png"))
        print(f"Relatório: {len(pdf)} páginas")
    for name in [] if report_only else ["Aurora", "Vertice"]:
        with pymupdf.open(examples / f"Apolice_{name}_Ficticia.pdf") as pdf:
            assert len(pdf) == 2
            for i, p in enumerate(pdf):
                p.get_pixmap().save(str(preview / f"{name.lower()}-{i + 1}.png"))

def build_zip():
    OUT.mkdir(exist_ok=True)
    archive = OUT / "InsurMinds_Codigo_Fonte.zip"
    folders = ["backend", "src", "public", "tests", "scripts", "docs", ".github", ".impeccable", "Projeto_Final_Artefatos"]
    root_files = ["README.md", "DESIGN.md", "PRODUCT.md", "components.json", "LICENSE", "requirements.txt", "package.json", "package-lock.json", "tsconfig.json", "vite.config.ts", "index.html", ".env.example", ".gitignore", ".gitattributes"]
    candidates = [ROOT / f for f in root_files]
    for folder in folders:
        candidates.extend((ROOT / folder).rglob("*"))
    files = [p for p in candidates if p.is_file() and p != archive and not any(part in ("__pycache__", ".DS_Store") for part in p.parts) and p.suffix not in (".pyc", ".zip") and (not p.name.startswith(".env") or p.name == ".env.example")]
    with ZipFile(archive, "w", ZIP_DEFLATED) as z:
        for p in sorted(set(files)):
            z.write(p, "insurminds/" + p.relative_to(ROOT).as_posix())
    with ZipFile(archive) as z:
        assert z.testzip() is None
        assert not any("/data/" in n or "/node_modules/" in n or n.endswith("/.env") for n in z.namelist())
        print(f"ZIP: {len(z.namelist())} arquivos, {archive.stat().st_size / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip-only", action="store_true")
    parser.add_argument("--report-only", action="store_true", help="Atualiza o relatório e ZIP preservando os PDFs de exemplo")
    args = parser.parse_args()
    if not args.zip_only:
        build_pdfs(report_only=args.report_only)
    build_zip()
