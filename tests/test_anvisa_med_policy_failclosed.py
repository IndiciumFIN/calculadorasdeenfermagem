"""Anvisa medicines source/policy chain cannot grant clinical permissions."""
import json
import unittest
from pathlib import Path
from packages.cli.parsers import anvisa_med

ROOT=Path(__file__).resolve().parents[1]


class AnvisaMedPolicyTests(unittest.TestCase):
    def test_contract_and_parser_binding(self):
        a=json.loads((ROOT/"contracts/fontes/anvisa_med.json").read_text())
        b=json.loads((ROOT/"contracts/policies/KERNEL-POLICY-006.json").read_text())
        self.assertEqual(a["parser"],"packages/cli/parsers/anvisa_med.py")
        self.assertEqual(a["parser_version"],anvisa_med.PARSER_API_VERSION)
        self.assertEqual(a["source_contract"],anvisa_med.SOURCE_CONTRACT)
        self.assertEqual(a["kernel_policy_id"],b["id"])
        self.assertEqual(b["source_contract"],anvisa_med.SOURCE_CONTRACT)

    def test_rights_and_reviewer_required(self):
        p=json.loads((ROOT/"contracts/policies/KERNEL-POLICY-006.json").read_text())
        for key in ("sha256_required","fail_closed","requires_human_review","wo_required"):
            self.assertTrue(p[key])
        self.assertFalse(p["publication_allowed"])
        self.assertFalse(p["rights_by_operation_approved"])
        self.assertIn("METADATA_ONLY",p["processing_scope"])
        self.assertEqual(p["review_policy"]["approval_required"],"enfermeiro_registrado")

    def test_stub_validators_stay_blocked(self):
        from packages.cli.kernel.core import Kernel,VALIDATOR_HOLDS
        k=Kernel()
        self.assertEqual(VALIDATOR_HOLDS.get("schema_validator"),"SELF_TEST_FAILED")
        self.assertEqual(VALIDATOR_HOLDS.get("ncm_validator"),"SELF_TEST_FAILED")
        self.assertEqual(k.gate("KERNEL-POLICY-006"),2)


if __name__=="__main__":
    unittest.main()
