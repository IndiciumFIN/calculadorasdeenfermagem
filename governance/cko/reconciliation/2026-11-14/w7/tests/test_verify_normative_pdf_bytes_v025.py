import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "verify_normative_pdf_bytes_v0.2.5.py"
spec = importlib.util.spec_from_file_location("verify_norm", SCRIPT)
verify_norm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify_norm)


class TestNormativeReceipt(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.file = Path(self.dir.name) / "test.pdf"
        self.bytes = b"%PDF-1.4\n%data fixture\n"
        self.file.write_bytes(self.bytes)
        self.sha = hashlib.sha256(self.bytes).hexdigest()

    def check(self, kind="DERIVED_DOSSIER", sha=None, size=None, file=None):
        return verify_norm.verify(file or self.file, sha or self.sha, kind, size)

    def test_dossier_never_promoted(self):
        r = self.check(size=len(self.bytes))
        self.assertEqual(r["status"], "DERIVED_DOSSIER_BYTES_MATCH_HOLD_PRIMARY")
        self.assertFalse(r["primary_source_approved"])
        self.assertFalse(r["publication_allowed"])

    def test_official_candidate_never_auto_approved(self):
        r = self.check(kind="OFFICIAL_PRIMARY_CANDIDATE")
        self.assertEqual(r["status"], "OFFICIAL_CANDIDATE_BYTES_MATCH_HOLD_LEGAL_RIGHTS_CLINICAL")
        self.assertFalse(r["normative_currentness_approved"])
        self.assertFalse(r["reuse_rights_approved"])
        self.assertFalse(r["publication_allowed"])

    def test_secondary_dossier_cli_exits_nonzero(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "--input", str(self.file),
                              "--expected-sha256", self.sha, "--kind", "DERIVED_DOSSIER"],
                             check=False, text=True, capture_output=True)
        self.assertEqual(run.returncode, 2)
        receipt = json.loads(run.stdout)
        self.assertEqual(receipt["status"], "DERIVED_DOSSIER_BYTES_MATCH_HOLD_PRIMARY")
        self.assertFalse(receipt["publication_allowed"])

    def test_official_candidate_cli_exits_zero_for_bytes_only(self):
        run = subprocess.run([sys.executable, str(SCRIPT), "--input", str(self.file),
                              "--expected-sha256", self.sha, "--kind", "OFFICIAL_PRIMARY_CANDIDATE"],
                             check=False, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0)
        receipt = json.loads(run.stdout)
        self.assertFalse(receipt["normative_currentness_approved"])
        self.assertFalse(receipt["publication_allowed"])

    def test_wrong_hash_blocks(self):
        self.assertEqual(self.check(sha="0" * 64)["status"], "HOLD_HASH_OR_SIZE_MISMATCH")

    def test_wrong_size_blocks(self):
        self.assertEqual(self.check(size=1)["status"], "HOLD_HASH_OR_SIZE_MISMATCH")

    def test_non_pdf_blocks(self):
        self.file.write_bytes(b"NOT_A_PDF\n")
        self.assertEqual(self.check()["status"], "HOLD_NOT_PDF")

    def test_missing_blocks(self):
        self.assertEqual(self.check(file=self.file.with_name("missing.pdf"))["status"], "HOLD_FILE_MISSING")

    def test_bad_sha_rejected(self):
        with self.assertRaises(ValueError):
            self.check(sha="abc")

    def test_unknown_kind_rejected(self):
        with self.assertRaises(ValueError):
            self.check(kind="ASSURED")


if __name__ == "__main__":
    unittest.main()
