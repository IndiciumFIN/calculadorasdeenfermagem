"""WO do Kernel para obter e atomizar uma pasta Drive. Fail-closed."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "cli"))
sys.path.insert(1, str(ROOT))

from kernel.work_orders import run_activity, submit_work_order  # noqa: E402

FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
OTHER = "1c9vErI_It3XwzAcAFOnbxw9V0Mn6xfB9"


def _gate_ok(_policy_id: str) -> tuple[bool, str]:
    return True, "ok"


class KernelWorkOrderTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="ce-wo-")
        self.root = Path(self._tmp.name)
        (self.root / "contracts" / "policies").mkdir(parents=True)
        (self.root / "config").mkdir()
        (self.root / "data" / "legado").mkdir(parents=True)
        policy = {
            "id": "KERNEL-POLICY-001",
            "fail_closed": True,
            "validators": ["texto_length_validator"],
            "atoms_output": "data/canonical/atoms/cofen/",
            "quarentena_output": "data/quarentena/cofen/",
            "source_contract": "contracts/fontes/cofen_dou.json",
        }
        (self.root / "contracts" / "policies" / "KERNEL-POLICY-001.json").write_text(
            json.dumps(policy), encoding="utf-8"
        )
        roots = {
            "roots": [{"id": OTHER, "label": "CE_SITE"}],
            "restrictions": ["READ_ONLY", "NO_DELETE", "NO_PUBLICATION", "NO_CANONICAL_PROMOTION"],
        }
        (self.root / "config" / "drive_inventory_roots_20261016.json").write_text(
            json.dumps(roots), encoding="utf-8"
        )
        self.calls = []

    def tearDown(self):
        self._tmp.cleanup()

    def test_unregistered_folder_is_blocked_without_download(self):
        def downloader(folder_id, dest):
            self.calls.append(folder_id)
            return []

        code, decision = run_activity(
            activity="obter",
            folder_id=FOLDER,
            repo_root=self.root,
            credential_check=lambda: (False, "credencial ausente"),
            validator_gate=_gate_ok,
            downloader=downloader,
        )
        self.assertEqual(code, 2)
        self.assertEqual(decision["status"], "BLOQUEADO")
        self.assertEqual(decision["submitted_by"], "kernel")
        self.assertFalse(decision["executed"])
        self.assertFalse(decision["bytes_acquired"])
        self.assertEqual(self.calls, [])
        self.assertFalse((self.root / "data" / "raw").exists())
        self.assertTrue((self.root / "data" / "legado" / f"autorizacao_{decision['wo_id']}.json").is_file())

    def test_atomize_blocked_when_obter_is_blocked(self):
        run_activity(
            activity="obter",
            folder_id=FOLDER,
            repo_root=self.root,
            credential_check=lambda: (False, "credencial ausente"),
            validator_gate=_gate_ok,
        )
        code, decision = run_activity(
            activity="atomizar",
            folder_id=FOLDER,
            repo_root=self.root,
            credential_check=lambda: (True, "ok"),
            validator_gate=_gate_ok,
            texts=[{"text": "Art. 1 O enfermeiro registra o procedimento no prontuário.", "origin": "local"}],
        )
        self.assertEqual(code, 2)
        self.assertEqual(decision["status"], "BLOQUEADO")
        self.assertEqual(decision["atoms_written"], 0)
        self.assertFalse(list((self.root / "data").rglob("NORM-*.json")))

    def test_authorized_obter_uses_downloader_and_not_canonical(self):
        roots = {
            "roots": [{"id": FOLDER, "label": "LOTE"}],
            "restrictions": ["READ_ONLY"],
        }
        (self.root / "config" / "drive_inventory_roots_20261016.json").write_text(
            json.dumps(roots), encoding="utf-8"
        )
        (self.root / "data" / "legado" / "drive_raizes.json").write_text("{}", encoding="utf-8")
        policy = json.loads((self.root / "contracts" / "policies" / "KERNEL-POLICY-001.json").read_text())
        policy["drive_folder_ids"] = [FOLDER]
        policy["atoms_output"] = "data/staging/atoms/"
        (self.root / "contracts" / "policies" / "KERNEL-POLICY-001.json").write_text(
            json.dumps(policy), encoding="utf-8"
        )

        def downloader(folder_id, dest):
            self.calls.append((folder_id, str(dest)))
            target = dest / "norma.txt"
            target.write_text("Art. 2 O registro é obrigatório antes do fim do plantão.", encoding="utf-8")
            return [{"name": "norma.txt", "sha256": "abc"}]

        code, decision = run_activity(
            activity="obter",
            folder_id=FOLDER,
            repo_root=self.root,
            credential_check=lambda: (True, "ok"),
            validator_gate=_gate_ok,
            downloader=downloader,
        )
        self.assertEqual(code, 0)
        self.assertEqual(decision["status"], "AUTORIZADA")
        self.assertTrue(decision["executed"])
        self.assertEqual(len(self.calls), 1)
        self.assertTrue((self.root / "data" / "raw" / "drive" / FOLDER / "norma.txt").is_file())
        self.assertFalse((self.root / "data" / "canonical").exists())

    def test_authorized_atomize_keeps_unverified_status(self):
        roots = {"roots": [{"id": FOLDER, "label": "LOTE"}], "restrictions": []}
        (self.root / "config" / "drive_inventory_roots_20261016.json").write_text(
            json.dumps(roots), encoding="utf-8"
        )
        (self.root / "data" / "legado" / "drive_raizes.json").write_text("{}", encoding="utf-8")
        policy = json.loads((self.root / "contracts" / "policies" / "KERNEL-POLICY-001.json").read_text())
        policy["drive_folder_ids"] = [FOLDER]
        policy["atoms_output"] = "data/staging/atoms/"
        (self.root / "contracts" / "policies" / "KERNEL-POLICY-001.json").write_text(
            json.dumps(policy), encoding="utf-8"
        )
        run_activity(
            activity="obter",
            folder_id=FOLDER,
            repo_root=self.root,
            credential_check=lambda: (True, "ok"),
            validator_gate=_gate_ok,
            downloader=lambda folder_id, dest: [{"name": "norma.txt"}],
        )
        code, decision = run_activity(
            activity="atomizar",
            folder_id=FOLDER,
            repo_root=self.root,
            credential_check=lambda: (True, "ok"),
            validator_gate=_gate_ok,
            texts=[{
                "text": "Art. 3 A dose é registrada em miligramas no prontuário do paciente.",
                "origin": "norma.txt",
            }],
        )
        self.assertEqual(code, 0)
        self.assertEqual(decision["atoms_written"], 1)
        self.assertFalse(decision["canonical_promoted"])
        atoms = list((self.root / "data" / "staging" / "atoms").glob("*.json"))
        self.assertEqual(len(atoms), 1)
        payload = json.loads(atoms[0].read_text(encoding="utf-8"))
        self.assertEqual(payload["vigencia"], "NAO_VERIFICADO")
        self.assertTrue(payload["id_atomo"].startswith("NORM-"))


if __name__ == "__main__":
    unittest.main()
