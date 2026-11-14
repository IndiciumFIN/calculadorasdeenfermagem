"""ICD-11 source-bound policy and stub fail-closed checks."""
import json
import unittest
from pathlib import Path

from packages.cli.parsers import icd11

ROOT = Path(__file__).resolve().parents[1]


class ICD11PolicyTests(unittest.TestCase):
    def test_contract_versioned_parser_and_policy(self):
        source = json.loads((ROOT / "contracts/fontes/cid11.json").read_text())
        policy = json.loads((ROOT / "contracts/policies/KERNEL-POLICY-004.json").read_text())
        self.assertEqual(source["source_contract"], icd11.SOURCE_CONTRACT)
        self.assertEqual(source["parser"], "packages/cli/parsers/icd11.py")
        self.assertEqual(source["kernel_policy_id"], policy["id"])
        self.assertEqual(policy["source_contract"], icd11.SOURCE_CONTRACT)
        self.assertIn("cid11_validator", policy["validators"])

    def test_normative_release_stays_on_hold(self):
        policy = json.loads((ROOT / "contracts/policies/KERNEL-POLICY-004.json").read_text())
        for field in ("sha256_required", "fail_closed", "wo_required",
                      "requires_human_review"):
            self.assertIs(policy[field], True, field)
        self.assertIs(policy["publication_allowed"], False)
        self.assertIs(policy["review_policy"]["approval_required"], True)
        self.assertIn("METADATA_ONLY", policy["processing_scope"])

    def test_stub_cid11_and_schema_never_unlock(self):
        from packages.cli.kernel.core import Kernel, VALIDATOR_HOLDS
        kernel = Kernel()
        self.assertEqual(VALIDATOR_HOLDS.get("cid11_validator"), "SELF_TEST_FAILED")
        self.assertEqual(VALIDATOR_HOLDS.get("schema_validator"), "SELF_TEST_FAILED")
        self.assertEqual(kernel.gate("KERNEL-POLICY-004"), 2)


if __name__ == "__main__":
    unittest.main()
