import asyncio
import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import pymupdf
from starlette.testclient import TestClient
from backend import agents, checkpoints, storage
from backend.app import app, tasks
from backend.documents import read_document
from backend.models import Extraction, Fact, Evidence


def page(number, text, image=None):
    return {"page": number, "text": text, "image": image}


def extraction(value, quote, number, kind="do_policy"):
    return Extraction(document_type=kind, title="D&O", warnings=[], facts=[
        Fact(key="limit", value=value, quote=quote, page=number)])


class ChunkTests(unittest.TestCase):
    def test_long_documents_keep_every_page_and_original_numbers(self):
        pages = [page(i, "texto " * 900) for i in range(1, 115)]
        chunks = agents.split_pages(pages)
        self.assertGreater(len(chunks), 1)
        self.assertEqual([p for c in chunks for p in c], pages)
        for chunk in chunks:
            self.assertLessEqual(sum(len(p["text"]) for p in chunk), agents.CHUNK_CHARS)
            self.assertLessEqual(len(chunk), agents.CHUNK_PAGES)

    def test_large_single_page_and_many_scans_are_split_without_loss(self):
        text = "0123456789" * 14000
        chunks = agents.split_pages([page(77, text)])
        pieces = [p for chunk in chunks for p in chunk]
        reconstructed = pieces[0]["text"] + "".join(p["text"][500:] for p in pieces[1:])
        self.assertEqual(reconstructed, text)
        self.assertTrue(all(p["page"] == 77 for p in pieces))
        scans = agents.split_pages([page(i, "", "scan") for i in range(1, 26)])
        self.assertEqual(sum(len(c) for c in scans), 25)
        self.assertTrue(all(len(c) <= agents.CHUNK_IMAGES for c in scans))

    def test_accepts_large_pdf_within_limits(self):
        with pymupdf.open() as doc:
            for _ in range(114):
                doc.new_page().insert_text((50, 50), "Policy D&O " * 12)
            pages, _ = read_document(doc.tobytes(), "large.pdf")
        self.assertEqual(len(pages), 114)
        self.assertEqual(pages[-1]["page"], 114)

    def test_non_contiguous_original_page_and_multiple_evidence(self):
        pages = [page(40, "Limite 100"), page(41, "Exceção 50")]
        result = extraction("100; exceção 50", "Limite 100", 40)
        result.facts[0].evidence = [Evidence(quote="Limite 100", page=40), Evidence(quote="Exceção 50", page=41)]
        facts, _ = agents.validate_extraction(result, pages)
        limit = next(f for f in facts if f["key"] == "limit")
        self.assertEqual([e["page"] for e in limit["evidence"]], [40, 41])
        result.facts[0].evidence[-1].page = 1
        facts, _ = agents.validate_extraction(result, pages)
        self.assertIsNone(next(f for f in facts if f["key"] == "limit")["value"])

    def test_distinct_values_are_preserved_with_their_own_sources(self):
        results = []
        for number, value in [(1, "100"), (42, "50")]:
            facts, _ = agents.validate_extraction(extraction(value, value, number), [page(number, value)])
            results.append(facts)
        facts, warnings = agents.merge_facts(results)
        limit = next(f for f in facts if f["key"] == "limit")
        self.assertTrue(limit["needs_review"])
        self.assertEqual([v["value"] for v in limit["variants"]], ["100", "50"])
        self.assertEqual(limit["variants"][1]["evidence"][0]["page"], 42)
        self.assertTrue(warnings)

    def test_equal_values_keep_all_evidence_without_conflict(self):
        results = [agents.validate_extraction(extraction("100", "100", n), [page(n, "100")])[0] for n in [1, 42]]
        facts, warnings = agents.merge_facts(results)
        limit = next(f for f in facts if f["key"] == "limit")
        self.assertEqual(limit["value"], "100")
        self.assertFalse(limit["needs_review"])
        self.assertEqual(len(limit["evidence"]), 2)
        self.assertEqual(warnings, [])

    def test_comparison_ignores_page_numbers_but_preserves_distinct_values(self):
        policies = []
        for start in [1, 40]:
            parts = [agents.validate_extraction(extraction(value, value, start + i), [page(start + i, value)])[0]
                     for i, value in enumerate(["100", "50"])]
            policies.append({"facts": agents.merge_facts(parts)[0]})
        limit = next(row for row in agents.compare(policies) if row["key"] == "limit")
        self.assertEqual(limit["status"], "same")


class ResumeTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"DATA_DIR": self.temp.name})
        self.env.start()

    async def asyncTearDown(self):
        self.env.stop()
        self.temp.cleanup()

    async def test_failure_then_resume_skips_completed_chunk(self):
        pages = [page(1, "100"), page(2, "50")]
        with patch.object(agents, "CHUNK_PAGES", 1):
            provider = AsyncMock(side_effect=[extraction("100", "100", 1).model_dump_json(), agents.ProviderError("503")])
            progress = []
            with patch.object(agents, "response", provider):
                with self.assertRaises(agents.ProviderError):
                    await agents.extract(pages, progress.append)
            self.assertEqual(progress[-1]["completed_chunks"], 1)
            provider = AsyncMock(return_value=extraction("50", "50", 2).model_dump_json())
            with patch.object(agents, "response", provider):
                _, facts, _ = await agents.extract(pages, progress.append)
            self.assertEqual(provider.await_count, 1)
            self.assertIn("PÁGINA 2", provider.call_args.args[0][0]["text"])
            self.assertEqual(progress[-1]["cached_chunks"], 1)
            self.assertTrue(next(f for f in facts if f["key"] == "limit")["needs_review"])
            with patch.object(agents, "response", AsyncMock(side_effect=AssertionError("No new call"))):
                await agents.extract(pages)

    async def test_configuration_change_invalidates_cache(self):
        pages = [page(1, "100")]
        provider = AsyncMock(return_value=extraction("100", "100", 1).model_dump_json())
        with patch.object(agents, "response", provider):
            await agents.extract(pages)
            with patch.dict(os.environ, {"GEMINI_MODEL": "different"}):
                await agents.extract(pages)
        self.assertEqual(provider.await_count, 2)

    async def test_non_policy_annex_does_not_reject_full_policy(self):
        with patch.object(agents, "CHUNK_PAGES", 1), patch.object(agents, "response", AsyncMock(side_effect=[
            extraction("100", "100", 1).model_dump_json(),
            Extraction(document_type="other", title="Boleto", facts=[], warnings=[]).model_dump_json()
        ])):
            _, facts, warnings = await agents.extract([page(1, "100"), page(2, "Boleto")])
        self.assertEqual(next(f for f in facts if f["key"] == "limit")["value"], "100")
        self.assertTrue(any("anexo" in w for w in warnings))


