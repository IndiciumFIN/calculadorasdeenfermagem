"""Synthetic-only CATMAT official API pagination and safety tests."""
import hashlib
import json
import unittest

from packages.cli.parsers.catmat import parse, ParseHold, SOURCE_CONTRACT

SRC = "SRC-SYNTHETIC-CATMAT"
DOC = "DOC-SYNTHETIC-CATMAT"


def fixture():
    return {
        "resultado": [
            {"codigoGrupo": 16, "codigoClasse": 1610, "codigoPdm": 70001,
             "codigoItem": 1111, "descricaoItem": "INTERNAL_SYNTHETIC_DESCRIPTION",
             "statusItem": True, "itemSustentavel": False},
            {"codigoGrupo": 16, "codigoClasse": 1610, "codigoPdm": 70002,
             "codigoItem": 1112, "descricaoItem": "ANOTHER_SYNTHETIC_DESCRIPTION",
             "statusItem": False},
        ],
        "totalRegistros": 2,
        "totalPaginas": 1,
        "paginasRestantes": 0,
    }


def run(v, **opts):
    payload = v if isinstance(v, bytes) else (v.encode("utf-8") if isinstance(v, str)
              else json.dumps(v, separators=(",", ":")).encode("utf-8"))
    return parse(payload, source_id=opts.get("source_id", SRC),
                 document_id=opts.get("document_id", DOC),
                 page=opts.get("page", 1),
                 captured_at=opts.get("captured_at", "2026-11-14T10:00:00-03:00"),
                 expected_sha256=opts.get("expected_sha256", hashlib.sha256(payload).hexdigest()))


class CatmatParserTests(unittest.TestCase):
    def test_metadata_only_provenance(self):
        x = run(fixture())
        self.assertEqual(len(x), 2)
        self.assertEqual(x[0]["catmat_item_code_candidate"], 1111)
        self.assertEqual(x[0]["source_contract"], SOURCE_CONTRACT)
        self.assertTrue(x[0]["status_active_useless_for_clinical_decision"])
        self.assertFalse(x[1]["status_active_useless_for_clinical_decision"])
        for item in x:
            for key in ("source_origin_verified", "catalog_membership_verified",
                        "rights_verified", "clinical_approved", "publication_allowed",
                        "release_allowed"):
                self.assertFalse(item[key], key)
            self.assertEqual(item["status"], "HOLD_HUMAN")
        self.assertNotIn("INTERNAL_SYNTHETIC_DESCRIPTION", str(x))
        self.assertNotIn("ANOTHER_SYNTHETIC_DESCRIPTION", str(x))

    def test_idempotent_and_hash_pinned(self):
        self.assertEqual(run(fixture()), run(fixture()))
        with self.assertRaises(ParseHold):
            run(fixture(), expected_sha256="f" * 64)

    def test_reject_invalid_records_atomically(self):
        bad_fields = [
            ("codigoItem", 0), ("codigoItem", "1111"), ("codigoItem", True),
            ("codigoGrupo", 0), ("codigoClasse", -2), ("codigoPdm", None),
            ("statusItem", "true"), ("statusItem", 1),
            ("descricaoItem", ""), ("descricaoItem", "x\x00y"),
        ]
        for field, value in bad_fields:
            with self.subTest(field=field, value=value):
                x = fixture()
                x["resultado"][1][field] = value
                with self.assertRaises(ParseHold):
                    run(x)
        x = fixture()
        x["resultado"][1]["codigoItem"] = 1111
        with self.assertRaises(ParseHold):
            run(x)

    def test_pagination_rejects_unrelated_or_malformed_pages(self):
        changes = [
            {"totalRegistros": 1},
            {"totalPaginas": 0},
            {"totalPaginas": 2},
            {"paginasRestantes": 1},
            {"totalRegistros": "2"},
            {"resultado": []},
            {"resultado": [{"codigoItem": 1}]},
        ]
        for update in changes:
            with self.subTest(change=update), self.assertRaises(ParseHold):
                run({**fixture(), **update})
        with self.assertRaises(ParseHold):
            run(fixture(), page=2)

    def test_invalid_json_duplicate_keys_and_unsafe_inputs(self):
        examples = [
            '{"resultado":[],"resultado":[]}',
            '{"resultado":NaN}',
            "[]", "{}", "", "{invalid", b"\xff",
            b"\x00", "x" * (5_000_000 + 1),
        ]
        for raw in examples:
            with self.subTest(raw=str(raw)[:40]), self.assertRaises(ParseHold):
                run(raw)

    def test_provenance_and_capture_requirements(self):
        invalid = [
            {"source_id": ""}, {"document_id": ""},
            {"captured_at": "2026-11-14T10:00:00"},
            {"captured_at": "not a date"},
            {"page": -1}, {"page": True}, {"page": 99},
            {"expected_sha256": "INVALID"},
        ]
        for args in invalid:
            with self.subTest(args=args), self.assertRaises(ParseHold):
                run(fixture(), **args)

    def test_output_has_no_claim_authorization(self):
        x = fixture()
        x["resultado"][0].update({"clinical_approved": True,
                                   "publication_allowed": True})
        y = run(x)[0]
        self.assertFalse(y["clinical_approved"])
        self.assertFalse(y["publication_allowed"])


if __name__ == "__main__":
    unittest.main()
