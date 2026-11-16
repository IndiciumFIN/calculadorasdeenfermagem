"""Source/policy device registry cannot silently approve medical products."""
import json
import unittest
from pathlib import Path
from packages.cli.parsers import anvisa_dev

ROOT=Path(__file__).resolve().parents[1]

class AnvisaDevicePolicyTests(unittest.TestCase):
    def test_source_parser_policy_automatically_linked(self):
        source=json.loads((ROOT/"contracts/fontes/anvisa_dev.json").read_text())
        policy=json.loads((ROOT/"contracts/policies/KERNEL-POLICY-009.json").read_text())
        self.assertEqual(source["parser"],"packages/cli/parsers/anvisa_dev.py")
        self.assertEqual(source["source_contract"],anvisa_dev.SOURCE_CONTRACT)
        self.assertEqual(source["parser_version"],anvisa_dev.PARSER_API_VERSION)
        self.assertEqual(source["kernel_policy_id"],policy["id"])
        self.assertEqual(policy["source_contract"],anvisa_dev.SOURCE_CONTRACT)

    def test_provenance_rights_and_wo_mandatory(self):
        policy=json.loads((ROOT/"contracts/policies/KERNEL-POLICY-009.json").read_text())
        for field in ("sha256_required","fail_closed","requires_human_review","wo_required"):
            self.assertTrue(policy[field])
        self.assertFalse(policy["publication_allowed"])
        self.assertFalse(policy["rights_by_operation_approved"])
        self.assertIn("METADATA_ONLY",policy["processing_scope"])

    def test_schema_stub_must_not_enable_release(self):
        from packages.cli.kernel.core import Kernel,VALIDATOR_HOLDS
        kernel=Kernel()
        self.assertEqual(VALIDATOR_HOLDS.get("schema_validator"),"SELF_TEST_FAILED")
        self.assertEqual(kernel.gate("KERNEL-POLICY-009"),2)

if __name__=="__main__":
    unittest.main()
