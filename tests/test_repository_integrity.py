"""Contratos mínimos e casos negativos para auditoria canônica (somente leitura)."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.verify_repository_integrity import inspect


class CanonicalIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ce-integrity-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "contracts/fontes").mkdir(parents=True)
        (self.root / "contracts/policies").mkdir(parents=True)
        self.parser = self.root / "packages/cli/adapters/dou.py"
        self.parser.parent.mkdir(parents=True)
        self.parser.write_text("# Fixture; não é implementação de produção\n")
        self.source = self.root / "contracts/fontes/cofen_dou.json"
        self.policy = self.root / "contracts/policies/KERNEL-POLICY-001.json"
        self.source_data = {
            "fonte_slug": "cofen_dou",
            "source_contract": "contracts/fontes/cofen_dou.json",
            "kernel_policy_id": "KERNEL-POLICY-001",
            "parser": "packages/cli/adapters/dou.py",
        }
        self.policy_data = {
            "id": "KERNEL-POLICY-001",
            "source_contract": "contracts/fontes/cofen_dou.json",
            "validators": ["atomo_schema_validator"],
        }
        self._save()

    def _save(self):
        self.source.write_text(json.dumps(self.source_data), encoding="utf-8")
        self.policy.write_text(json.dumps(self.policy_data), encoding="utf-8")

    def codes(self):
        return {x["code"] for x in inspect(self.root)["findings"]}

    def test_valid_minimal_registry(self):
        result = inspect(self.root)
        self.assertTrue(result["structural_pass"])
        self.assertTrue(result["strict_pass"])

    def test_reject_legacy_contracts_fonts(self):
        (self.root / "contracts/fonts").mkdir()
        self.assertIn("LEGACY_SOURCE_DIR", self.codes())

    def test_reject_slug_mismatch(self):
        self.source_data["fonte_slug"] = "outro"
        self._save()
        self.assertIn("SOURCE_SLUG_MISMATCH", self.codes())

    def test_reject_source_self_reference(self):
        self.source_data["source_contract"] = "contracts/fonts/cofen_dou.json"
        self._save()
        self.assertIn("SOURCE_SELF_REFERENCE", self.codes())

    def test_reject_policy_missing_source(self):
        self.policy_data["source_contract"] = "contracts/fontes/ausente.json"
        self._save()
        self.assertIn("POLICY_SOURCE_MISSING", self.codes())

    def test_reject_policy_without_validator(self):
        self.policy_data["validators"] = []
        self._save()
        self.assertIn("POLICY_NO_VALIDATORS", self.codes())

    def test_missing_parser_is_strict_hold(self):
        self.parser.unlink()
        result = inspect(self.root)
        self.assertTrue(result["structural_pass"])
        self.assertFalse(result["strict_pass"])
        self.assertIn("MISSING_PARSER", self.codes())

    def test_invalid_import_is_strict_hold(self):
        f = self.root / "packages/cli/main.py"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("from kernel.core import Kernel\n", encoding="utf-8")
        result = inspect(self.root)
        self.assertTrue(result["structural_pass"])
        self.assertFalse(result["strict_pass"])
        self.assertIn("PACKAGE_IMPORT_NAMESPACE", self.codes())

    def test_reject_invalid_source_json(self):
        self.source.write_text("{garbled", encoding="utf-8")
        self.assertIn("INVALID_SOURCE_JSON", self.codes())

    def test_reject_empty_registry(self):
        self.source.unlink()
        self.policy.unlink()
        self.assertIn("EMPTY_REGISTRY", self.codes())

    def test_reject_wrong_policy_id(self):
        self.policy_data["id"] = "KERNEL-POLICY-999"
        self._save()
        self.assertIn("POLICY_ID_MISMATCH", self.codes())


if __name__ == "__main__":
    unittest.main()
