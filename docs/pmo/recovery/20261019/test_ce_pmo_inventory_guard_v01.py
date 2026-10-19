"""Adversarial fail-closed tests for CE inventory documentary guard."""
import copy
import json
import io
import unittest
import zipfile
from pathlib import Path

from ce_pmo_inventory_guard_v01 import preflight

ROOT = Path(__file__).resolve().parent


class InventoryGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pmo = json.loads((ROOT / "CE_PMO_REGISTRO_MESTRE_20261019_v0.1.0_CANDIDATE.json").read_text())
        cls.summary = json.loads((ROOT / "CE_PMO_INVENTARIO_RECURSIVO_RESUMO_20261019_CANDIDATE.json").read_text())
        cls.manifest = {"root_scope": "recursive_workspace_only", "files": [{"relative_path": "sample.txt", "sha256": "a" * 64, "bytes": 2, "external_persistence": "NOT_PROVEN_BY_LOCAL_SCAN"}]}
        cls.plan = {"branch": "pmo/recovery-controlled-20261019", "operations": [{"action": "create", "path": "docs/pmo/recovery/20261019/sample.md", "sha256_local": "b" * 64, "readback_required": True}]}

    def assert_block(self, domain, modified, expected):
        self.assertTrue(any(expected in issue for issue in preflight(**{domain: modified})))

    def test_valid_preflight_not_release(self):
        self.assertEqual([], preflight(manifest=self.manifest, summary=self.summary, pmo=self.pmo, publication=self.plan))

    def test_false_pass(self):
        x = copy.deepcopy(self.pmo)
        x["pmo_trusted"] = True
        self.assert_block("pmo", x, "PMO_FALSE_PASS")

    def test_m24_release(self):
        x = copy.deepcopy(self.pmo)
        x["populations"] = [v for v in x["populations"] if v["population_id"] != "POP-M24-HOLD"]
        self.assert_block("pmo", x, "M24_POPULATION_RELEASED")

    def test_gate_false_pass(self):
        x = copy.deepcopy(self.pmo)
        x["gates"][0]["status"] = "PASS"
        self.assert_block("pmo", x, "GATE_FALSE_PASS")

    def test_delete_blocked(self):
        x = copy.deepcopy(self.plan)
        x["operations"][0]["action"] = "deduplicate_delete"
        self.assert_block("publication", x, "DESTRUCTIVE_OR_UNKNOWN_ACTION")

    def test_main_blocked(self):
        x = copy.deepcopy(self.plan)
        x["branch"] = "main"
        self.assert_block("publication", x, "UNAUTHORIZED_TARGET_BRANCH")

    def test_upload_path_blocked(self):
        x = copy.deepcopy(self.plan)
        x["operations"][0]["path"] = "docs/pmo/recovery/20261019/upload/private_manifest.json"
        self.assert_block("publication", x, "PRIVATE_PATH_PUBLICATION")

    def test_readback_required(self):
        x = copy.deepcopy(self.plan)
        x["operations"][0]["readback_required"] = False
        self.assert_block("publication", x, "READBACK_REQUIRED")

    def test_base_sha_required_for_update(self):
        x = copy.deepcopy(self.plan)
        x["operations"][0]["action"] = "update"
        self.assert_block("publication", x, "CAS_BASE_SHA_REQUIRED")

    def test_hash_missing(self):
        x = copy.deepcopy(self.manifest)
        del x["files"][0]["sha256"]
        self.assert_block("manifest", x, "HASH_MISSING_OR_INVALID")

    def test_duplicate_inventory_path(self):
        x = copy.deepcopy(self.manifest)
        x["files"].append(copy.deepcopy(x["files"][0]))
        self.assert_block("manifest", x, "DUPLICATE_MANIFEST_PATH")

    def test_false_custody(self):
        x = copy.deepcopy(self.manifest)
        x["files"][0]["external_persistence"] = "LIBRARY_VERIFIED"
        self.assert_block("manifest", x, "FALSE_CUSTODY_CLAIM")

    def test_summary_private_hash(self):
        x = copy.deepcopy(self.summary)
        x["sha256"] = "a" * 64
        self.assert_block("summary", x, "PRIVATE_FIELD_IN_PUBLIC_SUMMARY")

    def test_zip_traversal(self):
        target = io.BytesIO()
        with zipfile.ZipFile(target, "w") as arc:
            arc.writestr("../escape.txt", "data")
        target.seek(0)
        self.assert_block("archives", [target], "ZIP_PATH_TRAVERSAL")

    def test_zip_safe(self):
        target = io.BytesIO()
        with zipfile.ZipFile(target, "w") as arc:
            arc.writestr("safe/document.txt", "data")
        target.seek(0)
        self.assertEqual([], preflight(archives=[target]))


if __name__ == "__main__":
    unittest.main()
