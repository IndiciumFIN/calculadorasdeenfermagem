"""Regression tests: integrity checks must reject missing/tampered PMO and release flags."""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
FILES = ("GIT_SYNC_MANIFEST.json", "PMO_REGISTER_SNAPSHOT_M08_M09.json",
         "validate-atomic-content.py")


class FailClosedCorpusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cko-fail-closed-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "archives").mkdir()
        for name in FILES:
            shutil.copy2(HERE / name, self.root / name)
        for src in (HERE / "archives").glob("*.zip"):
            shutil.copy2(src, self.root / "archives" / src.name)

    def run_validator(self):
        result = subprocess.run(
            [sys.executable, str(self.root / "validate-atomic-content.py")],
            cwd=self.root, capture_output=True, text=True, check=False)
        try:
            report = json.loads(result.stdout)
        except ValueError:
            self.fail(f"Validator did not emit JSON: {result.stdout} {result.stderr}")
        return result.returncode, report

    def load_snapshot(self):
        return json.loads((self.root / FILES[1]).read_text(encoding="utf-8"))

    def write_snapshot(self, content):
        (self.root / FILES[1]).write_text(
            json.dumps(content, ensure_ascii=False), encoding="utf-8")

    def test_original_fixture_passes_with_publication_blocked(self):
        code, result = self.run_validator()
        self.assertEqual(code, 0, result)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["publication"])

    def test_missing_snapshot_fails(self):
        (self.root / FILES[1]).unlink()
        code, result = self.run_validator()
        self.assertNotEqual(code, 0)
        self.assertIn("PMO snapshot is required", result["errors"])

    def test_missing_pmo_row_fails(self):
        data = self.load_snapshot()
        next(r for r in data["registers"] if r["register"] == "CLAIM_LEDGER")["rows"].pop()
        self.write_snapshot(data)
        code, result = self.run_validator()
        self.assertNotEqual(code, 0)
        self.assertIn("PMO register row counts", result["errors"])

    def test_invalid_source_link_fails(self):
        data = self.load_snapshot()
        next(r for r in data["registers"] if r["register"] == "DOCUMENT_REGISTER")["rows"][0][1] = "SRC-UNKNOWN"
        self.write_snapshot(data)
        code, result = self.run_validator()
        self.assertNotEqual(code, 0)
        self.assertIn("Document references unknown source", result["errors"])

    def test_publication_flag_fails(self):
        data = json.loads((self.root / FILES[0]).read_text(encoding="utf-8"))
        data["publication_allowed"] = True
        (self.root / FILES[0]).write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8")
        code, result = self.run_validator()
        self.assertNotEqual(code, 0)
        self.assertIn("manifest publication hold", result["errors"])


if __name__ == "__main__":
    unittest.main()
