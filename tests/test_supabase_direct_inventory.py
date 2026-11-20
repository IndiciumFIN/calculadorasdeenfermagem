import hashlib
import pathlib
import tempfile
import unittest
from scripts.verify_supabase_snapshot import Hold, verify, verify_file

class SnapshotChecks(unittest.TestCase):
    def test_full_source_integrity(self):
        self.assertEqual(verify()["source_files"], 22)

    def test_detect_tampering(self):
        with tempfile.TemporaryDirectory() as temp:
            path = pathlib.Path(temp, "test.jsonl")
            path.write_text('{"ok":true}\n')
            raw = path.read_bytes()
            sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            meta = {"bytes": len(raw), "git_blob_sha1": sha, "record_count": 1}
            self.assertEqual(len(verify_file(path, meta)), 1)
            path.write_text('{"ok":false}\n')
            with self.assertRaisesRegex(Hold, "SOURCE_HASH_OR_SIZE_DRIFT"):
                verify_file(path, meta)

if __name__ == "__main__":
    unittest.main()
