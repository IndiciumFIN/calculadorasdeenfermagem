"""MedlinePlus educational metadata cannot bypass provenance/review gates."""
import json
import unittest
from pathlib import Path
from packages.cli.parsers import medlineplus

ROOT = Path(__file__).resolve().parents[1]


class MedlineplusPolicyTests(unittest.TestCase):
    def test_contract_is_bidirectionally_linked(self):
        contract = json.loads((ROOT / "contracts/fontes/medlineplus.json").read_text())
        policy = json.loads((ROOT / "contracts/policies/KERNEL-POLICY-015.json").read_text())
        self.assertEqual(contract["parser"], "packages/cli/parsers/medlineplus.py")
        self.assertEqual(contract["source_contract"], medlineplus.SOURCE_CONTRACT)
        self.assertEqual(contract["kernel_policy_id"], policy["id"])
        self.assertEqual(policy["source_contract"], medlineplus.SOURCE_CONTRACT)

    def test_policy_requires_provenance_rights_and_human_review(self):
        policy = json.loads((ROOT / "contracts/policies/KERNEL-POLICY-015.json").read_text())
        for key in ("sha256_required", "fail_closed", "wo_required", "requires_human_review"):
            self.assertIs(policy[key], True, key)
        self.assertIs(policy["review_policy"]["approval_required"], True)
        self.assertIs(policy["publication_allowed"], False)
        self.assertEqual(policy["processing_scope"], "METADATA_ONLY_PENDING_EDITORIAL_RIGHTS")

    def test_kernel_still_rejects_stub_schema_validator(self):
        from packages.cli.kernel.core import Kernel, VALIDATOR_HOLDS
        kernel = Kernel()
        self.assertEqual(VALIDATOR_HOLDS.get("schema_validator"), "SELF_TEST_FAILED")
        self.assertEqual(kernel.gate("KERNEL-POLICY-015"), 2)


if __name__ == "__main__":
    unittest.main()
