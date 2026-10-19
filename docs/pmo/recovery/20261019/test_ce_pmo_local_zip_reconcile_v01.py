#!/usr/bin/env python3
"""Pure-function and rejection tests for P1-C hash reconciliation."""
import hashlib
import io
import unittest
from pathlib import Path

from ce_pmo_local_zip_reconcile_v01 import payload_hash, reconcile


class ReconcileTests(unittest.TestCase):
    def test_byte_equality(self):
        self.assertEqual(payload_hash(io.BytesIO(b"same")), hashlib.sha256(b"same").hexdigest())

    def test_empty_member(self):
        self.assertEqual(payload_hash(io.BytesIO(b"")), hashlib.sha256(b"").hexdigest())

    def test_different_bytes(self):
        self.assertNotEqual(payload_hash(io.BytesIO(b"a")), payload_hash(io.BytesIO(b"A")))

    def test_wrong_scope_fails_closed(self):
        with self.assertRaises(ValueError):
            reconcile(Path("/not-the-script-workspace"))


if __name__ == "__main__":
    unittest.main()
