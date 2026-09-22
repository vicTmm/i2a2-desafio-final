"""Dados autorais sintéticos. Não representam seguradoras ou contratos reais."""
from datetime import datetime, timezone
from .models import FIELDS
from . import storage

VALUES = [
    ["Aurora Seguros (fictícia)", "Horizonte Tecnologia S.A. (fictícia)", "DEMO-2026-001", "01/01/2026 a 31/12/2026", "BRL 10.000.000,00", "BRL 32.500,00", "Side B: BRL 50.000,00 por reclamação. Side A: sem franquia.", "Mundial, exceto EUA e Canadá", "Contratada, sujeita às condições da apólice", "Contratada, sujeita às condições da apólice", "Não contratada", "Incluídos no limite agregado", "Sublimite de BRL 1.000.000,00", "Atos dolosos com decisão definitiva; danos corporais e materiais", "01/01/2023", "12 meses, sem prêmio adicional"],
    ["Vértice Seguros (fictícia)", "Horizonte Tecnologia S.A. (fictícia)", "DEMO-2026-002", "01/01/2026 a 31/12/2026", "BRL 15.000.000,00", "BRL 41.800,00", "Side B: BRL 100.000,00 por reclamação. Side A: sem franquia.", "Mundial, exceto EUA e Canadá", "Contratada, sujeita às condições da apólice", "Contratada, sujeita às condições da apólice", "Contratada exclusivamente para reclamações de valores mobiliários", "Incluídos no limite agregado", "Sublimite de BRL 2.000.000,00", "Atos dolosos com decisão definitiva; danos corporais e materiais; poluição", "01/01/2022", "24 meses, sem prêmio adicional"],
]

def demo_pages(index):
    values = VALUES[index]
    pages = []
    for page_index, keys in enumerate([list(FIELDS)[:8], list(FIELDS)[8:]]):
        title = "INSURMINDS - DOCUMENTO FICTÍCIO PARA DEMONSTRAÇÃO"
        text = title + "\nSeguro de responsabilidade civil de administradores - D&O\n\n"
        for key in keys:
            text += f"{FIELDS[key][0]}: {values[list(FIELDS).index(key)]}.\n\n"
        text += "Material didático sem validade contratual. Não representa oferta de seguro."
        pages.append({"page": page_index + 1, "text": text, "image": None})
    return pages

def seed():
    from .reports import sample_pdf
    for index, values in enumerate(VALUES):
        item_id = f"demo-{index + 1}"
        if storage.get("policies", item_id):
            continue
        pages = demo_pages(index)
        facts = [{"key": key, "value": values[i], "quote": f"{FIELDS[key][0]}: {values[i]}.", "page": 1 if i < 8 else 2, "evidence_status": "verified"} for i, key in enumerate(FIELDS)]
        path = storage.root() / f"{item_id}.pdf"
        path.write_bytes(sample_pdf(pages))
        storage.save("policies", {"id": item_id, "title": "D&O " + ("Essencial" if index == 0 else "Ampliada"), "filename": f"apolice-{['aurora', 'vertice'][index]}-demonstracao.pdf", "status": "ready", "demo": True, "created_at": datetime.now(timezone.utc).isoformat(), "pages": pages, "facts": facts, "warnings": ["Exemplo fictício com extração pré-preenchida. Não foi processado por IA."], "model": "fixture", "mime": "application/pdf", "file_path": str(path)})
