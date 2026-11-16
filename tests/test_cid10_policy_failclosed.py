"""CID-10 DATASUS source and Kernel policy must remain unapproved."""
import json
import unittest
from pathlib import Path

from packages.cli.parsers import cid10

ROOT=Path(__file__).resolve().parents[1]


class Cid10CategoryPolicyTests(unittest.TestCase):
    def test_source_version_and_parser_link(self):
        s=json.loads((ROOT/"contracts/fontes/cid10.json").read_text())
        p=json.loads((ROOT/"contracts/policies/KERNEL-POLICY-003.json").read_text())
        self.assertEqual(s["source_contract"],cid10.SOURCE_CONTRACT)
        self.assertEqual(s["parser"],"packages/cli/parsers/cid10.py")
        self.assertEqual(s["parser_version"],cid10.PARSER_API_VERSION)
        self.assertEqual(s["kernel_policy_id"],p["id"])
        self.assertEqual(p["source_contract"],cid10.SOURCE_CONTRACT)

    def test_rights_checksum_and_independent_review_hold(self):
        p=json.loads((ROOT/"contracts/policies/KERNEL-POLICY-003.json").read_text())
        for key in ("sha256_required","fail_closed","requires_human_review","wo_required"):
            self.assertIs(p[key],True,key)
        self.assertIs(p["publication_allowed"],False)
        self.assertIs(p["rights_by_operation_approved"],False)
        self.assertIn("METADATA_ONLY",p["processing_scope"])

    def test_stub_terminology_validator_does_not_approve(self):
        from packages.cli.kernel.core import Kernel,VALIDATOR_HOLDS
        kernel=Kernel()
        self.assertEqual(VALIDATOR_HOLDS.get("cid10_validator"),"SELF_TEST_FAILED")
        self.assertEqual(VALIDATOR_HOLDS.get("schema_validator"),"SELF_TEST_FAILED")
        self.assertEqual(kernel.gate("KERNEL-POLICY-003"),2)


if __name__ == "__main__":
    unittest.main()
