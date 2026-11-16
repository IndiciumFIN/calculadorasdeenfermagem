"""Offline fail-closed checks for two ANVISA source contracts.

Only validates repository metadata; does not fetch sources, publish content,
or authorize migration/clinical promotion.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ("anvisa_dev", "anvisa_dou")


class AnvisaContractPathsTests(unittest.TestCase):
    def test_canonical_contracts_are_self_referential(self):
        for slug in CONTRACTS:
            with self.subTest(slug=slug):
                path = ROOT / "contracts" / "fontes" / f"{slug}.json"
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(payload["fonte_slug"], slug)
                self.assertEqual(
                    payload["source_contract"],
                    f"contracts/fontes/{slug}.json",
                )
                self.assertIsInstance(payload["validators"], list)
                self.assertTrue(payload["validators"])
                self.assertTrue(all(isinstance(v, str) and v.strip()
                                    for v in payload["validators"]))
                self.assertTrue(payload["kernel_policy_required"])
                self.assertTrue(payload["kernel_policy_id"].strip())

    def test_declared_parser_paths_resolve_inside_repository(self):
        for slug in CONTRACTS:
            with self.subTest(slug=slug):
                payload = json.loads(
                    (ROOT / "contracts" / "fontes" / f"{slug}.json")
                    .read_text(encoding="utf-8")
                )
                relative = Path(payload["parser"])
                self.assertFalse(relative.is_absolute())
                self.assertNotIn("..", relative.parts)
                self.assertTrue((ROOT / relative).is_file(),
                                f"Missing parser for {slug}: {relative}")


if __name__ == "__main__":
    unittest.main()
