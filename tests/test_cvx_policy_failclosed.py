"""CDC CVX contract-bound policy keeps publication and validator stubs in HOLD."""
import json
import unittest
from pathlib import Path

from packages.cli.parsers import vacinas

ROOT = Path(__file__).resolve().parents[1]


class CVXPolicyTests(unittest.TestCase):
    def test_source_contract_and_policy_are_bound(self):
        source = json.loads((ROOT / "contracts/fontes/vacinas_cdc.json").read_text())
        policy = json.loads((ROOT / "contracts/policies/KERNEL-POLICY-007.json").read_text())
        self.assertEqual(source["parser"], "packages/cli/parsers/vacinas.py")
        self.assertEqual(source["source_contract"], vacinas.SOURCE_CONTRACT)
        self.assertEqual(source["kernel_policy_id"], policy["id"])
        self.assertEqual(policy["source_contract"], vacinas.SOURCE_CONTRACT)
        self.assertIn("cvx_validator", policy["validators"])

    def test_source_provenance_rights_and_human_review_fail_closed(self):
        p = json.loads((ROOT / "contracts/policies/KERNEL-POLICY-007.json").read_text())
        for key in ("sha256_required", "fail_closed", "requires_human_review", "wo_required"):
            self.assertIs(p[key], True, key)
        self.assertIs(p["publication_allowed"], False)
        self.assertIs(p["review_policy"]["approval_required"], True)
        self.assertIn("METADATA_ONLY", p["processing_scope"])

    def test_stub_cvx_and_schema_validators_not_auto_admitted(self):
        from packages.cli.kernel.core import Kernel, VALIDATOR_HOLDS
        kernel = Kernel()
        for name in ("cvx_validator", "schema_validator"):
            self.assertEqual(VALIDATOR_HOLDS.get(name), "SELF_TEST_FAILED")
        self.assertEqual(kernel.gate("KERNEL-POLICY-007"), 2)


if __name__ == "__main__":
    unittest.main()
