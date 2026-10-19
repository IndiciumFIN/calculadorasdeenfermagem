#!/usr/bin/env python3
"""Deterministic tests for Git blob object hashing, no filesystem writes."""
import io
import unittest

from ce_pmo_git_blob_index_v01 import git_blob_hash


class GitBlobIndexTests(unittest.TestCase):
    def test_known_git_object(self):
        self.assertEqual(git_blob_hash(io.BytesIO(b"hello\n"), 6), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_empty_object(self):
        self.assertEqual(git_blob_hash(io.BytesIO(b""), 0), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")

    def test_short_read_blocks(self):
        with self.assertRaises(ValueError):
            git_blob_hash(io.BytesIO(b"tiny"), 5)

    def test_excess_bytes_blocks(self):
        with self.assertRaises(ValueError):
            git_blob_hash(io.BytesIO(b"long"), 3)


if __name__ == "__main__":
    unittest.main()
