"""PNI 2026 privacy-first source / policy / Kernel evidence checks."""
import json
import unittest
from pathlib import Path

from packages.cli.parsers import pni

ROOT = Path(__file__).resolve().parents[1]


class PniPrivacyPolicyTests(unittest.TestCase):
    def test_source_parser_policy_links(self):
        source = json.loads((ROOT / "contracts/fontes/pni.json").read_text())
        policy = json.loads((ROOT / "contracts/policies/KERNEL-POLICY-012.json").read_text())
        self.assertEqual(source["parser"], "packages/cli/parsers/pni.py")
        self.assertEqual(source["source_contract"], pni.SOURCE_CONTRACT)
        self.assertEqual(source["parser_version"], pni.PARSER_API_VERSION)
        self.assertEqual(source["kernel_policy_id"], policy["id"])
        self.assertEqual(source["validators"], policy["validators"])

    def test_privacy_and_rights_are_explicit_holds(self):
        policy = json.loads((ROOT / "contracts/policies/KERNEL-POLICY-012.json").read_text())
        for field in ("sha256_required", "fail_closed",
                      "requires_human_review", "wo_required"):
            self.assertTrue(policy[field])
        self.assertFalse(policy["publication_allowed"])
        self.assertFalse(policy["rights_by_operation_approved"])
        self.assertIn("AGGREGATES_ONLY", policy["processing_scope"])
        privacy = policy["privacy_controls"]
        self.assertFalse(privacy["row_level_export_allowed"])
        self.assertFalse(privacy["patient_pseudonym_export_allowed"])
        self.assertTrue(privacy["reidentification_risk_review_required"])
        self.assertTrue(privacy["lgpd_review_required"])
        self.assertEqual(privacy["min_aggregate_records"], 10)

    def test_unimplemented_schema_validator_and_clinical_release_hold(self):
        from packages.cli.kernel.core import Kernel, VALIDATOR_HOLDS
        kernel = Kernel()
        self.assertEqual(VALIDATOR_HOLDS.get("schema_validator"), "SELF_TEST_FAILED")
        self.assertEqual(kernel.gate("KERNEL-POLICY-012"), 2)


if __name__ == "__main__":
    unittest.main()
