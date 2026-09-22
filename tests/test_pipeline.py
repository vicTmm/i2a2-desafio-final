import asyncio
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch, AsyncMock
import pymupdf
from PIL import Image
from starlette.testclient import TestClient
from backend import agents, storage
from backend.app import app
from backend.models import Fact, Extraction, FIELDS
from backend.documents import read_document, MAX_BYTES
from backend.demo import demo_pages, VALUES
from backend.reports import sample_pdf


class DocumentTests(unittest.TestCase):
    def test_text_pdf_preserves_page_number(self):
        pages, mime = read_document(sample_pdf(demo_pages(0)), "sample.pdf")
        self.assertEqual(len(pages), 2)
        self.assertEqual(mime, "application/pdf")
        self.assertIn("BRL 10.000.000,00", pages[0]["text"])
        self.assertIn("Side A", pages[1]["text"])
        self.assertTrue(all(p["image"] is None for p in pages))

    def test_image_and_scanned_pdf_use_vision(self):
        image = Image.new("RGB", (200, 200), "white")
        buf = io.BytesIO()
        image.save(buf, "PNG")
        pages, mime = read_document(buf.getvalue(), "scan.pdf")
        self.assertEqual(mime, "image/png")  # Conteúdo, não extensão, determina o formato.
        self.assertTrue(pages[0]["image"].startswith("data:image/jpeg;base64,"))
        with pymupdf.open() as doc:
            doc.new_page().insert_image(pymupdf.Rect(0, 0, 200, 200), stream=buf.getvalue())
            pages, _ = read_document(doc.tobytes(), "scan.pdf")
        self.assertTrue(pages[0]["image"])

    def test_reject_empty_invalid_and_oversize(self):
        for data in [b"", b"not a PDF", b"x" * (MAX_BYTES + 1)]:
            with self.assertRaises(ValueError):
                read_document(data, "contract.pdf")

    def test_reject_encrypted_pdf(self):
        with pymupdf.open() as doc:
            doc.new_page()
            data = doc.tobytes(encryption=pymupdf.PDF_ENCRYPT_AES_256, owner_pw="owner", user_pw="secret")
        with self.assertRaisesRegex(ValueError, "senha"):
            read_document(data, "secret.pdf")

    def test_reject_too_many_pages(self):
        with pymupdf.open() as doc:
            for _ in range(61):
                doc.new_page()
            data = doc.tobytes()
        with self.assertRaisesRegex(ValueError, "60"):
            read_document(data, "long.pdf")


