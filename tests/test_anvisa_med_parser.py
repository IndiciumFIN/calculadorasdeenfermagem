"""Anvisa medicines CSV parser, synthetic specimens only."""
import hashlib
import unittest

from packages.cli.parsers.anvisa_med import ParseHold, SOURCE_CONTRACT, HEADER, parse

SRC = "SRC-SYNTHETIC-ANVISA"
DOC = "DOC-SYNTHETIC-ANVISA"


def fields(reg="012345678", process="25351.123456/2020-11", name="SYNTHETIC"):
    return [
        "MEDICAMENTO", name, "01/01/2020", "GENÉRICO",
        reg, "112030", process, "CLASS_SECRET",
        "00000000000000 - CORP_SECRET", "VALIDO", "ACTIVE_SECRET",
    ]


def dataset(*records, header=None):
    header = list(HEADER) if header is None else header
    lines = [";".join(header)]
    for r in records:
        lines.append(";".join(r))
    return ("\r\n".join(lines) + "\r\n").encode("cp1252")


def run(raw, **override):
    if isinstance(raw, str):
        raw = raw.encode("cp1252")
    return parse(raw, source_id=override.get("source_id", SRC),
                 document_id=override.get("document_id", DOC),
                 snapshot_month=override.get("snapshot_month", "2026-11"),
                 expected_sha256=override.get("expected_sha256", hashlib.sha256(raw).hexdigest()))


class AnvisaMedicineCSVTests(unittest.TestCase):
    def test_metadata_only_with_leading_zero_registration(self):
        output = run(dataset(fields()))
        self.assertEqual(len(output), 1)
        item = output[0]
        self.assertEqual(item["registration_number_candidate"], "012345678")
        self.assertEqual(item["process_number_candidate"], "25351.123456/2020-11")
        self.assertEqual(item["source_contract"], SOURCE_CONTRACT)
        self.assertEqual(item["status"], "HOLD_HUMAN")
        for flag in ("source_origin_verified", "record_registration_current_verified",
                     "rights_verified", "clinical_approved", "publication_allowed",
                     "release_allowed"):
            self.assertFalse(item[flag])
        txt = str(output)
        for hidden in ("SYNTHETIC", "CLASS_SECRET", "CORP_SECRET", "ACTIVE_SECRET"):
            self.assertNotIn(hidden, txt)

    def test_exact_duplicates_are_preserved_and_numbered(self):
        data = dataset(fields(), fields())
        out = run(data)
        self.assertEqual(len(out), 2)
        self.assertEqual([x["occurrence_index"] for x in out], [1, 2])
        self.assertNotEqual(out[0]["record_sha256"], out[1]["record_sha256"])

    def test_null_registration_can_be_retained_as_candidate(self):
        value = fields(reg="")
        out = run(dataset(value))[0]
        self.assertIsNone(out["registration_number_candidate"])
        self.assertFalse(out["record_registration_current_verified"])

    def test_digest_and_snapshot_rejected(self):
        data = dataset(fields())
        for kwargs in ({"expected_sha256": "0" * 64}, {"expected_sha256": "bad"},
                       {"snapshot_month": "latest"}, {"snapshot_month": "2026-13"},
                       {"source_id": ""}, {"document_id": ""}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ParseHold):
                run(data, **kwargs)

    def test_bad_columns_and_rows_rejected(self):
        records = [
            fields(reg="bad"),
            fields(process="BAD"),
            fields(name=""),
            ["OTHER"] + fields()[1:],
            fields()[:-1],
            fields() + ["EXTRA"],
        ]
        for index, record in enumerate(records):
            with self.subTest(i=index), self.assertRaises(ParseHold):
                run(dataset(record))
        with self.assertRaises(ParseHold):
            run(dataset(fields(), header=list(HEADER)[::-1]))
        with self.assertRaises(ParseHold):
            run(dataset(fields(), header=list(HEADER)[:-1]))

    def test_invalid_encoding_binary_and_empty_rejected(self):
        for raw in (b"", b"\x00", b"\x81", b"invalid", b";;\r\n"):
            with self.subTest(raw=raw), self.assertRaises(ParseHold):
                run(raw)
        with self.assertRaises(ParseHold):
            run(dataset())

    def test_duplicate_header_and_no_fake_approval(self):
        h = list(HEADER)
        h[-1] = h[0]
        with self.assertRaises(ParseHold):
            run(dataset(fields(), header=h))
        row = fields()
        row[-1] = "clinical_approved=True"  # Source text must never be trusted
        output = run(dataset(row))
        self.assertFalse(output[0]["clinical_approved"])


if __name__ == "__main__":
    unittest.main()
