"""SIES source and policy controls are bound and cannot approve clinical output."""
import json
import unittest
from pathlib import Path
from packages.cli.parsers import sies

ROOT=Path(__file__).resolve().parents[1]


class SiesPolicyTests(unittest.TestCase):
    def test_source_parser_policy_links(self):
        a=json.loads((ROOT/"contracts/fontes/sies.json").read_text())
        b=json.loads((ROOT/"contracts/policies/KERNEL-POLICY-016.json").read_text())
        self.assertEqual(a["parser"],"packages/cli/parsers/sies.py")
        self.assertEqual(a["parser_version"],sies.PARSER_API_VERSION)
        self.assertEqual(a["source_contract"],sies.SOURCE_CONTRACT)
        self.assertEqual(a["kernel_policy_id"],b["id"])
        self.assertEqual(b["source_contract"],sies.SOURCE_CONTRACT)

    def test_source_and_human_approval_required(self):
        p=json.loads((ROOT/"contracts/policies/KERNEL-POLICY-016.json").read_text())
        for field in ("sha256_required","fail_closed","requires_human_review","wo_required"):
            self.assertTrue(p[field])
        self.assertFalse(p["publication_allowed"])
        self.assertFalse(p["rights_by_operation_approved"])
        self.assertTrue(p["review_policy"]["approval_required"])
        self.assertIn("METADATA_ONLY",p["processing_scope"])

    def test_unimplemented_schema_validator_cannot_autoapprove(self):
        from packages.cli.kernel.core import Kernel,VALIDATOR_HOLDS
        k=Kernel()
        self.assertEqual(VALIDATOR_HOLDS.get("schema_validator"),"SELF_TEST_FAILED")
        self.assertEqual(k.gate("KERNEL-POLICY-016"),2)


if __name__=="__main__":
    unittest.main()
