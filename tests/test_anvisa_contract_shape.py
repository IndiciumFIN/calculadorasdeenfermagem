"""Regression: canonical ANVISA source contracts must retain validator arrays.

Offline-only; no database or network access.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestAnvisaContractShape(unittest.TestCase):
    def test_anvisa_dev_validator_list(self):
        path = ROOT / "contracts/fontes/anvisa_dev.json"
        contract = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(contract["validators"], list)
        self.assertTrue(contract["validators"])
        self.assertTrue(all(isinstance(v, str) and v for v in contract["validators"]))
        self.assertEqual(contract["source_contract"], "contracts/fontes/anvisa_dev.json")

    def test_anvisa_dou_validator_list(self):
        path = ROOT / "contracts/fontes/anvisa_dou.json"
        contract = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(contract["validators"], list)
        self.assertEqual(contract["source_contract"], "contracts/fontes/anvisa_dou.json")


if __name__ == "__main__":
    unittest.main()
