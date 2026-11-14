import io
import pathlib
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
from cko_p0_intake_audit import scan  # noqa: E402

class P0SourceIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def put_zip(self, name, items, compression=zipfile.ZIP_DEFLATED):
        path = self.root / name
        with zipfile.ZipFile(path, "w", compression=compression) as out:
            for filename, data in items:
                out.writestr(filename, data)
        return path
    def test_identical_content_with_different_zip_order(self):
        a = self.put_zip("a.zip", [("a.txt", "1"), ("b.txt", "2")])
        b = self.put_zip("b.zip", [("b.txt", "2"), ("a.txt", "1")], zipfile.ZIP_STORED)
        report = scan([a, b])
        self.assertEqual(report["duplicate_groups"], [["a.zip", "b.zip"]])
        self.assertEqual(report["integrity"], "PASS")
    def test_same_name_changed_bytes_is_not_duplicate(self):
        a = self.put_zip("a.zip", [("source.json", "one")])
        b = self.put_zip("b.zip", [("source.json", "two")])
        report = scan([a, b])
        self.assertEqual(report["duplicate_groups"], [])
        self.assertEqual(report["same_path_different_bytes"], ["source.json"])
    def test_zip_slip_fails_closed(self):
        path = self.put_zip("attack.zip", [("../escape", "unsafe")])
        self.assertEqual(scan([path])["integrity"], "HOLD")
    def test_nested_zip_inspection(self):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("fixture.json", "{}")
        path = self.put_zip("outer.zip", [("inner.zip", buffer.getvalue())])
        report = scan([path])
        self.assertEqual(report["integrity"], "PASS")
        self.assertEqual(len(report["inputs"][0]["nested_archives"][0]["entries"]), 1)
    def test_python_upload_is_never_executed(self):
        path = self.root / "evil.py"
        path.write_text('raise AssertionError("must never execute")')
        self.assertEqual(scan([path])["integrity"], "PASS")
    def test_no_medical_release_from_metadata(self):
        path = self.root / "claims.json"
        path.write_text('{"claim_id":"FAKE","clinical_approval":true}')
        report = scan([path])
        self.assertIs(report["clinical_approval"], False)
        self.assertIs(report["release_allowed"], False)
        self.assertEqual(report["p0_release"], "HOLD")
    def test_invalid_zip_holds(self):
        path = self.root / "bad.zip"
        path.write_bytes(b"invalid zip")
        self.assertEqual(scan([path])["integrity"], "HOLD")

if __name__ == "__main__":
    unittest.main()
