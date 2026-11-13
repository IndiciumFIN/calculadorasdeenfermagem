"""WO do Kernel, gate e atomização da pasta Drive — sem rede."""
import json
from pathlib import Path

import pytest

from packages.cli.drive_atomize import (
    atomize_document,
    matching_policies,
    run_drive_job,
    select_policy,
)
from packages.cli.drive_recursive_inventory import CredentialError
from packages.cli.kernel.work_orders import assess_all_policies, submit_work_order

FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
SOURCE = f"https://drive.google.com/drive/folders/{FOLDER}?hl=pt-br"
COFEN = """COFEN

Art. 1º O enfermeiro realiza a consulta de enfermagem em 2024 na rede de atenção à saúde conforme protocolo institucional.

Art. 3 x
"""


def test_gate_aprova_somente_politicas_com_suite_real():
    gate = assess_all_policies()
    assert gate["valid_policy_ids"] == [
        "KERNEL-POLICY-001",
        "KERNEL-POLICY-002",
        "KERNEL-POLICY-019",
        "KERNEL-POLICY-020",
    ]
    reasons = {item["policy_id"]: item["reason"] for item in gate["results"]}
    assert reasons["KERNEL-POLICY-003"].startswith("test_suite reprovou")


def test_classificacao_deterministica():
    assert matching_policies(COFEN, "resolucao.pdf") == ["KERNEL-POLICY-001"]
    ambiguous = "O COFEN e a ANVISA publicam atos conjuntos."
    assert matching_policies(ambiguous, "ato.txt") == [
        "KERNEL-POLICY-001",
        "KERNEL-POLICY-002",
    ]
    assert select_policy(ambiguous, "ato.txt", {"KERNEL-POLICY-001", "KERNEL-POLICY-002"}) is None
    assert select_policy("texto sem órgão oficial reconhecido", "nota.txt", {"KERNEL-POLICY-001"}) is None


def test_atomiza_cofen_e_quarentena_curta():
    atoms, rejected = atomize_document(
        text=COFEN,
        file_id="arquivo1",
        file_name="resolucao.pdf",
        policy_id="KERNEL-POLICY-001",
        fonte_slug="cofen_dou",
        wo_id="CE-WO-DRIVE-TESTE-ATOMIZAR",
        link_fonte="https://www.in.gov.br/web/dou/-/resolucao-cofen-736",
        year_fallback=2026,
    )
    assert len(atoms) == 1
    assert atoms[0]["vigencia"] == "NAO_VERIFICADO"
    assert atoms[0]["id_atomo"].startswith("NORM-2024-")
    assert atoms[0]["wo_id"] == "CE-WO-DRIVE-TESTE-ATOMIZAR"
    assert atoms[0]["link_fonte"].startswith("https://www.in.gov.br/")
    assert any(row["motivo"] == "texto_curto" for row in rejected)


def test_sem_credencial_bloqueia_e_nao_grava_atomo(tmp_path: Path):
    def token_loader():
        raise CredentialError("Neither GDRIVE_SA_KEY nor DRIVE_ACCESS_TOKEN is configured; fail closed.")

    def fetch(*_args, **_kwargs):
        raise AssertionError("não deve consultar o Drive sem credencial")

    code = run_drive_job(
        folder_id=FOLDER,
        source=SOURCE,
        repo_root=tmp_path,
        wo_dir=tmp_path / "wo",
        evidence_dir=tmp_path / "evidence",
        token_loader=token_loader,
        fetch=fetch,
        year_fallback=2026,
    )
    assert code == 2
    assert list(tmp_path.rglob("data/canonical/**/*.json")) == []
    orders = sorted((tmp_path / "wo").glob("*.json"))
    assert len(orders) == 2
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in orders]
    by_task = {item["task"]: item for item in payloads}
    assert by_task["obter"]["submitted_by"] == "kernel"
    assert by_task["obter"]["status"] == "BLOQUEADO"
    assert "DRIVE_ACCESS_TOKEN" in by_task["obter"]["motivo"]
    assert by_task["atomizar"]["status"] == "BLOQUEADO"
    assert by_task["atomizar"]["depends_on"] == by_task["obter"]["wo_id"]
    assert "KERNEL-POLICY-001" in by_task["obter"]["policy_ids"]
    assert "KERNEL-POLICY-003" not in by_task["obter"]["policy_ids"]


def test_wo_rejeita_politica_desconhecida(tmp_path: Path):
    with pytest.raises(ValueError, match="gate do Kernel ausente"):
        submit_work_order(
            wo_dir=tmp_path,
            wo_id="CE-WO-DRIVE-TESTE123456789012-OBTER",
            task="obter",
            slug="teste",
            source=SOURCE,
            folder_id=FOLDER,
            gate={},
        )


def test_documento_cofen_grava_atomo_com_fetch_falso(tmp_path: Path):
    calls = {"download": 0}

    def token_loader():
        return lambda: "token-de-teste"

    def fetch(folder, token, page_token=None):
        assert folder == FOLDER
        assert token() == "token-de-teste"
        return {
            "files": [
                {
                    "id": "arqcofen",
                    "name": "resolucao-cofen.txt",
                    "mimeType": "text/plain",
                    "size": "120",
                }
            ]
        }

    def download(file_id, mime, token):
        calls["download"] += 1
        assert file_id == "arqcofen"
        assert token() == "token-de-teste"
        return COFEN.encode("utf-8")

    code = run_drive_job(
        folder_id=FOLDER,
        source=SOURCE,
        repo_root=tmp_path,
        wo_dir=tmp_path / "wo",
        evidence_dir=tmp_path / "evidence",
        token_loader=token_loader,
        fetch=fetch,
        downloader=download,
        year_fallback=2026,
    )
    assert code == 0
    assert calls["download"] == 1
    atoms = list((tmp_path / "data/canonical/atoms/cofen").glob("*.json"))
    assert len(atoms) == 1
    atom = json.loads(atoms[0].read_text(encoding="utf-8"))
    assert atom["vigencia"] == "NAO_VERIFICADO"
    assert atom["fonte_slug"] == "cofen_dou"
    quarantine = (tmp_path / "data/quarentena/cofen/rejeicoes.jsonl").read_text(encoding="utf-8")
    assert "texto_curto" in quarantine
    obter = json.loads(next((tmp_path / "wo").glob("*OBTER.json")).read_text(encoding="utf-8"))
    assert obter["status"] == "PASS"
    assert obter["resultado"]["atomos_gravados"] == 1
