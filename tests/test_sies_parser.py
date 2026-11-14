"""Synthetic SIES ZIP/CSV lineage and malicious-archive tests."""
import hashlib
import io
import zipfile
import unittest

from packages.cli.parsers.sies import parse, ParseHold, SOURCE_CONTRACT

HEAD = ("TX_SIGLA;IBGE;TX_INSUMO;ANO;MES;QTDE;ORIGEM;TX_AREA\n")
GOOD = "SP;3550308;SECRET_SUPPLY;2026;11;123;SECRET_ORIGIN;SECRET_AREA\n"
SRC = "SRC-SYNTHETIC-SIES"
DOC = "DOC-SYNTHETIC-SIES"


def fixture(*rows):
    return (HEAD + "".join(rows or (GOOD,))).encode("utf-8")


def zipup(*members):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in members:
            z.writestr(name, data)
    return buf.getvalue()


def run(raw, **opt):
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    return parse(raw,
                 source_id=opt.get("source_id", SRC),
                 document_id=opt.get("document_id", DOC),
                 snapshot_date=opt.get("snapshot_date", "2026-11-13"),
                 expected_sha256=opt.get("expected_sha256", hashlib.sha256(raw).hexdigest()),
                 delimiter=opt.get("delimiter", ";"))


class SiesParserTests(unittest.TestCase):
    def test_provenance_and_no_source_text_or_release(self):
        out = run(fixture())[0]
        self.assertEqual(out["source_contract"], SOURCE_CONTRACT)
        self.assertEqual(out["period_candidate"], "2026-11")
        self.assertEqual(out["ibge_municipio_candidate"], "3550308")
        self.assertEqual(out["quantity_string_candidate"], "123")
        self.assertEqual(out["status"], "HOLD_HUMAN")
        for f in ("source_origin_verified", "rights_verified",
                  "clinical_approved", "publication_allowed", "release_allowed"):
            self.assertFalse(out[f])
        for value in ("SECRET_SUPPLY", "SECRET_ORIGIN", "SECRET_AREA"):
            self.assertNotIn(value, str(out))

    def test_pinned_zip_and_csv_same_candidate_contents(self):
        csv_data = fixture()
        archive = zipup(("sies.csv", csv_data))
        direct = run(csv_data)[0]
        zipped = run(archive)[0]
        self.assertEqual(direct["record_sha256"], zipped["record_sha256"])
        self.assertNotEqual(direct["source_sha256"], zipped["source_sha256"])
        self.assertEqual(zipped["csv_member_sha256"], hashlib.sha256(csv_data).hexdigest())

    def test_duplicate_source_rows_have_provenance_indices(self):
        out = run(fixture(GOOD, GOOD))
        self.assertEqual(len(out), 2)
        self.assertEqual([x["source_occurrence_index"] for x in out], [1, 2])

    def test_rejects_bad_records_atomically(self):
        bad = [
            "SP;3550308;X;2026;13;5;SRC;VACCINE\n",
            "SP;3550308;X;1999;11;5;SRC;VACCINE\n",
            "SP;BAD_IBGE;X;2026;11;5;SRC;VACCINE\n",
            "SP;3550308;X;2026;11;-3;SRC;VACCINE\n",
            "SP;3550308;X;2026;11;NaN;SRC;VACCINE\n",
            "SP;3550308;;2026;11;5;SRC;VACCINE\n",
            "SP;3550308;X;2026;11;5;SRC\n",
        ]
        for i, line in enumerate(bad):
            with self.subTest(i=i), self.assertRaises(ParseHold):
                run(fixture(GOOD, line))

    def test_rejects_invalid_zip_members(self):
        examples = [
            zipup(("../escape.csv", fixture())),
            zipup(("folder/member.csv", fixture())),
            zipup(("readme.txt", b"x")),
            zipup(("same.csv", fixture()), ("same.csv", fixture())),
            b"PKnot-really-a-zip",
        ]
        for i, value in enumerate(examples):
            with self.subTest(i=i), self.assertRaises(ParseHold):
                run(value)

    def test_provenance_hash_and_date_are_mandatory(self):
        for kwargs in (
            {"source_id": ""}, {"document_id": ""}, {"snapshot_date": "2026-19-01"},
            {"snapshot_date": "2026-02-30"}, {"snapshot_date": "latest"},
            {"expected_sha256": "bad"}, {"expected_sha256": "f" * 64},
            {"delimiter": "|"},
        ):
            with self.subTest(kwargs=kwargs), self.assertRaises(ParseHold):
                run(fixture(), **kwargs)

    def test_invalid_header_and_binary_rejected(self):
        for data in (b"", b"\x00", b"\xff", b"OTHER;IBGE\nvalue;value\n",
                     HEAD.encode("utf-8")):
            with self.subTest(data=data[:12]), self.assertRaises(ParseHold):
                run(data)

    def test_no_submitted_approval_can_escape_hold(self):
        line = "SP;3550308;X;2026;11;5;clinical_approved=True;VACCINE\n"
        row = run(fixture(line))[0]
        self.assertFalse(row["clinical_approved"])
        self.assertFalse(row["publication_allowed"])


if __name__ == "__main__":
    unittest.main()
