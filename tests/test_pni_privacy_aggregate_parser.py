"""Synthetic-only PNI 60-column vaccination CSV tests; never use patient records."""
from __future__ import annotations

import csv
import hashlib
import io
import zipfile
import unittest

from packages.cli.parsers.pni import (
    DICTIONARY_FIELDS, MIN_CELL_RECORDS, ParseHold, SOURCE_CONTRACT, parse,
)

SOURCE_ID = "SYNTHETIC-PNI-2026-10"
DOCUMENT_ID = "SYNTHETIC-PNI-MANIFEST"


def sample_row(index: int, *, uf="SP", vaccine="77", month="2026-10"):
    row = dict.fromkeys(DICTIONARY_FIELDS, "")
    row["co_documento"] = f"DOCUMENT-SECRET-{index:06d}"
    row["co_paciente"] = f"PATIENT-SECRET-{index:06d}"
    row["no_municipio_paciente"] = "CITY-SECRET"
    row["co_vacina"] = vaccine
    row["dt_vacina"] = month + "-12"
    row["sg_uf_estabelecimento"] = uf
    row["co_lote_vacina"] = "SECRET-LOT"
    return row


def csv_snapshot(rows, *, fields=DICTIONARY_FIELDS):
    buf = io.StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fields, delimiter=";", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in fields})
    return buf.getvalue().encode("utf-8")


def zip_snapshot(name: str, data: bytes):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(name, data)
    return buf.getvalue()


def run(data, **overrides):
    return parse(
        data,
        source_id=overrides.get("source_id", SOURCE_ID),
        document_id=overrides.get("document_id", DOCUMENT_ID),
        snapshot_month=overrides.get("snapshot_month", "2026-10"),
        expected_sha256=overrides.get("expected_sha256", hashlib.sha256(data).hexdigest()),
        encoding=overrides.get("encoding", "utf-8-sig"),
        delimiter=overrides.get("delimiter", ";"),
    )


