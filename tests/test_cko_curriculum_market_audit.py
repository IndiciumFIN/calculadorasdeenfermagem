"""Negative and baseline tests for CKO curriculum/market audit. Standard library only."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import cko_curriculum_market_audit as audit


REPO = Path(__file__).resolve().parents[1]


class TestCurriculumMarketAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.build_report(REPO, revision="TEST")

    def test_specialty_coverage_uses_actual_catalog(self):
        r = self.report
        self.assertEqual(len(r["specialties"]), r["counts"]["cofen_main"])
        self.assertEqual(sum(x["job_ad_count"] for x in r["specialties"]), r["counts"]["employer_ads_sample"])
        self.assertEqual(
            r["counts"]["cofen_specialties_with_ads"] + r["counts"]["cofen_specialties_with_no_ads_in_sample"],
            r["counts"]["cofen_main"],
        )
        self.assertGreaterEqual(r["counts"]["cofen_main"], 65)

    def test_all_candidates_remain_unapproved(self):
        r = self.report
        self.assertTrue(r["no_clinical_or_legal_approval"])
        self.assertTrue(r["no_database_change_or_publication"])
        self.assertTrue(r["no_global_percent"])
        self.assertTrue(all(x["clinical_approval"] == "NO" for x in r["specialties"]))
        self.assertTrue(all(not x["human_approval"] for x in r["backlog"]))

    def test_missing_market_evidence_never_means_no_demand(self):
        empty = [x for x in self.report["specialties"] if x["job_ad_count"] == 0]
        self.assertTrue(empty)
        self.assertTrue(all(x["job_status"] == "NO_AD_IN_SAMPLE_NOT_NO_DEMAND" for x in empty))

    def test_artifact_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            audit.write_outputs(self.report, folder)
            for name in ("coverage.json", "specialty_matrix.csv", "backlog.jsonl", "status.md", "run_manifest.json"):
                self.assertTrue((folder / name).is_file())
            data = json.loads((folder / "coverage.json").read_text(encoding="utf-8"))
            self.assertTrue(data["no_global_percent"])
            with (folder / "specialty_matrix.csv").open(encoding="utf-8", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), self.report["counts"]["cofen_main"])
            self.assertIn("HOLD_CLINICAL", (folder / "status.md").read_text(encoding="utf-8"))

    def test_duplicate_ids_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            audit.assert_unique([{"id": "a"}, {"id": "a"}], "id", "synthetic")

    def test_invalid_release_gate_fails_closed(self):
        actual = audit.json_file

        def altered(path):
            obj = actual(path)
            if path.name == "EXECUTION_MANIFEST_v1.0.0.json":
                obj["publication_gates"]["clinical"] = True
            return obj

        with mock.patch.object(audit, "json_file", side_effect=altered):
            with self.assertRaisesRegex(ValueError, "Publication gate"):
                audit.build_report(REPO, revision="NEGATIVE_TEST")

    def test_unknown_skill_code_fails_closed(self):
        original = audit.json_lines

        def altered(path):
            items = original(path)
            if path.name == "JOB_DESCRIPTIONS_34_v0.5.7.jsonl":
                items[0]["skill_signals"]["required"].append("UNRECOGNIZED_EXPERIMENTAL_SKILL")
            return items

        with mock.patch.object(audit, "json_lines", side_effect=altered):
            with self.assertRaisesRegex(ValueError, "Unknown skill code"):
                audit.build_report(REPO, revision="NEGATIVE_TEST")

    def test_all_source_hashes_present_and_valid(self):
        v = self.report["input_files_sha256"]
        self.assertGreaterEqual(len(v), 10)
        self.assertTrue(all(len(digest) == 64 for digest in v.values()))
        self.assertTrue(all(all(x in "0123456789abcdef" for x in digest) for digest in v.values()))


if __name__ == "__main__":
    unittest.main()
