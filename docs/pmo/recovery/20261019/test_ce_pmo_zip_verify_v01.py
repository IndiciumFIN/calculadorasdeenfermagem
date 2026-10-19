#!/usr/bin/env python3
"""In-memory adversarial ZIP tests; no filesystem writes."""
import io
import stat
import unittest
import zipfile

from ce_pmo_zip_verify_v01 import inspect_zip, unsafe_name


def archive_with(name: str, payload: bytes = b"alpha", *, symlink: bool = False) -> io.BytesIO:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_STORED) as archive:
        info = zipfile.ZipInfo(name)
        if symlink:
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
        archive.writestr(info, payload)
    stream.seek(0)
    return stream


class ZipVerificationTests(unittest.TestCase):
    def test_safe_path(self):
        self.assertFalse(unsafe_name("docs/legal.txt"))

    def test_parent_escape(self):
        self.assertTrue(unsafe_name("../outside.txt"))

    def test_backslash_escape(self):
        self.assertTrue(unsafe_name("folder\\..\\outside.txt"))

    def test_windows_drive(self):
        self.assertTrue(unsafe_name("C:/secret.txt"))

    def test_absolute_path(self):
        self.assertTrue(unsafe_name("/tmp/unsafe.txt"))

    def test_positive_crc(self):
        result = inspect_zip(archive_with("safe.txt"))
        self.assertEqual(result["status"], "PASS_ZIP_INTEGRITY_ONLY")
        self.assertEqual(result["counts"]["payload_crc_verified"], 1)

    def test_unsafe_zip_hold(self):
        self.assertIn("ZIP_PATH_TRAVERSAL", inspect_zip(archive_with("../escape"))["findings"])

    def test_symlink_zip_hold(self):
        self.assertIn("ZIP_SYMLINK_ENTRY", inspect_zip(archive_with("link", symlink=True))["findings"])

    def test_member_budget_hold(self):
        result = inspect_zip(archive_with("b.txt", b"0123456789"), max_member=5)
        self.assertIn("ZIP_MEMBER_BUDGET_EXCEEDED", result["findings"])

    def test_archive_budget_hold(self):
        result = inspect_zip(archive_with("b.txt", b"0123456789"), max_archive=5)
        self.assertIn("ZIP_ARCHIVE_BUDGET_EXCEEDED", result["findings"])

    def test_corrupted_payload_crc_hold(self):
        stream = archive_with("crc.txt", b"UNIQUE_PAYLOAD_VALUE")
        raw = stream.getvalue().replace(b"UNIQUE_PAYLOAD_VALUE", b"BROKEN_PAYLOAD_VALUE", 1)
        result = inspect_zip(io.BytesIO(raw))
        self.assertIn("ZIP_PAYLOAD_READ_OR_CRC_FAILED", result["findings"])

    def test_unreadable_zip_hold(self):
        result = inspect_zip(io.BytesIO(b"not a zip"))
        self.assertIn("ZIP_OPEN_FAILED", result["findings"])


if __name__ == "__main__":
    unittest.main()
