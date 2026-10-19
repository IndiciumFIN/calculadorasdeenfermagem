"""P1 Git blob crosswalk synthetic tests."""
import hashlib
import pathlib
import tempfile
import unittest
from ce_p1_git_blob_guard import audit

DATA=b"canonical snapshot"
def one(path,data):
    return {"path":path,"sha256":hashlib.sha256(data).hexdigest(),
            "git_blob_sha1":hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest(),
            "byte_length":len(data)}

class GitBlobTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name)
        (self.root/"a.txt").write_bytes(DATA)
        self.m={"files":[one("a.txt",DATA)]}

    def test_original(self):
        x=audit(self.root,self.m)
        self.assertEqual(x["decision"],"PASS_BOUNDED")
        self.assertFalse(x["git_tree_authenticity_verified"])

    def test_tampered(self):
        (self.root/"a.txt").write_bytes(b"changed")
        self.assertTrue(any(x.startswith("MISMATCH:") for x in audit(self.root,self.m)["errors"]))

    def test_undeclared_extra(self):
        (self.root/"other").write_bytes(DATA)
        self.assertIn("POPULATION_MISMATCH",audit(self.root,self.m)["errors"])

    def test_missing(self):
        (self.root/"a.txt").unlink()
        self.assertIn("POPULATION_MISMATCH",audit(self.root,self.m)["errors"])

    def test_duplicate_manifest(self):
        self.assertIn("DUPLICATE_MANIFEST",audit(self.root,{"files":self.m["files"]*2})["errors"])

    def test_mismatched_git_blob_only(self):
        wrong=dict(self.m["files"][0],git_blob_sha1="0"*40)
        self.assertIn("MISMATCH:git_blob_sha1:a.txt",audit(self.root,{"files":[wrong]})["errors"])

    def test_path_traversal(self):
        item=dict(self.m["files"][0],path="../a.txt")
        self.assertIn("INVALID_PATH",audit(self.root,{"files":[item]})["errors"])

    def test_symlink_file(self):
        (self.root/"link").symlink_to(self.root/"a.txt")
        self.assertTrue(any("SYMLINK_FILE" in x for x in audit(self.root,self.m)["errors"]))

    def test_symlink_directory(self):
        (self.root/"dirlink").symlink_to(self.root,target_is_directory=True)
        self.assertTrue(any("SYMLINK_DIRECTORY" in x for x in audit(self.root,self.m)["errors"]))

    def test_snapshot_surprises(self):
        import random
        rnd=random.Random(20261019)
        for _ in range(30):
            data=bytearray(DATA)
            data[rnd.randrange(len(data))] ^= rnd.randrange(1,256)
            (self.root/"a.txt").write_bytes(data)
            self.assertEqual(audit(self.root,self.m)["decision"],"FAIL")

if __name__=="__main__":
    unittest.main()
