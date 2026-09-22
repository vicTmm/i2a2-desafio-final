import base64
import io
import pymupdf
from PIL import Image, UnidentifiedImageError

MAX_BYTES = 20 * 1024 * 1024
MAX_PAGES = 60

def read_document(data: bytes, filename: str):
    if not data or len(data) > MAX_BYTES:
        raise ValueError("Envie um arquivo não vazio de até 20 MB.")
    if data.startswith(b"%PDF-"):
        try:
            with pymupdf.open(stream=data, filetype="pdf") as doc:
                if doc.needs_pass:
                    raise ValueError("PDF protegido por senha. Envie uma cópia desbloqueada.")
                if not 1 <= len(doc) <= MAX_PAGES:
                    raise ValueError("O MVP aceita PDFs de 1 a 60 páginas.")
                pages = []
                for i, page in enumerate(doc):
                    text = page.get_text(sort=True).strip()
                    image = None
                    if len(text) < 80:
                        # Leitura visual para páginas digitalizadas, inclusive PDFs mistos.
                        scale = min(1.5, 1600 / max(page.rect.width, page.rect.height))
                        pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale))
                        image = "data:image/png;base64," + base64.b64encode(pix.tobytes("png")).decode()
                    pages.append({"page": i + 1, "text": text, "image": image})
                return pages, "application/pdf"
        except (pymupdf.FileDataError, RuntimeError) as exc:
            raise ValueError("Não foi possível ler este PDF.") from exc
    try:
        with Image.open(io.BytesIO(data)) as im:
            if im.format not in ("PNG", "JPEG", "WEBP"):
                raise ValueError("Formato não suportado. Use PDF, PNG, JPG ou WebP.")
            original_mime = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}[im.format]
            im.verify()
        with Image.open(io.BytesIO(data)) as im:
            im.thumbnail((1800, 1800))
            out = io.BytesIO()
            im.convert("RGB").save(out, format="JPEG", quality=90)
        return [{"page": 1, "text": "", "image": "data:image/jpeg;base64," + base64.b64encode(out.getvalue()).decode()}], original_mime
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("Arquivo inválido. Use PDF, PNG, JPG ou WebP.") from exc