class EvidenceTests(unittest.TestCase):
    def extraction(self, facts):
        return Extraction(document_type="do_policy", title="D&O", facts=facts, warnings=[])

    def test_invented_quote_is_discarded(self):
        facts, warnings = agents.validate_extraction(self.extraction([Fact(key="limit", value="BRL 99", quote="inexistente", page=1)]), demo_pages(0))
        self.assertIsNone(next(f for f in facts if f["key"] == "limit")["value"])
        self.assertTrue(warnings)

    def test_out_of_range_page_is_discarded(self):
        facts, _ = agents.validate_extraction(self.extraction([Fact(key="limit", value="BRL 99", quote="x", page=99)]), demo_pages(0))
        self.assertTrue(all(f["value"] is None for f in facts))

    def test_normalized_quote_is_verified(self):
        facts, _ = agents.validate_extraction(self.extraction([Fact(key="limit", value="BRL 10.000.000,00", quote="Limite de responsabilidade:\nBRL 10.000.000,00.", page=1)]), demo_pages(0))
        self.assertEqual(next(f for f in facts if f["key"] == "limit")["evidence_status"], "verified")

    def test_visual_evidence_requires_human_review(self):
        facts, warnings = agents.validate_extraction(self.extraction([Fact(key="limit", value="BRL 99", quote="Limite: BRL 99", page=1)]), [{"text": "", "image": "data:image/png;base64,test", "page": 1}])
        self.assertEqual(next(f for f in facts if f["key"] == "limit")["evidence_status"], "visual_review")
        self.assertTrue(warnings)

    def test_duplicate_fields_rejected(self):
        f = Fact(key="limit", value=None, quote=None, page=None)
        with self.assertRaises(ValueError):
            agents.validate_extraction(self.extraction([f, f]), demo_pages(0))

    def test_missing_is_not_equal_or_excluded(self):
        facts, _ = agents.validate_extraction(self.extraction([]), demo_pages(0))
        rows = agents.compare([{"facts": facts}, {"facts": facts}])
        self.assertEqual(len(rows), 16)
        self.assertTrue(all(r["status"] == "missing" for r in rows))


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"DATA_DIR": self.tmp.name, "OPENAI_API_KEY": ""})
        self.env.start()
        self.client = TestClient(app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.env.stop()
        self.tmp.cleanup()

    def test_empty_library_and_demo_idempotence(self):
        self.assertEqual(self.client.get("/api/policies").json(), [])
        self.client.post("/api/demo")
        res = self.client.post("/api/demo")
        self.assertEqual(len(res.json()), 2)
        self.assertTrue(all(p["demo"] for p in res.json()))
        self.assertNotIn("file_path", res.json()[0])

    def test_comparison_history_and_exports(self):
        self.client.post("/api/demo")
        res = self.client.post("/api/comparisons", json={"policy_ids": ["demo-1", "demo-2"]})
        self.assertEqual(res.status_code, 201)
        comparison = res.json()
        self.assertEqual(len(comparison["rows"]), 16)
        self.assertEqual(sum(r["status"] == "different" for r in comparison["rows"]), 10)
        self.assertEqual(len(self.client.get("/api/comparisons").json()), 1)
        self.assertEqual(storage.get("comparisons", comparison["id"])["id"], comparison["id"])
        pdf = self.client.get(f"/api/comparisons/{comparison['id']}/export")
        self.assertTrue(pdf.content.startswith(b"%PDF"))
        with pymupdf.open(stream=pdf.content, filetype="pdf") as doc:
            self.assertIn("DEMONSTRAÇÃO", "".join(p.get_text() for p in doc))
        exported = self.client.get(f"/api/comparisons/{comparison['id']}/export?format=json").json()
        self.assertEqual(exported["rows"], comparison["rows"])

    def test_duplicate_and_insufficient_comparisons(self):
        self.client.post("/api/demo")
        for ids in [["demo-1"], ["demo-1", "demo-1"]]:
            self.assertEqual(self.client.post("/api/comparisons", json={"policy_ids": ids}).status_code, 400)
        self.assertEqual(self.client.get("/api/policies/not-found").status_code, 404)

    def test_no_key_returns_actionable_error_without_fake_ai(self):
        res = self.client.post("/api/upload", files={"file": ("test.pdf", sample_pdf(demo_pages(0)), "application/pdf")})
        self.assertEqual(res.status_code, 503)
        self.assertIn("OPENAI_API_KEY", res.json()["error"])
        self.assertEqual(self.client.get("/api/policies").json(), [])

    def test_upload_processing_with_mocked_provider(self):
        facts = [Fact(key=k, value=VALUES[0][i], quote=f"{FIELDS[k][0]}: {VALUES[0][i]}.", page=1 if i < 8 else 2) for i, k in enumerate(FIELDS)]
        extraction = Extraction(document_type="do_policy", title="D&O extraído", facts=facts, warnings=[])
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-not-real"}), patch("backend.agents.response", new=AsyncMock(return_value=extraction.model_dump_json())):
            response = self.client.post("/api/upload", files={"file": ("../example.pdf", sample_pdf(demo_pages(0)), "application/pdf")})
            self.assertEqual(response.status_code, 202)
            item_id = response.json()["id"]
            # Explicitly wait for this app's background tasks in the TestClient event loop.
            from backend.app import tasks
            async def wait_tasks():
                if tasks:
                    await asyncio.gather(*list(tasks))
            self.client.portal.call(wait_tasks)
            p = self.client.get("/api/policies/" + item_id).json()
            self.assertEqual(p["status"], "ready", p)
            self.assertFalse(p["demo"])
            self.assertEqual(p["filename"], "example.pdf")
            self.assertTrue(all(f["evidence_status"] == "verified" for f in p["facts"]))
            self.assertTrue(self.client.get("/api/policies/" + item_id + "/source").content.startswith(b"%PDF"))

    def test_provider_failure_is_saved_and_retryable(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-not-real"}), patch("backend.agents.response", new=AsyncMock(side_effect=agents.ProviderError("Limite da API"))):
            response = self.client.post("/api/upload", files={"file": ("test.pdf", sample_pdf(demo_pages(0)), "application/pdf")})
            item_id = response.json()["id"]
            from backend.app import tasks
            async def wait_tasks():
                if tasks:
                    await asyncio.gather(*list(tasks))
            self.client.portal.call(wait_tasks)
            p = self.client.get("/api/policies/" + item_id).json()
            self.assertEqual(p["status"], "error")
            self.assertEqual(p["error"], "Limite da API")

    def test_corrupt_upload_rejected(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-not-real"}):
            response = self.client.post("/api/upload", files={"file": ("test.pdf", b"invalid", "application/pdf")})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
