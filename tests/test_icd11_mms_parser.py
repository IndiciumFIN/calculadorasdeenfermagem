"""WHO ICD-11 MMS JSON-LD parser tests; fake synthetic entities only."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest

from packages.cli.parsers.icd11 import ParseHold, parse, SOURCE_CONTRACT

SRC = "SRC-SYNTHETIC-WHO-ICD11"
DOC = "DOC-SYNTHETIC-WHO-ICD11"
RELEASE = "2026-01"
PFX = f"http://id.who.int/icd/release/11/{RELEASE}/mms/"


def sample():
    return {
        "@context": "http://id.who.int/icd/contexts/contextForLinearizationEntity.json",
        "@id": PFX + "375810888",
        "parent": [PFX + "1215034670"],
        "code": "MG50.3",
        "source": "http://id.who.int/icd/entity/375810888",
        "classKind": "category",
        "title": {"@language": "en", "@value": "SYNTHETIC_NOT_FOR_PUBLICATION"},
        "definition": {"@language": "en", "@value": "SECRET_DO_NOT_REUSE"},
        "codingNote": {"@language": "en", "@value": "SECRET_CODING_NOTE"},
    }


def run(value, **opts):
    raw = (json.dumps(value, ensure_ascii=False, separators=(",", ":"))
           if not isinstance(value, (str, bytes)) else value)
    payload = raw.encode("utf-8") if isinstance(raw, str) else raw
    return parse(
        payload,
        source_id=opts.get("source_id", SRC),
        document_id=opts.get("document_id", DOC),
        release_id=opts.get("release_id", RELEASE),
        expected_sha256=opts.get("expected_sha256", hashlib.sha256(payload).hexdigest()),
    )


class ICD11CandidateParserTests(unittest.TestCase):
    def test_versioned_uri_and_metadata_only(self):
        out = run(sample())
        self.assertEqual(len(out), 1)
        row = out[0]
        self.assertEqual(row["icd11_code_candidate"], "MG50.3")
        self.assertEqual(row["release_id_declared"], RELEASE)
        self.assertEqual(row["source_contract"], SOURCE_CONTRACT)
        self.assertEqual(row["mms_parent_uri_candidate"], PFX + "1215034670")
        self.assertEqual(row["status"], "HOLD_HUMAN")
        self.assertEqual(row["language"], "en")
        for field in ("source_origin_verified", "reference_membership_verified",
                      "rights_verified", "clinical_approved", "publication_allowed",
                      "release_allowed"):
            self.assertFalse(row[field], field)
        data = str(row)
        for text in ("SECRET_DO_NOT_REUSE", "SYNTHETIC_NOT_FOR_PUBLICATION",
                     "SECRET_CODING_NOTE"):
            self.assertNotIn(text, data)

    def test_deterministic_and_hash_bound(self):
        payload = json.dumps(sample())
        self.assertEqual(run(payload), run(payload))
        self.assertEqual(run(payload.encode()), run(payload))
        with self.assertRaises(ParseHold):
            run(payload, expected_sha256="f" * 64)
        with self.assertRaises(ParseHold):
            run(payload, expected_sha256="INVALID")

    def test_rejects_bad_release_or_wrong_json_ld_source(self):
        changes = [
            {"@context": "https://malicious.example/ctx"},
            {"@id": PFX.replace("2026-01", "2025-01") + "375810888"},
            {"@id": "http://id.who.int/icd/entity/375810888"},
            {"@id": PFX + "375810888/unspecified"},
            {"classKind": "block"},
            {"code": "bad code"},
            {"code": "<script>"},
            {"code": ""},
            {"source": "http://evil.test/entity/375810888"},
            {"source": ""},
            {"parent": []},
            {"parent": [PFX + "1215034670", PFX + "2345"]},
            {"parent": ["http://id.who.int/icd/release/11/2025-01/mms/1215034670"]},
            {"parent": [PFX + "375810888"]},
            {"title": {"@language": "en", "@value": ""}},
            {"title": {"@language": "en", "@value": "ok", "extra": True}},
        ]
        # Extra fields are tolerated, but semantics and required fields aren't.
        for i, change in enumerate(changes[:-1]):
            item = sample()
            item.update(change)
            with self.subTest(i=i), self.assertRaises(ParseHold):
                run(item)

    def test_rejects_missing_or_invalid_metadata(self):
        for field in ("source", "parent", "@id", "code", "title", "@context"):
            obj = sample()
            del obj[field]
            with self.subTest(field=field), self.assertRaises(ParseHold):
                run(obj)
        for opts in ({"release_id": "latest"}, {"release_id": "2026-13"},
                     {"source_id": ""}, {"document_id": ""}):
            with self.subTest(options=opts), self.assertRaises(ParseHold):
                run(sample(), **opts)

    def test_rejects_unsafe_json_and_mixed_batches(self):
        payloads = [
            "", "not json", "[]", "[{}]", "[{}, {}]", "{}",
            '{"@id":"first","@id":"second"}',
            '{"notANumber":NaN}',
            b"\x00",
            b"\xff\xfe",
            "x" * (2_000_000 + 1),
        ]
        for i, value in enumerate(payloads):
            with self.subTest(i=i), self.assertRaises(ParseHold):
                run(value)

    def test_whole_object_is_not_a_clinical_approval(self):
        obj = sample()
        obj.update({"release_allowed": True, "clinical_approved": True,
                    "publication_allowed": True, "rights_verified": True})
        result = run(obj)[0]
        self.assertFalse(result["release_allowed"])
        self.assertFalse(result["publication_allowed"])
        self.assertFalse(result["clinical_approved"])
        self.assertFalse(result["rights_verified"])


if __name__ == "__main__":
    unittest.main()
