"""P0 integration: reuse three candidate parsers without admitting clinical content."""
import json
import unittest
from pathlib import Path

from scripts.verify_repository_integrity import inspect

ROOT = Path(__file__).resolve().parents[1]
PARSER_PATHS = {
    "fhir_vitais": "packages/cli/parsers/fhir.py",
    "medlineplus": "packages/cli/parsers/medlineplus.py",
    "mesh": "packages/cli/parsers/mesh.py",
}
POLICIES = {
    "KERNEL-POLICY-008.json": "fhir_vitais",
    "KERNEL-POLICY-015.json": "medlineplus",
    "KERNEL-POLICY-005.json": "mesh",
}

class P0ExistingParsersTest(unittest.TestCase):
    def test_three_sources_use_real_reused_parser_modules(self):
        for source, path in PARSER_PATHS.items():
            contract = json.loads((ROOT / "contracts" / "fontes" / f"{source}.json").read_text())
            self.assertEqual(contract["parser"], path)
            content = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn("def parse(", content)
            self.assertNotIn("NotImplementedError", content)

    def test_exactly_thirteen_unimplemented_source_contract_parsers_remain(self):
        result = inspect(ROOT)
        missing = [r for r in result["findings"] if r["code"] == "MISSING_PARSER"]
        self.assertEqual(len(missing), 13, missing)
        self.assertTrue(result["structural_pass"], result["findings"])
        self.assertFalse(result["strict_pass"], "Remaining parsers must block global admission")
        covered = {"contracts/fontes/" + x + ".json" for x in PARSER_PATHS}
        self.assertFalse(covered.intersection(r["path"] for r in missing))

    def test_three_policies_stay_fail_closed(self):
        for name, source in POLICIES.items():
            policy = json.loads((ROOT / "contracts" / "policies" / name).read_text())
            self.assertEqual(policy["source_contract"], f"contracts/fontes/{source}.json")
            self.assertIs(policy["publication_allowed"], False)
            self.assertIs(policy["requires_human_review"], True)
            self.assertIs(policy["wo_required"], True)
            self.assertIs(policy["fail_closed"], True)

    def test_xml_library_dependency_declared(self):
        req = (ROOT / "packages/cli/requirements.txt").read_text()
        self.assertIn("defusedxml>=0.7.1,<1", req)

if __name__ == "__main__":
    unittest.main()
