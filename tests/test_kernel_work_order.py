"""WO do Kernel: fail-closed sem credencial e átomo só com política única."""
import json
import tempfile
import unittest
from pathlib import Path

from packages.cli.drive_recursive_inventory import CredentialError
from packages.cli.kernel.core import Kernel
from packages.cli.kernel.work_order import (
    assemble_wo,
    atomize_texts,
    canonical_id,
    parse_folder_id,
    run_obtain_drive,
    select_policy,
)


FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"


class WorkOrderTests(unittest.TestCase):
    def test_parse_folder_url(self):
        url = f"https://drive.google.com/drive/folders/{FOLDER}?hl=pt-br"
        self.assertEqual(parse_folder_id(url), FOLDER)

    def test_canonical_id_is_stable(self):
        legacy = "DRIVE-abc-SEG-0001"
        self.assertEqual(canonical_id(legacy, 2026), canonical_id(legacy, 2026))
        self.assertTrue(canonical_id(legacy, 2026).startswith("NORM-2026-"))

    def test_kernel_refuses_preauthorized(self):
        with self.assertRaises(ValueError):
            assemble_wo(
                folder_id=FOLDER,
                tarefa="obter",
                estado="PREAUTHORIZED",
                motivo=None,
                sha256_fonte=None,
                politicas_validas=[],
                politicas_rejeitadas=[],
                ultimo_http_code=None,
                entradas=0,
                ano_id=2026,
                evidence_reference="evidence/x.json",
                acao_necessaria="n/a",
            )

    def test_blocked_wo_requires_motivo(self):
        with self.assertRaises(ValueError):
            assemble_wo(
                folder_id=FOLDER,
                tarefa="obter",
                estado="BLOQUEADO",
                motivo=None,
                sha256_fonte=None,
                politicas_validas=[],
                politicas_rejeitadas=[],
                ultimo_http_code=403,
                entradas=0,
                ano_id=2026,
                evidence_reference="evidence/x.json",
                acao_necessaria="n/a",
            )

    def test_obtain_without_credential_is_fail_closed(self):
        def loader():
            raise CredentialError(
                "Neither GDRIVE_SA_KEY nor DRIVE_ACCESS_TOKEN is configured; fail closed."
            )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = run_obtain_drive(
                FOLDER,
                root=root,
                token_loader=loader,
                probe=lambda _folder: (403, "permission denied"),
            )
            self.assertEqual(code, 2)
            obter = json.loads(
                (root / "data" / "legado" / f"autorizacao_WO-DRIVE-{FOLDER}-obter.json").read_text()
            )
            atom = json.loads(
                (
                    root / "data" / "legado" / f"autorizacao_WO-DRIVE-{FOLDER}-atomizar.json"
                ).read_text()
            )
            self.assertEqual(obter["estado"], "BLOQUEADO")
            self.assertEqual(atom["estado"], "BLOQUEADO")
            self.assertIn("GDRIVE_SA_KEY", obter["motivo"])
            self.assertIsNone(obter["sha256_fonte"])
            self.assertIn("sha256_fonte", atom["motivo"])
            self.assertEqual(obter["authorized_by"], "kernel")
            self.assertEqual(obter["ultimo_http_code"], 403)
            self.assertFalse(any(path.suffix == ".json" for path in (root / "data").rglob("*.json") if "canonical" in path.parts))
            stamp = obter["timestamp"]
            again = run_obtain_drive(
                FOLDER,
                root=root,
                token_loader=loader,
                probe=lambda _folder: (403, "permission denied"),
            )
            self.assertEqual(again, 2)
            reread = json.loads(
                (root / "data" / "legado" / f"autorizacao_WO-DRIVE-{FOLDER}-obter.json").read_text()
            )
            self.assertEqual(reread["timestamp"], stamp)

    def test_ambiguous_policies_go_to_quarantine(self):
        kernel = Kernel()
        text = "Art. 5o O enfermeiro registra o procedimento no prontuario em ate 24 horas."
        with tempfile.TemporaryDirectory() as tmp:
            counts = atomize_texts(
                Path(tmp),
                [{"file_id": "f1", "fonte": "norma.txt", "sha256": "a" * 64, "texto": text}],
                wo_id="CE-WO-TEST-atomizar",
                ano=2026,
                policy_ids=[
                    "KERNEL-POLICY-001",
                    "KERNEL-POLICY-002",
                    "KERNEL-POLICY-019",
                    "KERNEL-POLICY-020",
                ],
                kernel=kernel,
            )
            self.assertEqual(counts["canonical"], 0)
            self.assertGreaterEqual(counts["quarentena"], 1)
            quarantine = Path(tmp) / "data" / "quarentena" / "sem_politica_unica" / "rejeicoes.jsonl"
            stored = quarantine.read_text(encoding="utf-8")
            self.assertIn("politica_ambigua_ou_rejeitada", stored)
            self.assertIn(text.strip(), stored)

    def test_single_policy_writes_canonical_atom(self):
        kernel = Kernel()
        text = "Art. 5o O enfermeiro registra o procedimento no prontuario em ate 24 horas."
        with tempfile.TemporaryDirectory() as tmp:
            counts = atomize_texts(
                Path(tmp),
                [{"file_id": "f1", "fonte": "norma.txt", "sha256": "b" * 64, "texto": text}],
                wo_id="CE-WO-TEST-atomizar",
                ano=2026,
                policy_ids=["KERNEL-POLICY-001"],
                kernel=kernel,
            )
            self.assertEqual(counts["canonical"], 1)
            atoms = list((Path(tmp) / "data" / "canonical" / "atoms" / "cofen").glob("*.json"))
            self.assertEqual(len(atoms), 1)
            payload = json.loads(atoms[0].read_text(encoding="utf-8"))
            self.assertEqual(payload["vigencia"], "NAO_VERIFICADO")
            self.assertTrue(payload["id_atomo"].startswith("NORM-2026-"))

    def test_select_policy_requires_exactly_one(self):
        item = {"id": 1}
        self.assertEqual(select_policy(item, ["A", "B"], lambda _item, policy: True), None)
        self.assertEqual(select_policy(item, ["A", "B"], lambda _item, policy: policy == "B"), "B")


if __name__ == "__main__":
    unittest.main()
