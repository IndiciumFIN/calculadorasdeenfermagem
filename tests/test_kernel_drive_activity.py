"""O Kernel recusa obter/atomizar sem política, gate e credencial."""
import importlib.util
import json
import os
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO / "packages/cli/kernel/drive_activity.py"
TARGET_FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"


def load_module():
    spec = importlib.util.spec_from_file_location("kernel_drive_activity", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DriveActivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def _policy(self, **overrides):
        policy = {
            "id": "KERNEL-POLICY-001",
            "wo_required": True,
            "authorized_drive_folder_ids": [],
            "fail_closed": True,
        }
        policy.update(overrides)
        return policy

    def test_real_registry_rejects_target_folder_without_acquisition(self):
        policies = self.mod.load_policies(REPO)
        roots, restrictions = self.mod.load_roots(REPO)
        plan = self.mod.plan_drive_folder(
            folder_id=TARGET_FOLDER,
            policies=policies,
            registered_root_ids=roots,
            credential_configured=False,
            restrictions=restrictions,
        )
        self.assertEqual(plan["decision"], "REJECTED")
        self.assertEqual(plan["code"], "FOLDER_NOT_IN_POLICY")
        self.assertEqual(plan["exit_code"], 2)
        self.assertFalse(plan["bytes_acquired"])
        self.assertEqual(plan["atoms_written"], 0)
        self.assertFalse(plan["folder_is_registered_root"])
        self.assertGreaterEqual(len(plan["work_orders"]), 2)
        self.assertTrue(all(item["submitted_by"] == "kernel" for item in plan["work_orders"]))
        self.assertTrue(all(item["decision"] == "REJECTED" for item in plan["work_orders"]))
        self.assertFalse(self.mod.may_acquire(plan))
        self.assertIn("NO_CANONICAL_PROMOTION", plan["restrictions"])

    def test_registered_root_alone_does_not_authorize(self):
        plan = self.mod.plan_drive_folder(
            folder_id="root-folder-id",
            policies=[self._policy()],
            registered_root_ids=["root-folder-id"],
            credential_configured=True,
            gate_exit_by_policy={"KERNEL-POLICY-001": 0},
        )
        self.assertEqual(plan["code"], "FOLDER_NOT_IN_POLICY")
        self.assertTrue(plan["folder_is_registered_root"])
        self.assertFalse(self.mod.may_acquire(plan))

    def test_listed_folder_without_wo_flag_is_rejected(self):
        plan = self.mod.plan_drive_folder(
            folder_id=TARGET_FOLDER,
            policies=[self._policy(wo_required=False, authorized_drive_folder_ids=[TARGET_FOLDER])],
            registered_root_ids=[],
            credential_configured=True,
            gate_exit_by_policy={"KERNEL-POLICY-001": 0},
        )
        self.assertEqual({item["code"] for item in plan["work_orders"]}, {"POLICY_WO_NOT_REQUIRED"})
        self.assertFalse(self.mod.may_acquire(plan))

    def test_listed_folder_without_gate_is_rejected(self):
        plan = self.mod.plan_drive_folder(
            folder_id=TARGET_FOLDER,
            policies=[self._policy(authorized_drive_folder_ids=[TARGET_FOLDER])],
            registered_root_ids=[],
            credential_configured=True,
        )
        self.assertEqual({item["code"] for item in plan["work_orders"]}, {"GATE_NOT_RUN"})

    def test_gate_failure_and_missing_credential_block_acquisition(self):
        listed = self._policy(authorized_drive_folder_ids=[TARGET_FOLDER])
        failed = self.mod.plan_drive_folder(
            folder_id=TARGET_FOLDER,
            policies=[listed],
            registered_root_ids=[],
            credential_configured=True,
            gate_exit_by_policy={"KERNEL-POLICY-001": 2},
        )
        self.assertEqual({item["code"] for item in failed["work_orders"]}, {"POLICY_GATE_FAILED"})
        missing = self.mod.plan_drive_folder(
            folder_id=TARGET_FOLDER,
            policies=[listed],
            registered_root_ids=[],
            credential_configured=False,
            gate_exit_by_policy={"KERNEL-POLICY-001": 0},
        )
        self.assertEqual({item["code"] for item in missing["work_orders"]}, {"CREDENTIAL_ABSENT"})
        self.assertFalse(self.mod.may_acquire(missing))

    def test_unrelated_policy_does_not_veto_an_authorizing_policy(self):
        plan = self.mod.plan_drive_folder(
            folder_id=TARGET_FOLDER,
            policies=[
                self._policy(authorized_drive_folder_ids=[TARGET_FOLDER]),
                self._policy(id="KERNEL-POLICY-002"),
            ],
            registered_root_ids=[],
            credential_configured=True,
            gate_exit_by_policy={"KERNEL-POLICY-001": 0},
        )
        self.assertEqual(plan["decision"], "APPROVED")
        self.assertTrue(self.mod.may_acquire(plan))
        self.assertIn("FOLDER_NOT_IN_POLICY", {item["code"] for item in plan["work_orders"]})

    def test_submitted_plan_is_the_only_acquirable_state_and_writes_no_bytes(self):
        plan = self.mod.plan_drive_folder(
            folder_id=TARGET_FOLDER,
            policies=[self._policy(authorized_drive_folder_ids=[TARGET_FOLDER])],
            registered_root_ids=[],
            credential_configured=True,
            gate_exit_by_policy={"KERNEL-POLICY-001": 0},
        )
        self.assertEqual(plan["decision"], "APPROVED")
        self.assertTrue(self.mod.may_acquire(plan))
        self.assertFalse(plan["bytes_acquired"])
        self.assertEqual(plan["atoms_written"], 0)

    def test_malformed_folder_submits_nothing(self):
        plan = self.mod.plan_drive_folder(
            folder_id="../etc/passwd",
            policies=[self._policy(authorized_drive_folder_ids=["../etc/passwd"])],
            registered_root_ids=[],
            credential_configured=True,
            gate_exit_by_policy={"KERNEL-POLICY-001": 0},
        )
        self.assertEqual(plan["code"], "MALFORMED_FOLDER_ID")
        self.assertEqual(plan["work_orders"], [])

    def test_run_writes_evidence_inside_repo_and_exits_2(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            policies = root / "contracts/policies"
            policies.mkdir(parents=True)
            (policies / "KERNEL-POLICY-001.json").write_text(
                json.dumps({"id": "KERNEL-POLICY-001", "wo_required": True}),
                encoding="utf-8",
            )
            plan, code = self.mod.run_drive_folder(TARGET_FOLDER, root)
            evidence = root / "data/grc/evidencias" / f"kernel_drive_{TARGET_FOLDER}.json"
            self.assertEqual(code, 2)
            self.assertEqual(json.loads(evidence.read_text(encoding="utf-8"))["decision"], "REJECTED")
            self.assertEqual(plan["bytes_acquired"], False)
            self.assertFalse(any(root.joinpath("data/legado").glob("autorizacao_WO-*.json")))

    def test_authorizing_policy_still_does_not_download(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            policies = root / "contracts/policies"
            policies.mkdir(parents=True)
            (policies / "KERNEL-POLICY-001.json").write_text(
                json.dumps({
                    "id": "KERNEL-POLICY-001",
                    "wo_required": True,
                    "authorized_drive_folder_ids": [TARGET_FOLDER],
                }),
                encoding="utf-8",
            )
            previous = os.environ.get("GDRIVE_SA_KEY")
            os.environ["GDRIVE_SA_KEY"] = "configured"
            try:
                plan, code = self.mod.run_drive_folder(
                    TARGET_FOLDER,
                    root,
                    gate_exit_by_policy={"KERNEL-POLICY-001": 0},
                )
            finally:
                if previous is None:
                    os.environ.pop("GDRIVE_SA_KEY", None)
                else:
                    os.environ["GDRIVE_SA_KEY"] = previous
            self.assertEqual(code, 2)
            self.assertEqual(plan["code"], "ACQUISITION_NOT_ENABLED")
            self.assertFalse(plan["bytes_acquired"])
            self.assertEqual(plan["atoms_written"], 0)
            self.assertFalse(any(root.joinpath("data/legado").glob("autorizacao_WO-*.json")))

    def test_evidence_path_outside_repo_fails_closed(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            outside = Path(tmp) / "fora.json"
            root.mkdir()
            (root / "contracts/policies").mkdir(parents=True)
            with self.assertRaises(RuntimeError):
                self.mod.run_drive_folder(TARGET_FOLDER, root, outside)


if __name__ == "__main__":
    unittest.main()
