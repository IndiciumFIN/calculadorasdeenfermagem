"""CDC CVX.txt parser tests: synthetic data only, no copied source rows."""
from __future__ import annotations

import hashlib
import unittest

from packages.cli.parsers.vacinas import parse, ParseHold, SOURCE_CONTRACT, SOURCE_URI

SRC = "SRC-SYNTHETIC-CDC-CVX"
DOC = "DOC-SYNTHETIC-CDC-CVX-001"
RELEASE = "2026-09-18"


def record(code="01", *, status="Active", nonvaccine="False",
           updated="2026/09/18", short="synthetic", full="synthetic vaccine",
           notes="DO_NOT_EXPORT_PRIVATE_NOTE"):
    return f"{code:<10}|{short}|{full}|{notes}|{status}|{nonvaccine}|{updated}\n"


def run(payload, **kw):
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    return parse(payload,
                 source_id=kw.get("source_id", SRC),
                 document_id=kw.get("document_id", DOC),
                 release_date=kw.get("release_date", RELEASE),
                 expected_sha256=kw.get("expected_sha256", hashlib.sha256(payload).hexdigest()))


class CVXParserTests(unittest.TestCase):
    def test_metadata_only_and_holds(self):
        obj = run(record())[0]
        self.assertEqual(obj["cvx_code_candidate"], "01")
        self.assertEqual(obj["status_us_candidate"], "Active")
        self.assertFalse(obj["is_nonvaccine_candidate"])
        self.assertEqual(obj["last_updated_us"], "2026-09-18")
        self.assertEqual(obj["source_contract"], SOURCE_CONTRACT)
        self.assertEqual(obj["official_source_uri"], SOURCE_URI)
        for key in ("clinical_approved", "release_allowed", "publication_allowed",
                    "origin_and_rights_verified"):
            self.assertIs(obj[key], False)
        self.assertEqual(obj["status"], "HOLD_HUMAN")
        self.assertNotIn("DO_NOT_EXPORT_PRIVATE_NOTE", str(obj))
        self.assertNotIn("synthetic vaccine", str(obj))

    def test_preserves_leading_zeros_and_usspecific_status(self):
        rows = run(record("998", status="Inactive", nonvaccine="True")
                   + record("01", status="Non-US"))
        self.assertEqual([r["cvx_code_candidate"] for r in rows], ["01", "998"])
        self.assertTrue(rows[1]["is_nonvaccine_candidate"])
        self.assertEqual(rows[0]["status_us_candidate"], "Non-US")

    def test_deterministic_hashes_and_byte_proof(self):
        payload = record("01") + record("143")
        self.assertEqual(run(payload), run(payload))
        self.assertEqual(run(payload.encode("utf-8")), run(payload))
        self.assertEqual(len(run(payload)[0]["record_sha256"]), 64)
        with self.assertRaises(ParseHold):
            run(payload, expected_sha256="0" * 64)

    def test_atomic_batch_rejects_duplicates_and_malformed_records(self):
        invalid = [
            record("01") + record("01"),
            record("01") + "broken row\n",
            record("abc"),
            record("01", status="Not-CDC"),
            record("01", nonvaccine="maybe"),
            record("01", updated="2026/09/19"),
            record("01", updated="2026/02/30"),
            record("01", short=""),
            record("01", full=""),
            record("01", notes="|extra"),
            record("01") + "\n",
            record("01", status="active"),
        ]
        for index, payload in enumerate(invalid):
            with self.subTest(index=index), self.assertRaises(ParseHold):
                run(payload)

    def test_source_metadata_and_manifest_required(self):
        payload = record("01")
        cases = [
            {"source_id": ""}, {"document_id": ""},
            {"release_date": "bad"}, {"release_date": "2026-09-17"},
            {"expected_sha256": "BAD"}, {"expected_sha256": "f" * 64},
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(ParseHold):
                run(payload, **kwargs)

    def test_unsafe_payloads_and_types_rejected(self):
        with self.assertRaises(ParseHold):
            run(b"\xff")
        with self.assertRaises(ParseHold):
            run(record("01").encode("utf-8") + bytes([0]))
        with self.assertRaises(ParseHold):
            run(b"")
        with self.assertRaises(ParseHold):
            run("x" * (16_000_000 + 1))
        with self.assertRaises(ParseHold):
            parse([], source_id=SRC, document_id=DOC, release_date=RELEASE,
                  expected_sha256="0" * 64)

    def test_utf8_bom_supported_for_official_flat_file(self):
        content = b"\xef\xbb\xbf" + record("143").encode("utf-8")
        rows = run(content)
        self.assertEqual(rows[0]["cvx_code_candidate"], "143")


if __name__ == "__main__":
    unittest.main()
