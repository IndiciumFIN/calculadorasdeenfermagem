"""WO de Drive submetida pelo Kernel: fail-closed e sem concessão implícita."""
import json
import os
import tempfile
import unittest
from pathlib import Path

from packages.cli.drive_work_order import (
    decide_work_order,
    human_authorization_exists,
    submit,
    write_work_order,
)


ROOTS = {
    "schema": "CE-DRIVE-ROOTS-1.0.0",
    "roots": [
        {"id": "root-master", "label": "CE_MASTER"},
    ],
    "restrictions": [
        "READ_ONLY",
        "NO_DELETE",
        "NO_PUBLICATION",
        "NO_CANONICAL_PROMOTION",
    ],
}

POLICY = {
    "id": "KERNEL-POLICY-001",
    "validators": ["atomo_schema_validator"],
    "wo_required": True,
    "requires_human_review": True,
    "atoms_output": "data/canonical/atoms/cofen/",
    "fail_closed": True,
}


class DriveWorkOrderTests(unittest.TestCase):
    def test_unregistered_folder_blocks_both_grants(self):
        for activity in ("obter", "atomizar"):
            decision = decide_work_order(
                activity=activity,
                folder_id="1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC",
                roots_doc=ROOTS,
                policy=None,
                credentials_ok=True,
                human_authorization=False,
            )
            self.assertEqual(decision["status"], "BLOQUEADO")
            self.assertNotEqual(decision["status"], "PREAUTHORIZED")
            self.assertFalse(decision["grants_download"])
            self.assertFalse(decision["grants_atomize"])
            self.assertIn("registry de raízes", decision["motivo"])

    def test_missing_credentials_block_download_of_registered_root(self):
        decision = decide_work_order(
            activity="obter",
            folder_id="root-master",
            roots_doc=ROOTS,
            policy=POLICY,
            credentials_ok=False,
            human_authorization=True,
        )
        self.assertEqual(decision["status"], "BLOQUEADO")
        self.assertFalse(decision["grants_download"])
        self.assertIn("credencial ausente", decision["motivo"])

    def test_canonical_promotion_blocks_atomize_even_with_human_wo(self):
        decision = decide_work_order(
            activity="atomizar",
            folder_id="root-master",
            roots_doc=ROOTS,
            policy=POLICY,
            credentials_ok=True,
            human_authorization=True,
        )
        self.assertEqual(decision["status"], "BLOQUEADO")
        self.assertFalse(decision["grants_atomize"])
        self.assertIn("NO_CANONICAL_PROMOTION", decision["motivo"])
        self.assertIn("revisão humana", decision["motivo"])

    def test_registered_obter_with_human_wo_is_recorded_not_preauthorized(self):
        decision = decide_work_order(
            activity="obter",
            folder_id="root-master",
            roots_doc=ROOTS,
            policy={**POLICY, "wo_required": True, "requires_human_review": False, "atoms_output": ""},
            credentials_ok=True,
            human_authorization=True,
        )
        self.assertEqual(decision["status"], "REGISTRADA")
        self.assertTrue(decision["grants_download"])
        self.assertFalse(decision["grants_atomize"])
        self.assertEqual(decision["authorized_by"], "KERNEL")

    def test_wo_required_without_human_authorization_blocks(self):
        decision = decide_work_order(
            activity="obter",
            folder_id="root-master",
            roots_doc=ROOTS,
            policy=POLICY,
            credentials_ok=True,
            human_authorization=False,
        )
        self.assertIn("não concede autorização", decision["motivo"])

    def test_rewrite_is_idempotent(self):
        decision = decide_work_order(
            activity="obter",
            folder_id="1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC",
            roots_doc=ROOTS,
            policy=None,
            credentials_ok=False,
            human_authorization=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            first, payload, changed = write_work_order(out, decision, ["probe"])
            second, again, changed_again = write_work_order(out, decision, ["probe"])
            self.assertTrue(changed)
            self.assertFalse(changed_again)
            self.assertEqual(first, second)
            self.assertEqual(payload, again)
            stored = json.loads(first.read_text(encoding="utf-8"))
            self.assertEqual(stored["status"], "BLOQUEADO")
            self.assertNotEqual(stored["status"], "PREAUTHORIZED")

    def test_human_file_must_mention_folder_and_not_kernel(self):
        with tempfile.TemporaryDirectory() as tmp:
            legado = Path(tmp)
            (legado / "autorizacao_WO-1.json").write_text(
                json.dumps({
                    "status": "PREAUTHORIZED",
                    "authorized_by": "KERNEL",
                    "folder_id": "root-master",
                }),
                encoding="utf-8",
            )
            self.assertFalse(human_authorization_exists("root-master", legado))
            (legado / "autorizacao_WO-2.json").write_text(
                json.dumps({
                    "status": "PREAUTHORIZED",
                    "authorized_by": "HUMAN_APPROVER",
                    "folder_id": "root-master",
                }) + "\n# comentario posterior\n",
                encoding="utf-8",
            )
            self.assertTrue(human_authorization_exists("root-master", legado))

    def test_submit_unknown_policy_exits_before_grant(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            roots = root / "roots.json"
            roots.write_text(json.dumps(ROOTS), encoding="utf-8")
            policies = root / "policies"
            policies.mkdir()
            with self.assertRaises(Exception):
                submit(
                    activity="atomizar",
                    folder_id="1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC",
                    roots_path=roots,
                    output_dir=root / "out",
                    policies_dir=policies,
                    policy_id="KERNEL-POLICY-999",
                    credentials_ok=False,
                )
            self.assertEqual(list((root / "out").glob("*.json")), [])

    def test_env_credentials_are_not_required_to_decide(self):
        previous_sa = os.environ.pop("GDRIVE_SA_KEY", None)
        previous_token = os.environ.pop("DRIVE_ACCESS_TOKEN", None)
        try:
            decision = decide_work_order(
                activity="obter",
                folder_id="root-master",
                roots_doc=ROOTS,
                policy=None,
                credentials_ok=False,
                human_authorization=False,
            )
        finally:
            if previous_sa is not None:
                os.environ["GDRIVE_SA_KEY"] = previous_sa
            if previous_token is not None:
                os.environ["DRIVE_ACCESS_TOKEN"] = previous_token
        self.assertEqual(decision["status"], "BLOQUEADO")


if __name__ == "__main__":
    unittest.main()
