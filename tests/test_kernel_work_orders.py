"""WO do Kernel antes de baixar ou atomizar uma pasta Drive."""
import json
import unittest
from pathlib import Path

from packages.cli.kernel.work_orders import run_activity, submit_work_order

FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
ROOT = Path(__file__).resolve().parents[1]


def _allow_credentials():
    return True, "credencial de teste"


def _allow_gate():
    return True, "gate de teste"


class KernelWorkOrderTests(unittest.TestCase):
    def test_real_folder_is_blocked_without_download(self):
        before = list((ROOT / "data").rglob("*"))
        code, decision = submit_work_order(activity="obter", folder_id=FOLDER, repo_root=ROOT)
        self.assertEqual(code, 2)
        self.assertEqual(decision["status"], "BLOQUEADO")
        self.assertEqual(decision["submitted_by"], "kernel")
        self.assertFalse(decision["bytes_acquired"])
        self.assertFalse(decision["canonical_promoted"])
        self.assertIn("raízes registradas", decision["motivo"])
        self.assertIn("nenhuma política", decision["motivo"])
        self.assertTrue((ROOT / "data" / "legado" / f"autorizacao_{decision['wo_id']}.json").is_file())
        created = [p for p in (ROOT / "data").rglob("*") if p not in before and p.suffix == ".json"]
        self.assertTrue(all("autorizacao_" in p.name for p in created))

    def test_atomize_real_folder_blocked(self):
        code, decision = submit_work_order(activity="atomizar", folder_id=FOLDER, repo_root=ROOT)
        self.assertEqual(code, 2)
        self.assertIn("bytes não adquiridos", decision["motivo"])
        self.assertFalse((ROOT / "data" / "canonical").exists())

    def test_activity_reruns_kernel_decision(self):
        code, decision = run_activity(activity="obter", folder_id=FOLDER, repo_root=ROOT)
        self.assertEqual(code, 2)
        self.assertFalse(decision["executed"])

    def test_same_decision_keeps_timestamp(self):
        first, _ = submit_work_order(activity="obter", folder_id=FOLDER, repo_root=ROOT)
        path = ROOT / "data" / "legado" / f"autorizacao_CE-WO-DRIVE-{FOLDER}-OBTER.json"
        stamp = json.loads(path.read_text(encoding="utf-8"))["timestamp"]
        second, again = submit_work_order(activity="obter", folder_id=FOLDER, repo_root=ROOT)
        self.assertEqual(first, 2)
        self.assertEqual(second, 2)
        self.assertEqual(again["timestamp"], stamp)

    def test_unknown_activity_rejected(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "contracts" / "policies").mkdir(parents=True)
            (root / "config").mkdir()
            (root / "contracts" / "policies" / "KERNEL-POLICY-003.json").write_text(
                json.dumps({"id": "KERNEL-POLICY-003", "fail_closed": True, "validators": ["schema_validator"]}),
                encoding="utf-8",
            )
            (root / "config" / "drive_inventory_roots_20261016.json").write_text(
                json.dumps({"roots": [{"id": "1FDBAMQ3-WT-8l6xU0664u7QjABd0FbEH"}]}),
                encoding="utf-8",
            )
            code, decision = submit_work_order(activity="publicar", folder_id=FOLDER, repo_root=root)
        self.assertEqual(code, 2)
        self.assertIn("atividade desconhecida", decision["motivo"])
        self.assertEqual(list((ROOT / "data" / "legado").glob("autorizacao_CE-WO-DRIVE-*-REJEITADA.json")), [])

    def test_explicit_policy_can_authorize_without_executing(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "contracts" / "policies").mkdir(parents=True)
            (root / "config").mkdir()
            policy = {
                "id": "KERNEL-POLICY-003",
                "fail_closed": True,
                "drive_folder_ids": ["pastaautorizada1"],
                "requires_human_review": False,
                "wo_required": False,
                "validators": ["schema_validator"],
            }
            (root / "contracts" / "policies" / "KERNEL-POLICY-003.json").write_text(
                json.dumps(policy), encoding="utf-8"
            )
            (root / "config" / "drive_inventory_roots_20261016.json").write_text(
                json.dumps({"roots": [{"id": "pastaautorizada1"}]}), encoding="utf-8"
            )
            code, decision = submit_work_order(
                activity="obter",
                folder_id="pastaautorizada1",
                repo_root=root,
                credential_check=_allow_credentials,
                validator_gate=_allow_gate,
            )
            self.assertEqual(code, 0)
            self.assertEqual(decision["status"], "AUTORIZADA")
            run_code, run = run_activity(
                activity="obter",
                folder_id="pastaautorizada1",
                repo_root=root,
                credential_check=_allow_credentials,
                validator_gate=_allow_gate,
            )
            self.assertEqual(run_code, 2)
            self.assertFalse(run["executed"])
            self.assertFalse((root / "data" / "canonical").exists())


if __name__ == "__main__":
    unittest.main()
