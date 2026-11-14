"""Regression guard: technical CI failures and source provenance must not be swallowed.

This suite checks only a small number of explicit CI invariants. It does not
attest G6 (independent human/clinical approval) or any external legal validity.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/ci.yml"


def verify_ci_text(source):
    missing = []
    for required in ("npm ci", "npm run type-check", "python -m packages.cli.main --help",
                     "test_kernel_", "contents: read"):
        if required not in source:
            missing.append("MISSING:" + required)
    for dangerous in ("|| echo", "continue-on-error: true", "npm install",
                      "|| true", "exit 0 #"):
        if dangerous in source:
            missing.append("BYPASS:" + dangerous)
    return missing


def verify_next_lock(data):
    errors = []
    try:
        packages = data["packages"]
        expected = packages["node_modules/next"]["dependencies"]["postcss"]
        parent = packages.get("node_modules/postcss", {})
        entry = (parent if parent.get("version") == expected else
                 packages.get("node_modules/next/node_modules/postcss", {}))
        if entry.get("version") != expected:
            errors.append("MISSING_EXACT_NEXT_POSTCSS")
        if not str(entry.get("integrity", "")).startswith("sha512-"):
            errors.append("MISSING_INTEGRITY")
        if entry.get("resolved") != (
            "https://registry.npmjs.org/postcss/-/postcss-" + expected + ".tgz"
        ):
            errors.append("INVALID_PACKAGE_SOURCE")
    except (KeyError, TypeError):
        errors.append("BROKEN_LOCK_GRAPH")
    return errors


class CIFailClosedTests(unittest.TestCase):
    def test_required_checks_mandatory(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertEqual(verify_ci_text(text), [])

    def test_detects_masked_typescript_failure(self):
        source = WORKFLOW.read_text(encoding="utf-8").replace(
            "npm run type-check", "npm run type-check || echo skipped")
        self.assertIn("BYPASS:|| echo", verify_ci_text(source))
        self.assertIn("MISSING:npm run type-check", verify_ci_text(
            WORKFLOW.read_text(encoding="utf-8").replace(
                "npm run type-check", "echo approved")))

    def test_detects_skipped_cli_and_install_fallback(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        altered = text.replace(
            "python -m packages.cli.main --help",
            "python -m packages.cli.main --help || true")
        self.assertIn("BYPASS:|| true", verify_ci_text(altered))
        altered = text.replace("npm ci", "npm install")
        self.assertIn("BYPASS:npm install", verify_ci_text(altered))

    def test_exact_nested_next_postcss_resolution(self):
        package = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
        deps = package["packages"]
        next_package = deps["node_modules/next"]
        exact = next_package["dependencies"]["postcss"]
        self.assertEqual(exact, "8.4.31")
        nested = deps["node_modules/next/node_modules/postcss"]
        self.assertEqual(nested["version"], exact)
        self.assertTrue(nested["integrity"].startswith("sha512-"))
        self.assertEqual(
            nested["resolved"],
            "https://registry.npmjs.org/postcss/-/postcss-8.4.31.tgz",
        )
        self.assertNotEqual(deps["node_modules/postcss"]["version"], exact)
        self.assertEqual(verify_next_lock(package), [])

    def test_detects_absent_nested_lock_entry(self):
        data = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
        data["packages"].pop("node_modules/next/node_modules/postcss")
        self.assertIn("MISSING_EXACT_NEXT_POSTCSS", verify_next_lock(data))

    def test_detects_replaced_integrity(self):
        data = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
        data["packages"]["node_modules/next/node_modules/postcss"]["integrity"] = "unknown"
        self.assertIn("MISSING_INTEGRITY", verify_next_lock(data))


if __name__ == "__main__":
    unittest.main()
