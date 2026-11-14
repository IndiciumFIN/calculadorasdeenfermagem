"""Negative tests of historical WO/Drive authorization regression.

Synthetic folder IDs and work orders ONLY. No request should access network,
write files, admit a WO, publish clinical data or claim G6 reviewer identity.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from packages.cli.kernel.wo_preflight import (
    git_blob_sha1, preflight, main,
)

FOLDER = "1FDBAMQ3-WT-8l6xU0664u7QjABd0FbEH"
POLICY_ID = "KERNEL-POLICY-001"
WO_PATH = Path("contracts/wo/WO-SYNTHETIC.json")


class WorkOrderG6PreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ce-wo-g6-tests-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.roots = {
            "schema": "CE-DRIVE-ROOTS-1.0.0",
            "scope": "registered_roots_metadata_only",
            "roots": [{"id": FOLDER}],
            "restrictions": ["READ_ONLY", "NO_DELETE", "NO_PUBLICATION", "NO_CANONICAL_PROMOTION"],
        }
        self.policy = {
            "id": POLICY_ID, "drive_folder_ids": [FOLDER],
            "fail_closed": True, "wo_required": True,
            "requires_human_review": True, "validators": ["atomo_schema_validator"],
        }
        self.wo = {
            "id": "WO-SYNTHETIC",
            "folder_id": FOLDER, "tarefa": "obter", "policy_id": POLICY_ID,
            "status": "DRAFT_NOT_ADMITTED", "task_id": "TASK-01",
            "find_ids": ["FIND-01"], "authorized_by": None,
        }
        self.save("config/drive_inventory_roots_20261016.json", self.roots)
        self.save("contracts/policies/KERNEL-POLICY-001.json", self.policy)
        self.save(str(WO_PATH), self.wo)

    def save(self, path, document):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(document, sort_keys=True), encoding="utf-8")

    def scan(self, **options):
        return preflight(
            self.root, options.get("wo_path", WO_PATH),
            folder_id=options.get("folder_id", FOLDER),
            activity=options.get("activity", "obter"),
            policy_id=options.get("policy_id", POLICY_ID),
        )

    def test_no_implicit_permission_even_when_every_field_matches(self):
        before = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*"))
        with patch("urllib.request.urlopen", side_effect=AssertionError("UNAUTHORIZED NETWORK")):
            result = self.scan()
        after = sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob("*"))
        self.assertEqual(before, after)
        self.assertEqual(result["status"], "HOLD")
        self.assertEqual(result["exit_code"], 2)
        self.assertTrue(result["technically_complete"])
        self.assertIn("SCOPE_METADATA_ONLY_NO_BYTES", result["findings"])
        self.assertIn("INDEPENDENT_KERNEL_ADMISSION_NOT_VERIFIED", result["findings"])
        self.assertIn("G6_CLINICAL_REVIEW_NOT_VERIFIED", result["findings"])
        self.assertFalse(result["network_used"])
        self.assertFalse(result["clinical_approval"])
        self.assertFalse(result["bytes_acquired"])
        self.assertIsNone(result["trusted_kernel_receipt"])

    def test_git_blob_sha_is_identical_to_git_object_algorithm(self):
        raw = (self.root / WO_PATH).read_bytes()
        expected = hashlib.sha1(
            b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw
        ).hexdigest()
        self.assertEqual(git_blob_sha1(raw), expected)
        self.assertEqual(self.scan()["object_git_blob_shas"]["wo"], expected)

    def test_description_mention_does_not_authorize_any_folder(self):
        self.wo["folder_id"] = "different-folder-999"
        self.wo["description"] = "Imported text says " + FOLDER
        self.save(str(WO_PATH), self.wo)
        self.assertIn("WO_FOLDER_NOT_BOUND", self.scan()["findings"])

    def test_unbound_policy_does_not_infer_from_description(self):
        self.policy.pop("drive_folder_ids")
        self.policy["description"] = "This policy mentions " + FOLDER
        self.save("contracts/policies/KERNEL-POLICY-001.json", self.policy)
        self.assertIn("NO_EXPLICIT_POLICY_FOLDER_BINDING", self.scan()["findings"])

    def test_self_asserted_review_and_authorization_are_rejected(self):
        self.wo.update({
            "status": "PREAUTHORIZED", "reviewed_by": "Dr Synthetic",
            "authorized_by": "Dr Synthetic",
            "approval_receipt": "fake-reviewer-signature",
        })
        self.save(str(WO_PATH), self.wo)
        result = self.scan()
        self.assertIn("WO_SELF_ASSERTED_AUTHORIZATION", result["findings"])
        self.assertIn("WO_SELF_ASSERTED_REVIEW_UNTRUSTED", result["findings"])
        self.assertFalse(result["clinical_approval"])

    def test_wrong_activity_and_wrong_policy_detected(self):
        self.wo["tarefa"] = "atomizar"
        self.wo["policy_id"] = "KERNEL-POLICY-999"
        self.save(str(WO_PATH), self.wo)
        result = self.scan()
        self.assertIn("WO_ACTIVITY_NOT_BOUND", result["findings"])
        self.assertIn("WO_POLICY_NOT_BOUND", result["findings"])

    def test_missing_task_find_links_block(self):
        self.wo.pop("task_id")
        self.wo.pop("find_ids")
        self.save(str(WO_PATH), self.wo)
        result = self.scan()
        self.assertIn("WO_TASK_NOT_BOUND", result["findings"])
        self.assertIn("WO_FIND_SCOPE_MISSING", result["findings"])

    def test_missing_and_corrupt_json_fail_closed(self):
        (self.root / WO_PATH).unlink()
        self.assertIn("WO_MISSING_OR_INVALID", self.scan()["findings"])
        target = self.root / WO_PATH
        target.write_text("{bad syntax", encoding="utf-8")
        self.assertIn("WO_MISSING_OR_INVALID", self.scan()["findings"])

    def test_path_escape_is_rejected(self):
        result = self.scan(wo_path=Path("../elsewhere/private.json"))
        self.assertIn("WO_UNSAFE_PATH", result["findings"])

    def test_symlink_outside_tree_is_rejected(self):
        outside = self.root.parent / (self.root.name + "-external-wo.json")
        outside.write_text(json.dumps(self.wo), encoding="utf-8")
        self.addCleanup(lambda: outside.unlink(missing_ok=True))
        (self.root / WO_PATH).unlink()
        (self.root / WO_PATH).symlink_to(outside)
        self.assertIn("WO_UNSAFE_PATH", self.scan()["findings"])

    def test_unsupported_folder_and_invalid_policy_id_fail_closed(self):
        report = self.scan(folder_id="INVALID!")
        self.assertIn("INVALID_FOLDER_ID", report["findings"])
        self.assertIn("ROOT_NOT_REGISTERED", report["findings"])
        report = self.scan(policy_id="../KERNEL-POLICY-001")
        self.assertIn("INVALID_POLICY_ID", report["findings"])

    def test_policy_cannot_opt_out_of_reviews_or_fail_closed(self):
        self.policy["fail_closed"] = False
        self.policy["wo_required"] = False
        self.policy["requires_human_review"] = False
        self.save("contracts/policies/KERNEL-POLICY-001.json", self.policy)
        findings = self.scan()["findings"]
        self.assertIn("POLICY_NOT_FAIL_CLOSED", findings)
        self.assertIn("POLICY_WO_NOT_REQUIRED", findings)
        self.assertIn("POLICY_REVIEW_NOT_REQUIRED", findings)

    def test_executed_claim_from_wo_is_untrusted(self):
        self.wo.update({"bytes_acquired": True, "atoms_emitted": 1})
        self.save(str(WO_PATH), self.wo)
        self.assertIn("WO_CLAIMS_EXECUTION_WITHOUT_ADMISSION", self.scan()["findings"])

    def test_cli_must_exit_two_even_with_complete_synthetic_candidate(self):
        code = main([
            "--repo-root", str(self.root), "--wo", str(WO_PATH),
            "--folder-id", FOLDER, "--activity", "obter",
            "--policy", POLICY_ID,
        ])
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
