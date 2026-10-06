"""Renderiza cópias de QA do DOCX/PPTX com o LibreOffice instalado."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Projeto_Final_Artefatos"
QA = ROOT / "tmp" / "video-review"
QA.mkdir(parents=True, exist_ok=True)
binary = shutil.which("soffice")
if not binary:
    raise SystemExit("Instale LibreOffice e disponibilize soffice no PATH para renderizar o QA.")
with tempfile.TemporaryDirectory(prefix="insurminds-office-") as profile:
    subprocess.run([
        binary, "-env:UserInstallation=" + Path(profile).as_uri(), "--headless",
        "--convert-to", "pdf", "--outdir", str(QA),
        str(OUT / "InsurMinds_System_Design.docx"),
        str(OUT / "InsurMinds_Projeto_Final.pptx"),
    ], check=True, timeout=90)
for stem in ["InsurMinds_System_Design", "InsurMinds_Projeto_Final"]:
    path = QA / (stem + ".pdf")
    with pymupdf.open(path) as doc:
        for i, page in enumerate(doc):
            page.get_pixmap(matrix=pymupdf.Matrix(1.4, 1.4)).save(str(QA / f"{stem}-{i+1}.png"))
        print(f"{stem}: {len(doc)} páginas renderizadas.")
