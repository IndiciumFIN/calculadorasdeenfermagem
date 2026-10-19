"""P1 ZIP guard surprises and negative testing; synthetic archives only."""
import hashlib
import io
import pathlib
import tempfile
import unittest
import zipfile
from ce_p1_zip_guard import audit_zip

DATA=b"Alpha data for deterministic hash"
def manifest(name="safe.txt",data=DATA):
    return {"members":[{"path":name,"sha256":hashlib.sha256(data).hexdigest(),"byte_length":len(data)}]}

class P1ZipTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path=pathlib.Path(self.tmp.name)/"fixture.zip"

    def write(self,files,compression=zipfile.ZIP_DEFLATED):
        with zipfile.ZipFile(self.path,"w",compression=compression) as z:
            for name,data in files:
                z.writestr(name,data)

    def test_bounded_pass(self):
        self.write([("safe.txt",DATA)])
        self.assertEqual(audit_zip(self.path,manifest())["decision"],"PASS_BOUNDED")

    def test_wrong_hash(self):
        self.write([("safe.txt",b"other")])
        self.assertTrue(any(x.startswith("MEMBER_SHA_MISMATCH") for x in audit_zip(self.path,manifest())["errors"]))

    def test_missing_member(self):
        self.write([("other.txt",DATA)])
        self.assertIn("POPULATION_MISMATCH",audit_zip(self.path,manifest())["errors"])

    def test_extra_member(self):
        self.write([("safe.txt",DATA),("hidden.txt",b"x")])
        self.assertIn("POPULATION_MISMATCH",audit_zip(self.path,manifest())["errors"])

    def test_duplicate_members(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.write([("safe.txt",DATA),("safe.txt",DATA)])
        self.assertIn("DUPLICATE_OR_CASE_COLLISION",audit_zip(self.path,manifest())["errors"])

    def test_case_collision(self):
        self.write([("safe.txt",DATA),("SAFE.TXT",DATA)])
        self.assertIn("DUPLICATE_OR_CASE_COLLISION",audit_zip(self.path,manifest())["errors"])

    def test_zip_slip(self):
        self.write([("../escape.txt",DATA)])
        self.assertIn("ZIP_SLIP_PATH",audit_zip(self.path,manifest("../escape.txt"))["errors"])

    def test_directory_traversal(self):
        self.write([("../escape/",b""),("safe.txt",DATA)])
        self.assertIn("ZIP_SLIP_PATH",audit_zip(self.path,manifest())["errors"])

    def test_backslash_windows(self):
        self.write([("..\\evil.txt",DATA)])
        self.assertIn("ZIP_SLIP_PATH",audit_zip(self.path,manifest("..\\evil.txt"))["errors"])

    def test_archive_sha_mismatch(self):
        self.write([("safe.txt",DATA)])
        x=manifest();x["archive_sha256"]="f"*64
        self.assertIn("ARCHIVE_SHA_MISMATCH",audit_zip(self.path,x)["errors"])

    def test_zip_bomb_ratio(self):
        data=b"0"*2000000
        self.write([("safe.txt",data)])
        self.assertTrue(any(x.startswith("DECOMPRESSION_LIMIT") for x in audit_zip(self.path,manifest(data=data))["errors"]))

    def test_nested_hold(self):
        self.write([("nested.zip",DATA)])
        x=audit_zip(self.path,manifest("nested.zip"))
        self.assertEqual(x["decision"],"HOLD")

    def test_invalid_archive(self):
        self.path.write_bytes(b"not-a-zip")
        self.assertTrue(any(x.startswith("INVALID_ARCHIVE") for x in audit_zip(self.path,manifest())["errors"]))

    def test_oversized_expected_length(self):
        self.write([("safe.txt",DATA)])
        x=manifest();x["members"][0]["byte_length"]=999
        self.assertTrue(any(x.startswith("MEMBER_LENGTH_MISMATCH") for x in audit_zip(self.path,x)["errors"]))

    def test_symlink_member(self):
        import stat
        info=zipfile.ZipInfo("safe.txt")
        info.create_system=3
        info.external_attr=(stat.S_IFLNK | 0o777)<<16
        with zipfile.ZipFile(self.path,"w") as z:
            z.writestr(info,b"target")
        self.assertTrue(any(x.startswith("SYMLINK_MEMBER") for x in audit_zip(self.path,manifest(data=b"target"))["errors"]))

    def test_surprise_mutations(self):
        import random
        rnd=random.Random(20261019)
        for i in range(30):
            mutate=bytearray(DATA)
            mutate[rnd.randrange(len(mutate))] ^= rnd.randrange(1,256)
            self.write([("safe.txt",bytes(mutate))])
            r=audit_zip(self.path,manifest())
            self.assertEqual(r["decision"],"FAIL",str(i))

if __name__=="__main__":
    unittest.main()
