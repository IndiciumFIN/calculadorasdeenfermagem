"""MeSH parser policy must preserve review, source, rights and lineage controls."""
import json
import unittest
from pathlib import Path
from packages.cli.parsers import mesh

ROOT = Path(__file__).resolve().parents[1]


class MeshPolicyTests(unittest.TestCase):
    def test_source_contract_policy_links(self):
        contract = json.loads((ROOT / "contracts/fontes/mesh.json").read_text())
        policy = json.loads((ROOT / "contracts/policies/KERNEL-POLICY-005.json").read_text())
        self.assertEqual(contract["parser"], "packages/cli/parsers/mesh.py")
        self.assertEqual(contract["source_contract"], mesh.SOURCE_CONTRACT)
        self.assertEqual(contract["kernel_policy_id"], policy["id"])
        self.assertEqual(policy["source_contract"], mesh.SOURCE_CONTRACT)

    def test_no_clinical_publication_approval_implicit(self):
        policy = json.loads((ROOT / "contracts/policies/KERNEL-POLICY-005.json").read_text())
        for key in ("sha256_required", "wo_required", "fail_closed", "requires_human_review"):
            self.assertIs(policy[key], True, key)
        self.assertIs(policy["publication_allowed"], False)
        self.assertIs(policy["review_policy"]["approval_required"], True)
        self.assertEqual(policy["processing_scope"], "METADATA_ONLY_PENDING_NLM_RIGHTS")

    def test_stub_terminology_validator_is_not_enabled(self):
        from packages.cli.kernel.core import Kernel, VALIDATOR_HOLDS
        kernel = Kernel()
        self.assertEqual(VALIDATOR_HOLDS.get("mesh_validator"), "SELF_TEST_FAILED")
        self.assertEqual(kernel.gate("KERNEL-POLICY-005"), 2)


if __name__ == "__main__":
    unittest.main()
