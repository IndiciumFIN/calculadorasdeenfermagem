"""Kernel admite pasta Drive só com WO e falha fechada."""
import json
import shutil
import unittest
from pathlib import Path

from packages.cli.drive_admission import (
    admit_drive_folder,
    official_url_domains,
    write_admission,
)

REAL = Path(__file__).resolve().parents[1]
FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
PROBE_LOGIN = {
    "folder_http_status": 302,
    "folder_redirect_host": "accounts.google.com",
    "api_http_status": 403,
    "api_status": "PERMISSION_DENIED",
}


def stage(tmp: Path) -> Path:
    for rel in (
        "contracts/policies",
        "contracts/fontes",
        "config/drive_inventory_roots_20261016.json",
        "packages/cli/validators/sha256_validator.py",
    ):
        src = REAL / rel
        dest = tmp / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy(src, dest)
    return tmp


class DriveAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(self.id().replace(".", "_"))
        # unittest id is not a directory; use TemporaryDirectory via addCleanup
        import tempfile
        self.dir = tempfile.TemporaryDirectory(prefix="ce-drive-admit-")
        self.addCleanup(self.dir.cleanup)
        self.root = stage(Path(self.dir.name))

    def admit(self, folder=FOLDER, env=None, probe=None):
        return admit_drive_folder(
            folder,
            root=self.root,
            env={} if env is None else env,
            probe=PROBE_LOGIN if probe is None else probe,
        )

    def test_unregistered_folder_submits_blocked_work_orders(self):
        admission = self.admit()
        self.assertEqual(admission.exit_code, 2)
        self.assertEqual(len(admission.work_orders), 2)
        tasks = [order["tarefa"] for order in admission.work_orders]
        self.assertEqual(tasks, ["obter", "atomizar"])
        for order in admission.work_orders:
            self.assertEqual(order["submitted_by"], "kernel")
            self.assertIsNone(order["authorized_by"])
            self.assertEqual(order["status"], "BLOQUEADO")
            self.assertFalse(order["bytes_acquired"])
            self.assertFalse(order["canonical_promoted"])
            self.assertEqual(order["atoms_written"], 0)
            self.assertIsNone(order["policy_id"])
        obter = admission.work_orders[0]["motivos"]
        for code in (
            "UNREGISTERED_ROOT",
            "MISSING_CREDENTIAL",
            "DRIVE_LOGIN_REQUIRED",
            "DRIVE_API_FORBIDDEN",
            "NO_MATCHING_POLICY",
            "METADATA_ONLY_SCOPE",
            "NO_CANONICAL_PROMOTION",
        ):
            self.assertIn(code, obter)
        self.assertNotIn("ATOMIC_SOURCE_ABSENT", obter)
        self.assertIn("ATOMIC_SOURCE_ABSENT", admission.work_orders[1]["motivos"])
        self.assertFalse((self.root / "data" / "canonical").exists())

    def test_write_is_idempotent_and_valid_json(self):
        first = self.admit()
        write_admission(self.root, first)
        second = self.admit()
        paths = write_admission(self.root, second)
        self.assertEqual(second.evidence["attempt_count"], 2)
        self.assertEqual(second.evidence["first_submitted_at"], first.evidence["first_submitted_at"])
        for path in paths:
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn(payload["schema"], {"CE-WO-AUTHORIZATION-1.0.0", "CE-DRIVE-ADMISSION-1.0.0"})
        self.assertEqual(list((self.root / "data" / "canonical").rglob("*.json")), [])

    def test_registered_root_still_blocks_without_matching_policy(self):
        roots = self.root / "config/drive_inventory_roots_20261016.json"
        document = json.loads(roots.read_text(encoding="utf-8"))
        document["roots"].append({"id": FOLDER, "label": "PEDIDO"})
        roots.write_text(json.dumps(document), encoding="utf-8")
        admission = self.admit(
            env={"GDRIVE_SA_KEY": "present"},
            probe={
                "folder_http_status": 200,
                "folder_redirect_host": None,
                "api_http_status": 200,
                "api_status": None,
            },
        )
        self.assertEqual(admission.exit_code, 2)
        self.assertTrue(admission.evidence["gates"]["registered_root"])
        self.assertTrue(admission.evidence["gates"]["credential_present"])
        self.assertTrue(admission.evidence["gates"]["drive_identity_established"])
        self.assertFalse(admission.evidence["gates"]["matching_policy"])
        self.assertFalse(admission.evidence["bytes_acquired"])
        self.assertIn("NO_MATCHING_POLICY", admission.work_orders[0]["motivos"])
        self.assertIn("METADATA_ONLY_SCOPE", admission.work_orders[0]["motivos"])
        self.assertIn("NO_CANONICAL_PROMOTION", admission.work_orders[0]["motivos"])

    def test_invalid_folder_id_fails_closed(self):
        admission = self.admit(folder="../segredo", probe={})
        self.assertEqual(admission.exit_code, 2)
        self.assertIn("INVALID_FOLDER_ID", admission.work_orders[0]["motivos"])
        self.assertNotIn("UNREGISTERED_ROOT", admission.work_orders[0]["motivos"])

    def test_drive_domain_is_outside_official_allowlist(self):
        domains = official_url_domains(self.root)
        self.assertIn("www.in.gov.br", domains)
        self.assertNotIn("drive.google.com", domains)
        self.assertTrue(all(item["admitted"] is False for item in self.admit().evidence["policies"]))


if __name__ == "__main__":
    unittest.main()