class ProviderTests(unittest.IsolatedAsyncioTestCase):
    async def invoke(self, outcomes):
        generate = AsyncMock(side_effect=outcomes)
        client = SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=generate), aclose=AsyncMock()))
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test", "GEMINI_MODEL": "primary", "GEMINI_FALLBACK_MODELS": "backup", "GEMINI_REQUEST_INTERVAL": "0"}), patch.object(agents.genai, "Client", return_value=client), patch.object(agents, "request_lock", asyncio.Lock()), patch.object(agents.asyncio, "sleep", AsyncMock()):
            result = await agents.response([{"type": "input_text", "text": "test"}], "test")
        return result, generate

    def error(self, code):
        error = RuntimeError("provider error")
        error.code = code
        return error

    async def test_transient_failure_retries_and_returns_model(self):
        result, calls = await self.invoke([self.error(503), SimpleNamespace(text="OK")])
        self.assertEqual(result, "OK")
        self.assertEqual(result.model, "primary")
        self.assertEqual(calls.await_count, 2)

    async def test_unavailable_primary_uses_alternative_after_bounded_retries(self):
        result, calls = await self.invoke([self.error(503)] * 3 + [SimpleNamespace(text="OK")])
        self.assertEqual(result.model, "backup")
        self.assertEqual([c.kwargs["model"] for c in calls.call_args_list], ["primary"] * 3 + ["backup"])

    async def test_authentication_and_daily_quota_do_not_switch_models(self):
        for code in [403, 429]:
            generate = AsyncMock(side_effect=self.error(code))
            client = SimpleNamespace(aio=SimpleNamespace(models=SimpleNamespace(generate_content=generate), aclose=AsyncMock()))
            with patch.dict(os.environ, {"GEMINI_API_KEY": "test", "GEMINI_MODEL": "primary", "GEMINI_FALLBACK_MODELS": "backup", "GEMINI_REQUEST_INTERVAL": "0"}), patch.object(agents.genai, "Client", return_value=client), patch.object(agents, "request_lock", asyncio.Lock()), patch.object(agents.asyncio, "sleep", AsyncMock()):
                with self.assertRaises(agents.ProviderError):
                    await agents.response([], "test")
            self.assertEqual(generate.await_count, 1 if code == 403 else 3)
            self.assertTrue(all(c.kwargs["model"] == "primary" for c in generate.call_args_list))


class ApiResumeTests(unittest.TestCase):
    def test_retry_restores_checkpoints_and_exposes_progress(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {"DATA_DIR": directory, "GEMINI_API_KEY": "test"}), patch.object(agents, "CHUNK_PAGES", 1), TestClient(app) as client:
            with pymupdf.open() as doc:
                for text in ["Limit 100", "Limit 50"]:
                    doc.new_page().insert_text((50, 50), text)
                data = doc.tobytes()
            async def finish():
                if tasks:
                    await asyncio.gather(*list(tasks))
            with patch.object(agents, "response", AsyncMock(side_effect=[extraction("100", "Limit 100", 1).model_dump_json(), agents.ProviderError("Unavailable")])):
                response = client.post('/api/upload', files={'file': ('policy.pdf', data, 'application/pdf')})
                client.portal.call(finish)
            item_id = response.json()['id']
            failed = client.get('/api/policies/' + item_id).json()
            self.assertEqual(failed['status'], 'error')
            self.assertEqual(failed['progress']['completed_chunks'], 1)
            provider = AsyncMock(return_value=extraction("50", "Limit 50", 2).model_dump_json())
            with patch.object(agents, 'response', provider):
                self.assertEqual(client.post('/api/policies/' + item_id + '/retry').status_code, 202)
                client.portal.call(finish)
            ready = client.get('/api/policies/' + item_id).json()
            self.assertEqual(ready['status'], 'ready')
            self.assertIsNone(ready['error'])
            self.assertEqual(ready['progress']['cached_chunks'], 1)
            self.assertEqual(provider.await_count, 1)
            with patch.object(agents, 'response', AsyncMock(side_effect=AssertionError('Cache should be reused'))):
                second = client.post('/api/upload', files={'file': ('second.pdf', data, 'application/pdf')})
                client.portal.call(finish)
            comparison = client.post('/api/comparisons', json={'policy_ids': [item_id, second.json()['id']]}).json()
            export = client.get(f"/api/comparisons/{comparison['id']}/export")
            with pymupdf.open(stream=export.content, filetype='pdf') as pdf:
                text = ''.join(p.get_text() for p in pdf)
            self.assertIn('Limit 100', text)
            self.assertIn('Limit 50', text)
            self.assertIn('Conferir versões/condições', text)
            json_export = client.get(f"/api/comparisons/{comparison['id']}/export?format=json").json()
            limit = next(row for row in json_export['rows'] if row['key'] == 'limit')
            self.assertEqual(len(limit['cells'][0]['variants']), 2)
