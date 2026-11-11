"""WO de Drive só segue depois que o Kernel submete e autoriza."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from packages.cli.kernel.work_orders import run_drive_folder

FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
REPO = Path(__file__).resolve().parents[1]
NOW = "2026-11-11T15:50:00Z"
LINE = (
    "Art. 1º O enfermeiro registra o cuidado conforme a fonte oficial "
    "https://www.in.gov.br/web/dou/-/resolucao-cofen-801"
)


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _authorized_repo(root: Path, folder: str) -> None:
    _write(root / "config/drive_inventory_roots_20261016.json", {
        "schema": "CE-DRIVE-ROOTS-1.0.0",
        "scope": "registered_roots",
        "roots": [{"id": folder, "label": "FONTE"}],
        "restrictions": ["NO_DELETE"],
    })
    _write(root / "data/legado/drive_raizes.json", {
        "roots": [{"id": folder, "label": "FONTE"}],
    })
    _write(root / "contracts/fontes/cofen_dou.json", {
        "fonte_slug": "cofen_dou",
        "source_contract": "contracts/fontes/cofen_dou.json",
    })
    _write(root / "contracts/policies/KERNEL-POLICY-001.json", {
        "id": "KERNEL-POLICY-001",
        "source_contract": "contracts/fontes/cofen_dou.json",
        "validators": [
            "atomo_schema_validator",
            "norm_atom_id_validator",
            "texto_length_validator",
            "url_validator",
        ],
        "atoms_output": "data/canonical/atoms/cofen/",
        "quarentena_output": "data/quarentena/cofen/",
        "drive_folder_ids": [folder],
        "wo_required": True,
    })


class KernelDriveWorkOrderTests(unittest.TestCase):
    def _live_copy(self) -> Path:
        tmp = tempfile.TemporaryDirectory(prefix="ce-wo-")
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        shutil.copytree(REPO / "contracts" / "policies", root / "contracts" / "policies")
        target = root / "config/drive_inventory_roots_20261016.json"
        target.parent.mkdir(parents=True)
        shutil.copy(REPO / "config/drive_inventory_roots_20261016.json", target)
        return root

    def test_live_folder_is_blocked_without_touching_acquire(self):
        calls = []

        def acquire(folder_id):
            calls.append(folder_id)
            raise AssertionError("Drive não pode ser chamado")

        root = self._live_copy()
        result = run_drive_folder(
            FOLDER,
            repo=root,
            now=NOW,
            credential_present_flag=False,
            acquire=acquire,
        )
        self.assertEqual(result["exit_code"], 2)
        self.assertFalse(result["bytes_acquired"])
        self.assertEqual(result["atoms_written"], 0)
        self.assertFalse(result["folder_in_registered_roots"])
        self.assertEqual(result["policies_authorizing_folder"], [])
        self.assertEqual(calls, [])
        estados = {order["tarefa"]: order["estado"] for order in result["orders"]}
        self.assertEqual(estados, {"obter": "BLOQUEADO", "atomizar": "BLOQUEADO"})
        for order in result["orders"]:
            self.assertEqual(order["submitted_by"], "kernel")
            self.assertIsNone(order["autorizado_por"])
        evidence = json.loads(
            (root / "data/grc/evidencias" / f"drive_{FOLDER}.json").read_text(encoding="utf-8")
        )
        self.assertEqual(evidence["submitted_by"], "kernel")
        self.assertFalse(evidence["bytes_acquired"])

    def test_metadata_only_root_does_not_acquire_bytes(self):
        tmp = tempfile.TemporaryDirectory(prefix="ce-wo-meta-")
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        folder = "pasta-autorizada-teste-01"
        _authorized_repo(root, folder)
        roots = json.loads((root / "config/drive_inventory_roots_20261016.json").read_text())
        roots["scope"] = "registered_roots_metadata_only"
        roots["restrictions"] = ["READ_ONLY", "NO_CANONICAL_PROMOTION"]
        _write(root / "config/drive_inventory_roots_20261016.json", roots)
        calls = []
        result = run_drive_folder(
            folder,
            repo=root,
            policy_id="KERNEL-POLICY-001",
            credential_present_flag=True,
            now=NOW,
            acquire=lambda folder_id: calls.append(folder_id) or [],
        )
        self.assertEqual(calls, [])
        self.assertEqual(result["orders"][0]["estado"], "BLOQUEADO")
        self.assertIn("somente metadados", result["orders"][0]["motivo"])

    def test_authorized_policy_atomizes_without_inferring_another_policy(self):
        tmp = tempfile.TemporaryDirectory(prefix="ce-wo-ok-")
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        folder = "pasta-autorizada-teste-02"
        _authorized_repo(root, folder)

        def acquire(folder_id):
            self.assertEqual(folder_id, folder)
            return [{
                "id": "file-1",
                "name": "norma.txt",
                "mime_type": "text/plain",
                "error": None,
                "data": (LINE + "\ncurto\n").encode("utf-8"),
            }]

        result = run_drive_folder(
            folder,
            repo=root,
            policy_id="KERNEL-POLICY-001",
            credential_present_flag=True,
            now=NOW,
            acquire=acquire,
        )
        self.assertTrue(result["bytes_acquired"])
        self.assertEqual(result["atoms_written"], 1)
        self.assertEqual(result["exit_code"], 0)
        atoms = list((root / "data/canonical/atoms/cofen").glob("*.json"))
        self.assertEqual(len(atoms), 1)
        atom = json.loads(atoms[0].read_text(encoding="utf-8"))
        self.assertEqual(atom["vigencia"], "NAO_VERIFICADO")
        self.assertEqual(atom["wo_id"], f"CE-WO-ATOMIZAR-{folder}")
        quarantine = (root / "data/quarentena/cofen/validacao_invalida.jsonl").read_text(encoding="utf-8")
        self.assertIn("texto_curto", quarantine)
