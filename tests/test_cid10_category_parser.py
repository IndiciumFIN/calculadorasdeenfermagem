"""Synthetic DATASUS CID-10 V2008 category CSV tests, no official text copied."""
from __future__ import annotations

import hashlib
import unittest
from packages.cli.parsers.cid10 import (
    parse, ParseHold, TABLE_NAME, SOURCE_CONTRACT, HEADER
)

SRC = "SRC-SYNTHETIC-CID10"
DOC = "DOC-SYNTHETIC-CID10"


def row(code="A00", marker="", desc="PRIVATE_DESCRIPTION",
        abbrev="PRIVATE_ABBREV", refer="", excluded=""):
    return ";".join([code, marker, desc, abbrev, refer, excluded, ""]) + "\r\n"


def fixture(*rows):
    return (";".join(HEADER) + "\r\n" + "".join(rows or (
        row("A00"), row("G01", "*")
    ))).encode("cp1252")


def run(blob, **opts):
    if isinstance(blob, str):
        blob = blob.encode("cp1252")
    return parse(
        blob, source_id=opts.get("source_id", SRC),
        document_id=opts.get("document_id", DOC),
        edition=opts.get("edition", "V2008"),
        table_name=opts.get("table_name", TABLE_NAME),
        expected_sha256=opts.get("expected_sha256", hashlib.sha256(blob).hexdigest())
    )


class Cid10CategoryParserTests(unittest.TestCase):
    def test_candidate_only_no_copyrighted_descriptions(self):
        data = run(fixture())
        self.assertEqual(len(data), 2)
        self.assertEqual([x["cid10_category_candidate"] for x in data], ["A00", "G01"])
        self.assertEqual(data[1]["classification_marker_candidate"], "*")
        self.assertEqual(data[0]["source_contract"], SOURCE_CONTRACT)
        self.assertEqual(data[0]["edition_declared"], "V2008")
        self.assertEqual(data[0]["status"], "HOLD_HUMAN")
        for x in data:
            for field in ("source_origin_verified", "edition_membership_verified",
                          "rights_verified", "clinical_approved",
                          "publication_allowed", "release_allowed"):
                self.assertFalse(x[field])
        self.assertNotIn("PRIVATE_DESCRIPTION", str(data))
        self.assertNotIn("PRIVATE_ABBREV", str(data))

    def test_same_data_produces_same_hashes(self):
        payload = fixture()
        self.assertEqual(run(payload), run(payload))
        self.assertEqual(run(payload.decode("cp1252")), run(payload))
        with self.assertRaises(ParseHold):
            run(payload, expected_sha256="0" * 64)

    def test_invalid_and_duplicate_code_atomic_hold(self):
        inputs = [
            row("A0"), row("A000"), row("X0Z"), row("a00"),
            row("00A"), row("A00", marker="unknown"),
            row("A00", desc=""), row("A00", abbrev=""),
            row("A00") + row("A00"),
            row("A00") + row("G01") + row("G01"),
            row("A00") + "bad;short\r\n",
            row("A00").removesuffix("\r\n") + ";unexpected\r\n",
        ]
        for i, payload in enumerate(inputs):
            with self.subTest(i=i), self.assertRaises(ParseHold):
                run(fixture(payload))

    def test_wrong_table_edition_and_provenance_rejected(self):
        for opt in (
            {"edition": "latest"}, {"edition": "V2019"},
            {"table_name": "CID-10-SUBCATEGORIAS.CSV"},
            {"table_name": "../CID-10-CATEGORIAS.CSV"},
            {"source_id": ""}, {"document_id": ""},
            {"expected_sha256": "BAD"},
        ):
            with self.subTest(opt=opt), self.assertRaises(ParseHold):
                run(fixture(), **opt)

    def test_header_corruption_and_empty_source_rejected(self):
        samples = [
            b"", b"\x00", b"not a CSV",
            fixture().replace(b"CAT;CLASSIF", b"SUBCAT;CLASSIF"),
            (";".join(HEADER) + "\r\n").encode("cp1252"),
        ]
        for i, raw in enumerate(samples):
            with self.subTest(i=i), self.assertRaises(ParseHold):
                run(raw)

    def test_untrusted_payload_cannot_self_approve(self):
        src = row("A00", desc="publication_allowed=true",
                  abbrev="clinical_approved=true")
        item = run(fixture(src))[0]
        self.assertFalse(item["publication_allowed"])
        self.assertFalse(item["clinical_approved"])


if __name__ == "__main__":
    unittest.main()
