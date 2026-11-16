"""FHIR parser policy must not silently downgrade clinical or governance gates."""
import json
import unittest
from pathlib import Path

from packages.cli.parsers import fhir


ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "contracts/policies/KERNEL-POLICY-008.json"
CONTRACT = ROOT / "contracts/fontes/fhir_vitais.json"


class FhirPolicyTests(unittest.TestCase):
    def test_spec_and_contract_binding(self):
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["parser"], "packages/cli/parsers/fhir.py")
        self.assertEqual(contract["source_contract"], fhir.SOURCE_CONTRACT)
        self.assertEqual(policy["source_contract"], fhir.SOURCE_CONTRACT)
        self.assertEqual(contract["kernel_policy_id"], policy["id"])
        self.assertEqual(policy["id"], "KERNEL-POLICY-008")

    def test_no_human_or_source_gate_bypass(self):
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        for field in ("sha256_required", "fail_closed",
                      "requires_human_review", "wo_required"):
            self.assertIs(policy[field], True, field)
        self.assertIs(policy["review_policy"]["approval_required"], True)
        self.assertIs(policy["publication_allowed"], False)
        self.assertEqual(policy["processing_scope"],
                         "SYNTHETIC_ONLY_PENDING_LGPD_CLINICAL_REVIEW")

    def test_untested_schema_and_loinc_validators_are_not_admitted(self):
        from packages.cli.kernel.core import Kernel, VALIDATOR_HOLDS
        kernel = Kernel()
        self.assertIn("schema_validator", VALIDATOR_HOLDS)
        self.assertIn("loinc_validator", VALIDATOR_HOLDS)
        self.assertEqual(kernel.gate("KERNEL-POLICY-008"), 2)


if __name__ == "__main__":
    unittest.main()
