"""WO do Kernel antes de obter ou atomizar arquivos do Drive."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "packages" / "cli")]

from drive_recursive_inventory import CredentialError, FOLDER
from kernel.atomize import build_needles, classify_name
from kernel.core import Kernel
from kernel.drive_job import execute_drive_folder
from kernel.policy_registry import get_policy
from kernel.work_orders import WorkOrderRejected

FOLDER_ID = "folder-test-id"
ARTIGO = (
    "Art. 1º O enfermeiro executa o processo de enfermagem em todas as etapas "
    "do cuidado, inclusive quando o CPF 123.456.789-00 consta no prontuário institucional."
)


def test_gate_aceita_cofen_e_rejeita_politica_invalida():
    kernel = Kernel()
    assert kernel.gate("KERNEL-POLICY-001") == 0
    assert kernel.gate("KERNEL-POLICY-003") == 2
    assert get_policy("KERNEL-POLICY-001").quarentena_output == "data/quarentena/cofen/"


def test_kernel_nao_submete_wo_para_politica_rejeitada(tmp_path: Path):
    kernel = Kernel()
    with pytest.raises(WorkOrderRejected):
        kernel.submit_work_order(
            "KERNEL-POLICY-003",
            "atomizar",
            FOLDER_ID,
            rationale="não deve gravar",
            wo_dir=tmp_path,
        )
    assert list(tmp_path.glob("*.json")) == []


def test_classificacao_por_nome_nao_promove_politica_rejeitada():
    policies = Kernel().registry.list_policies()
    needles = build_needles(policies)
    valid = {"KERNEL-POLICY-001"}
    assert classify_name("cofen_dou_resolucao.txt", needles, valid)[0] == "KERNEL-POLICY-001"
    assert classify_name("cid10_categorias.csv", needles, valid)[1] == "POLICY_NOT_VALID"
    assert classify_name("cofen_portaria.txt", needles, valid)[1] == "POLICY_AMBIGUOUS"
    assert classify_name("nota_interna.txt", needles, valid)[1] == "UNMATCHED_POLICY"


def test_credencial_ausente_bloqueia_sem_atomos(tmp_path: Path):
    def sem_credencial():
        raise CredentialError(
            "Neither GDRIVE_SA_KEY nor DRIVE_ACCESS_TOKEN is configured; fail closed."
        )

    code = execute_drive_folder(
        FOLDER_ID,
        wo_dir=tmp_path / "wo",
        evidence_path=tmp_path / "evidence.json",
        dest_root=tmp_path / "dest",
        token_loader=sem_credencial,
    )
    assert code == 2
    evidence = json.loads((tmp_path / "evidence.json").read_text(encoding="utf-8"))
    assert evidence["atoms_written"] == 0
    assert evidence["download"]["status"] == "BLOQUEADO"
    assert "fail closed" in evidence["download"]["motivo"]
    statuses = {item["status"] for item in evidence["work_orders"]}
    assert statuses == {"BLOQUEADO"}
    assert all(
        json.loads(path.read_text(encoding="utf-8"))["authorized_by"] == "kernel"
        for path in (tmp_path / "wo").glob("*.json")
    )
    again = execute_drive_folder(
        FOLDER_ID,
        wo_dir=tmp_path / "wo",
        evidence_path=tmp_path / "evidence.json",
        dest_root=tmp_path / "dest",
        token_loader=sem_credencial,
    )
    assert again == 2
    assert len(list((tmp_path / "wo").glob("*.json"))) == len(evidence["work_orders"])
    assert list((tmp_path / "dest").rglob("NORM-*.json")) == []


def test_arquivo_classificado_e_atomizado_com_mascara(tmp_path: Path):
    def fetch(folder, token, page_token=None):
        if folder != FOLDER_ID:
            return {"files": []}
        return {
            "files": [
                {
                    "id": "filecofen1",
                    "name": "cofen_dou_resolucao.txt",
                    "mimeType": "text/plain",
                    "size": "180",
                },
                {
                    "id": "subpasta",
                    "name": "outras",
                    "mimeType": FOLDER,
                },
                {
                    "id": "nota1",
                    "name": "nota_interna.txt",
                    "mimeType": "text/plain",
                    "size": "20",
                },
            ]
        }

    def baixar(file_id, mime, token_getter):
        assert token_getter() == "token-teste"
        if file_id == "nota1":
            return b"texto solto sem dispositivo legal suficiente para virar atomo normativo."
        return ARTIGO.encode("utf-8")

    code = execute_drive_folder(
        FOLDER_ID,
        wo_dir=tmp_path / "wo",
        evidence_path=tmp_path / "evidence.json",
        dest_root=tmp_path / "dest",
        token_loader=lambda: (lambda: "token-teste"),
        fetcher=fetch,
        downloader=baixar,
    )
    assert code == 0
    atoms = list((tmp_path / "dest").rglob("NORM-*.json"))
    assert len(atoms) == 1
    atom = json.loads(atoms[0].read_text(encoding="utf-8"))
    assert atom["fonte_slug"] == "cofen_dou"
    assert atom["vigencia"] == "NAO_VERIFICADO"
    assert "[CPF_REDACT]" in atom["texto_regra"]
    assert "123.456.789-00" not in atom["texto_regra"]
    assert atom["wo_id"].startswith("CE-WO-")
    raw = (tmp_path / "dest" / "data" / "raw" / "drive" / FOLDER_ID / "filecofen1.txt").read_text(
        encoding="utf-8"
    )
    assert "123.456.789-00" not in raw
    evidence = json.loads((tmp_path / "evidence.json").read_text(encoding="utf-8"))
    cofen = [
        item
        for item in evidence["work_orders"]
        if item["policy_id"] == "KERNEL-POLICY-001" and item["activity"] == "atomizar"
    ]
    assert cofen[0]["status"] == "PASS"
    assert evidence["atoms_written"] == 1
