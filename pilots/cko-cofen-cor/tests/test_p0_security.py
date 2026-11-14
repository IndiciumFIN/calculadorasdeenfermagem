"""Synthetic negative tests for P0 pilot; never fetch sources or access production."""
import argparse
import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "automatizacao"))
import cko_pilot
import cko_gates
import cko_schema


class PilotP0Tests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.directory.name)
        self.doc = self.root / "dados" / "SYNTHETIC-ACT"
        self.doc.mkdir(parents=True)

    def tearDown(self):
        self.directory.cleanup()

    def acquisition(self, headers=None, url="https://example.org/act/1"):
        source = {"http_headers": headers if headers is not None else {"Content-Type": "application/pdf"},
                  "official_primary_url": url, "http_final_url": url}
        (self.doc / "acquisition.json").write_text(json.dumps(source), encoding="utf-8")

    def test_run_halts_on_every_nonzero_stage(self):
        functions = ["cmd_fetch", "cmd_extract", "cmd_segment", "cmd_plan", "cmd_register", "cmd_validate", "cmd_gate"]
        for i, failed in enumerate(functions):
            called = []
            saved = {k: getattr(cko_pilot, k) for k in functions}
            try:
                for j, name in enumerate(functions):
                    setattr(cko_pilot, name, lambda args, index=j: called.append(index) or (2 if index == i else 0))
                self.assertEqual(cko_pilot.cmd_run(argparse.Namespace()), 2)
                self.assertEqual(called, list(range(i + 1)))
            finally:
                for name, fn in saved.items():
                    setattr(cko_pilot, name, fn)

    def test_run_all_zero_exits_zero(self):
        steps = ["cmd_fetch", "cmd_extract", "cmd_segment", "cmd_plan", "cmd_register", "cmd_validate", "cmd_gate"]
        with patch.multiple(cko_pilot, **{name: lambda args: 0 for name in steps}):
            self.assertEqual(cko_pilot.cmd_run(argparse.Namespace()), 0)

    def test_http_header_whitelist_typed_only(self):
        given = {"Content-Type": "application/pdf", "Content-Length": "2000", "Last-Modified": "Mon, 01 Jun 2020 00:00:00 GMT",
                 "Set-Cookie": "synthetic=SECRET", "ETag": '"opaque-id"', "Authorization": "Bearer SYNTHETIC"}
        kept = cko_pilot._safe_http_headers(given)
        self.assertEqual(set(kept), {"Content-Type", "Content-Length", "Last-Modified"})

    def test_http_header_disallows_synthetic_secret_in_allowed_field(self):
        for value in ["application/pdf; session=SYNTHETIC", "application/pdf\r\nSet-Cookie: x", "application/pdf; Bearer SYNTHETIC"]:
            self.assertEqual(cko_pilot._safe_http_headers({"Content-Type": value}), {})
        self.assertEqual(cko_pilot._safe_http_headers({"Content-Length": "123;token=x"}), {})

    def test_gate_g15_allows_only_safe_metadata(self):
        self.acquisition()
        self.assertEqual(cko_gates.g_no_session_credentials_in_acquisition(self.root), [])

    def test_gate_g15_rejects_cookie_name(self):
        self.acquisition({"Set-Cookie": "synthetic=value"})
        self.assertTrue(cko_gates.g_no_session_credentials_in_acquisition(self.root))

    def test_gate_g15_rejects_header_value_masquerade(self):
        self.acquisition({"Content-Type": "text/html; token=synthetic"})
        self.assertTrue(cko_gates.g_no_session_credentials_in_acquisition(self.root))

    def test_gate_g15_rejects_raw_etag(self):
        self.acquisition({"ETag": '"opaque-id"'})
        self.assertTrue(cko_gates.g_no_session_credentials_in_acquisition(self.root))

    def test_gate_g15_rejects_url_access_token(self):
        self.acquisition(url="https://example.org/source?access_token=SYNTHETIC")
        self.assertTrue(cko_gates.g_no_session_credentials_in_acquisition(self.root))

    def test_gate_g15_rejects_url_userinfo(self):
        self.acquisition(url="https://demo:SYNTHETIC@example.org/source")
        self.assertTrue(cko_gates.g_no_session_credentials_in_acquisition(self.root))

    def test_gate_g15_rejects_non_https_url(self):
        self.acquisition(url="http://example.org/source")
        self.assertTrue(cko_gates.g_no_session_credentials_in_acquisition(self.root))

    def test_gate_g15_rejects_non_dict_headers(self):
        self.acquisition()
        record = {"http_headers": ["Content-Type"]}
        (self.doc / "acquisition.json").write_text(json.dumps(record), encoding="utf-8")
        self.assertTrue(cko_gates.g_no_session_credentials_in_acquisition(self.root))

    def test_gate_g15_requires_records(self):
        self.assertTrue(cko_gates.g_no_session_credentials_in_acquisition(self.root))

    def test_candidate_claim_schema_rejects_promotion(self):
        schema = json.loads((ROOT / "modelos" / "contratos" / "clinical_claim_candidate.schema.json").read_text())
        claim = {"claim_id": "CLM-SYN-0001", "source_evidence_atom_ids": ["EV-SYN"], "assertion_paraphrase": "Synthetic educational text", "population": "", "setting": "", "scope": "", "exceptions": [], "negations": [], "status": "CANDIDATE", "clinical_reviewer_receipt_id": None, "rights_id": "HOLD_SYNTHETIC", "clinical_release_allowed": False}
        self.assertFalse(cko_schema.validate(claim, schema))
        for change in [{"clinical_release_allowed": True}, {"clinical_reviewer_receipt_id": "FAKE"}, {"status": "APPROVED"}, {"claim_id": "CK-CLAIM-SILENT-RENAME"}, {"source_evidence_atom_ids": []}, {"unrecognized_field": "x"}]:
            self.assertTrue(cko_schema.validate({**claim, **change}, schema), msg=str(change))

    def test_missing_claim_schema_fails_closed(self):
        schemas_dir = self.root / "modelos" / "contratos"
        schemas_dir.mkdir(parents=True)
        for name in ["evidence_atom_candidate", "norm_atom_candidate", "relation_candidate"]:
            (schemas_dir / f"{name}.schema.json").write_text('{"type":"object"}', encoding="utf-8")
        rc = cko_pilot.cmd_validate(argparse.Namespace(root=str(self.root)))
        report = json.loads((self.root / "gates" / "validation_report.json").read_text())
        self.assertNotEqual(rc, 0)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("clinical_claim_candidate" in item for item in report["issues"]))
        self.assertFalse(report["publication_allowed"])

    def test_nonclinical_release_is_not_approved(self):
        schema = json.loads((ROOT / "modelos" / "contratos" / "clinical_claim_candidate.schema.json").read_text())
        self.assertEqual(schema["properties"]["clinical_release_allowed"]["const"], False)
        self.assertEqual(schema["properties"]["clinical_reviewer_receipt_id"]["type"], "null")


if __name__ == "__main__":
    unittest.main()
