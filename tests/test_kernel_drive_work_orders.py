"""WO de Drive submetida pelo Kernel: sem credencial não há download nem átomo."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "packages" / "cli"
for path in (str(ROOT), str(CLI)):
    if path not in sys.path:
        sys.path.insert(0, path)

from packages.cli.drive_recursive_inventory import CredentialError
from kernel.work_orders import execute_drive_folder

FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"


class DriveWorkOrderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="ce-wo-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def _run(self):
        def no_credential():
            raise CredentialError(
                "Neither GDRIVE_SA_KEY nor DRIVE_ACCESS_TOKEN is configured; fail closed."
            )

        return execute_drive_folder(
            FOLDER,
            self.root,
            token_loader=no_credential,
            http_probe=lambda _folder: 403,
        )

    def test_missing_credential_submits_blocked_work_orders(self):
        code = self._run()
        self.assertEqual(code, 2)
        legado = self.root / "data" / "legado"
        files = sorted(legado.glob("autorizacao_WO-*.json"))
        self.assertEqual(len(files), 2)
        tarefas = set()
        for path in files:
            data = json.loads(path.read_text(encoding="utf-8"))
            tarefas.add(data["tarefa"])
            self.assertEqual(data["submitted_by"], "kernel")
            self.assertEqual(data["estado"], "BLOQUEADO")
            self.assertEqual(data["status"], "BLOQUEADO")
            self.assertTrue(data["motivo"])
            self.assertIsNone(data["policy_id"])
            self.assertEqual(data["ultimo_http_code"], 403)
            self.assertIn("KERNEL-POLICY-001", data["politicas_validas_no_gate"])
            self.assertNotIn("KERNEL-POLICY-003", data["politicas_validas_no_gate"])
        self.assertEqual(tarefas, {"obter", "atomizar"})
        self.assertFalse((self.root / "data" / "canonical").exists())
        evidence = list((self.root / "evidence").glob("*/bloqueio.json"))
        self.assertEqual(len(evidence), 2)
        body = json.loads(evidence[0].read_text(encoding="utf-8"))
        self.assertEqual(body["bytes_baixados"], 0)
        self.assertEqual(body["atomos_escritos"], 0)

    def test_second_run_does_not_duplicate_work_orders(self):
        self._run()
        self._run()
        files = list((self.root / "data" / "legado").glob("autorizacao_WO-*.json"))
        self.assertEqual(len(files), 2)

    def test_invalid_folder_writes_nothing(self):
        code = execute_drive_folder("nao e um id", self.root, http_probe=lambda _f: 200)
        self.assertEqual(code, 2)
        self.assertFalse((self.root / "data").exists())


if __name__ == "__main__":
    unittest.main()
