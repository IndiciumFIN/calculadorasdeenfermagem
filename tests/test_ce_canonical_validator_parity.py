"""Deterministic adversarial tests for canonical source/policy validator parity."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify_repository_integrity.py"
spec = importlib.util.spec_from_file_location("ce_verify_integrity", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CanonicalValidatorContractTests(unittest.TestCase):
    def inspect_fixture(self, source_validators, policy_validators):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "contracts/fontes").mkdir(parents=True)
            (root / "contracts/policies").mkdir(parents=True)
            src = {
                "fonte_slug": "example",
                "source_contract": "contracts/fontes/example.json",
                "kernel_policy_id": "KERNEL-POLICY-001",
                "parser": "parsers/example.py",
                "validators": source_validators,
            }
            pol = {
                "id": "KERNEL-POLICY-001",
                "source_contract": "contracts/fontes/example.json",
                "validators": policy_validators,
            }
            (root / "contracts/fontes/example.json").write_text(json.dumps(src), encoding="utf-8")
            (root / "contracts/policies/KERNEL-POLICY-001.json").write_text(json.dumps(pol), encoding="utf-8")
            result = module.inspect(root)
            return result, {finding["code"] for finding in result["findings"]}

    def test_valid_matching_contract_is_structurally_accepted(self):
        result, codes = self.inspect_fixture(["alpha", "beta_2"], ["alpha", "beta_2"])
        self.assertTrue(result["structural_pass"])
        self.assertFalse(result["strict_pass"])  # Missing parser remains fail-closed.
        self.assertIn("MISSING_PARSER", codes)

    def test_duplicate_policy_validator_rejected(self):
        result, codes = self.inspect_fixture(["alpha"], ["alpha", "alpha"])
        self.assertFalse(result["structural_pass"])
        self.assertIn("POLICY_NO_VALIDATORS", codes)

    def test_invalid_policy_validator_rejected(self):
        result, codes = self.inspect_fixture(["alpha"], ["Alpha-1"])
        self.assertFalse(result["structural_pass"])
        self.assertIn("POLICY_NO_VALIDATORS", codes)

    def test_invalid_source_validator_rejected(self):
        result, codes = self.inspect_fixture(["alpha", "alpha"], ["alpha"])
        self.assertFalse(result["structural_pass"])
        self.assertIn("SOURCE_VALIDATOR_SCHEMA", codes)

    def test_source_policy_drift_rejected(self):
        result, codes = self.inspect_fixture(["beta", "alpha"], ["alpha", "beta"])
        self.assertFalse(result["structural_pass"])
        self.assertIn("SOURCE_VALIDATOR_POLICY_DRIFT", codes)


if __name__ == "__main__":
    unittest.main()
