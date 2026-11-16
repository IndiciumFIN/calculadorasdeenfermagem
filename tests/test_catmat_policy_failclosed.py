"""CATMAT contract & policy cannot self-approve source metadata."""
import json
import unittest
from pathlib import Path
from packages.cli.parsers import catmat

ROOT = Path(__file__).resolve().parents[1]


class CatmatPolicyTests(unittest.TestCase):
    def test_contract_parser_policy_linkage(self):
        source = json.loads((ROOT/"contracts/fontes/catmat.json").read_text())
        policy = json.loads((ROOT/"contracts/policies/KERNEL-POLICY-013.json").read_text())
        self.assertEqual(source["parser"], "packages/cli/parsers/catmat.py")
        self.assertEqual(source["parser_version"], catmat.PARSER_API_VERSION)
        self.assertEqual(source["source_contract"], catmat.SOURCE_CONTRACT)
        self.assertEqual(source["kernel_policy_id"], policy["id"])
        self.assertEqual(policy["source_contract"], catmat.SOURCE_CONTRACT)

    def test_rights_and_release_holds_are_mandatory(self):
        policy = json.loads((ROOT/"contracts/policies/KERNEL-POLICY-013.json").read_text())
        for k in ("sha256_required", "fail_closed", "wo_required", "requires_human_review"):
            self.assertIs(policy[k], True, k)
        self.assertFalse(policy["publication_allowed"])
        self.assertFalse(policy["rights_by_operation_approved"])
        self.assertTrue(policy["review_policy"]["approval_required"])
        self.assertIn("METADATA_ONLY", policy["processing_scope"])

    def test_registry_stubs_remain_blocked(self):
        from packages.cli.kernel.core import Kernel, VALIDATOR_HOLDS
        k = Kernel()
        self.assertEqual(VALIDATOR_HOLDS.get("catmat_validator"), "SELF_TEST_FAILED")
        self.assertEqual(VALIDATOR_HOLDS.get("schema_validator"), "SELF_TEST_FAILED")
        self.assertEqual(k.gate("KERNEL-POLICY-013"), 2)


if __name__ == "__main__":
    unittest.main()