class PniPrivacyParserTests(unittest.TestCase):
    def test_dictionary_has_exact_60_unique_fields(self):
        self.assertEqual(len(DICTIONARY_FIELDS), 60)
        self.assertEqual(len(set(DICTIONARY_FIELDS)), 60)
        self.assertIn("co_paciente", DICTIONARY_FIELDS)
        self.assertIn("co_documento", DICTIONARY_FIELDS)

    def test_only_large_aggregates_and_no_patient_export(self):
        rows = [sample_row(i) for i in range(13)]
        rows.extend(sample_row(i + 13, uf="RJ", vaccine="88") for i in range(4))
        result = run(csv_snapshot(rows))
        self.assertEqual(len(result), 1)
        cell = result[0]
        self.assertEqual(cell["dose_records"], 13)
        self.assertEqual(cell["co_vacina_candidate"], "77")
        self.assertEqual(cell["uf_estabelecimento"], "SP")
        self.assertEqual(cell["suppression_threshold"], MIN_CELL_RECORDS)
        self.assertEqual(cell["source_contract"], SOURCE_CONTRACT)
        self.assertEqual(cell["status"], "HOLD_HUMAN")
        self.assertTrue(cell["no_row_level_output"])
        for field in ("data_privacy_release_reviewed", "source_origin_verified",
                      "rights_verified", "clinical_approved",
                      "publication_allowed", "release_allowed"):
            self.assertFalse(cell[field])
        output = str(result)
        for secret in ("PATIENT-SECRET", "DOCUMENT-SECRET", "CITY-SECRET",
                       "SECRET-LOT", "'RJ'", "'88'"):
            self.assertNotIn(secret, output)

    def test_all_small_cells_are_suppressed(self):
        self.assertEqual(run(csv_snapshot([sample_row(i) for i in range(9)])), [])

    def test_exactly_ten_documents_passes_technical_threshold(self):
        x = run(csv_snapshot([sample_row(i) for i in range(10)]))
        self.assertEqual(x[0]["dose_records"], 10)
        self.assertFalse(x[0]["clinical_approved"])

    def test_zip_metadata_and_csv_are_equivalent(self):
        data = csv_snapshot([sample_row(i) for i in range(12)])
        packed = zip_snapshot("PNI_2026_10.csv", data)
        from_csv, from_zip = run(data)[0], run(packed)[0]
        self.assertEqual(from_csv["dose_records"], from_zip["dose_records"])
        self.assertEqual(from_csv["record_sha256"], from_zip["record_sha256"])
        self.assertNotEqual(from_csv["source_sha256"], from_zip["source_sha256"])

    def test_declared_cp1252_text_is_hash_pinned_without_patient_export(self):
        rows = [sample_row(i) for i in range(12)]
        rows[0]["ds_vacina"] = "vacinação sintética"
        raw = csv_snapshot(rows).decode("utf-8").encode("cp1252")
        decoded = raw.decode("cp1252")
        expected = hashlib.sha256(raw).hexdigest()
        records = parse(decoded, source_id=SOURCE_ID, document_id=DOCUMENT_ID,
                        snapshot_month="2026-10", expected_sha256=expected,
                        encoding="cp1252")
        self.assertEqual(records[0]["dose_records"], 12)
        self.assertFalse(records[0]["publication_allowed"])
        self.assertNotIn("vacinação", str(records))

    def test_repeated_document_is_rejected_even_if_aggregate_large(self):
        rows = [sample_row(i) for i in range(12)]
        rows[11]["co_documento"] = rows[1]["co_documento"]
        with self.assertRaises(ParseHold):
            run(csv_snapshot(rows))

    def test_bad_snapshot_month_or_manifest_rejected(self):
        data = csv_snapshot([sample_row(i) for i in range(10)])
        for opts in (
            {"expected_sha256": "0" * 64}, {"expected_sha256": "bad"},
            {"snapshot_month": "2026-13"}, {"snapshot_month": "latest"},
            {"source_id": ""}, {"document_id": ""},
            {"encoding": "utf-16"}, {"delimiter": "|"},
        ):
            with self.subTest(opts=opts), self.assertRaises(ParseHold):
                run(data, **opts)

    def test_input_rows_outside_snapshot_rejected(self):
        rows = [sample_row(i) for i in range(12)]
        rows[-1]["dt_vacina"] = "2026-09-12"
        with self.assertRaises(ParseHold):
            run(csv_snapshot(rows))
        rows[-1]["dt_vacina"] = "2026-02-30"
        with self.assertRaises(ParseHold):
            run(csv_snapshot(rows))

    def test_invalid_code_uf_and_header_rejected(self):
        rows = [sample_row(i) for i in range(12)]
        for field, bad in (("co_vacina", "DATA-LEAK"), ("co_vacina", ""),
                           ("sg_uf_estabelecimento", "SÃO"),
                           ("sg_uf_estabelecimento", "")):
            cloned = [dict(row) for row in rows]
            cloned[-1][field] = bad
            with self.subTest(field=field, bad=bad), self.assertRaises(ParseHold):
                run(csv_snapshot(cloned))
        with self.assertRaises(ParseHold):
            run(csv_snapshot(rows, fields=DICTIONARY_FIELDS[:-1]))

    def test_bad_csv_zip_traversal_and_multiple_members_rejected(self):
        data = csv_snapshot([sample_row(i) for i in range(12)])
        bad = (
            b"", b"\xff", b"PKbad", b"\x00", b"not-csv",
            zip_snapshot("../escape.csv", data),
            zip_snapshot("nested/pni.csv", data),
            zip_snapshot("notcsv.txt", data),
        )
        for payload in bad:
            with self.subTest(payload=payload[:15]), self.assertRaises(ParseHold):
                run(payload)
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("a.csv", data)
            z.writestr("b.csv", data)
        with self.assertRaises(ParseHold):
            run(archive.getvalue())

    def test_no_fake_approval_from_source_columns(self):
        rows = [sample_row(i) for i in range(12)]
        rows[-1]["ds_vacina"] = "publication_allowed=True; clinical_approved=True"
        x = run(csv_snapshot(rows))[0]
        self.assertFalse(x["clinical_approved"])
        self.assertFalse(x["publication_allowed"])


if __name__ == "__main__":
    unittest.main()
