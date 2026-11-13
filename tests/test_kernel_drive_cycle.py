"""Ciclo Drive do Kernel: WO antes de obter ou atomizar, fail-closed sem credencial."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "packages" / "cli"))

from kernel.core import Kernel  # noqa: E402
from kernel.drive_cycle import classify_path, run_drive_cycle  # noqa: E402
from kernel.wo import WorkOrderError, require_wo, verify_wo  # noqa: E402
from packages.cli.drive_recursive_inventory import CredentialError, FOLDER  # noqa: E402

FOLDER_ID = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
WHEN = datetime(2026, 11, 13, 12, 0, tzinfo=timezone.utc)
ARTIGO = (
    "Art. 1 O enfermeiro executa o registro do procedimento no prontuario da unidade de saude."
)


def test_gate_policy_001_loads_registered_validators():
    assert Kernel().gate("KERNEL-POLICY-001") == 0


def test_missing_credential_submits_blocked_wo_and_does_not_list(tmp_path):
    calls = []

    def fetch(*args, **kwargs):
        calls.append(args)
        return {"files": []}

    def loader():
        raise CredentialError("Neither GDRIVE_SA_KEY nor DRIVE_ACCESS_TOKEN is configured; fail closed.")

    repo = tmp_path
    code = run_drive_cycle(
        FOLDER_ID,
        repo,
        token_loader=loader,
        fetch=fetch,
        now=WHEN,
    )
    assert code == 2
    assert calls == []
    wo_files = list((repo / "data" / "kernel" / "wo").glob("*.json"))
    assert len(wo_files) == 1
    payload = json.loads(wo_files[0].read_text(encoding="utf-8"))
    verify_wo(payload)
    assert payload["submitted_by"] == "kernel"
    assert payload["activity"] == "obter"
    assert payload["status"] == "BLOQUEADO"
    assert "GDRIVE_SA_KEY" in payload["motivo"]
    with pytest.raises(WorkOrderError):
        require_wo(repo, payload["wo_id"], activity="obter", folder_id=FOLDER_ID)


def test_download_happens_only_after_kernel_wo_and_cofen_is_atomized(tmp_path):
    seen = {}

    def fetch(folder, token, page_token=None):
        if folder == FOLDER_ID:
            return {
                "files": [
                    {"id": "file-cofen", "name": "COFEN", "mimeType": FOLDER},
                    {
                        "id": "solto",
                        "name": "notas.txt",
                        "mimeType": "text/plain",
                        "size": "20",
                    },
                ]
            }
        return {
            "files": [
                {
                    "id": "artigo-1",
                    "name": "resolucao-2024.txt",
                    "mimeType": "text/plain",
                    "size": "120",
                }
            ]
        }

    def download(file_id, token, export_mime=None):
        wo_files = list((tmp_path / "data" / "kernel" / "wo").glob("CE-WO-*-OBTER-*.json"))
        assert wo_files, "download sem WO de obter"
        payload = json.loads(wo_files[0].read_text(encoding="utf-8"))
        verify_wo(payload)
        assert payload["activity"] == "obter"
        seen[file_id] = export_mime
        if file_id == "artigo-1":
            return ARTIGO.encode()
        return b"nota solta sem politica"

    code = run_drive_cycle(
        FOLDER_ID,
        tmp_path,
        token_loader=lambda: "token-teste",
        fetch=fetch,
        download=download,
        now=WHEN,
    )
    assert code == 0
    assert seen.keys() == {"artigo-1", "solto"}
    atoms = list((tmp_path / "data" / "canonical" / "atoms" / "cofen").glob("*.json"))
    assert len(atoms) == 1
    atom = json.loads(atoms[0].read_text(encoding="utf-8"))
    assert atom["vigencia"] == "NAO_VERIFICADO"
    assert atom["texto_regra"] == ARTIGO
    assert atom["id_atomo"].startswith("NORM-2024-")
    assert atom["wo_id"].startswith("CE-WO-20261113-ATOMIZAR-")
    manifest = json.loads(
        (tmp_path / "data" / "kernel" / "drive" / FOLDER_ID / "manifest.json").read_text()
    )
    by_id = {row["id"]: row for row in manifest["items"]}
    assert by_id["solto"]["status"] == "SEM_POLITICA"
    assert by_id["artigo-1"]["status"] == "OBTIDO"
    assert by_id["artigo-1"]["sha256"]


def test_ambiguous_and_stub_policy_do_not_enter_canonical(tmp_path):
    def fetch(folder, token, page_token=None):
        if folder != FOLDER_ID:
            return {"files": []}
        return {
            "files": [
                {
                    "id": "mix",
                    "name": "cofen_portaria.txt",
                    "mimeType": "text/plain",
                    "size": "40",
                },
                {
                    "id": "cid",
                    "name": "cid10.txt",
                    "mimeType": "text/plain",
                    "size": "40",
                },
            ]
        }

    def download(file_id, token, export_mime=None):
        return b"Art. 2 Texto longo o suficiente para parecer uma regra normativa de teste."

    code = run_drive_cycle(
        FOLDER_ID,
        tmp_path,
        token_loader=lambda: "token-teste",
        fetch=fetch,
        download=download,
        now=WHEN,
    )
    assert code == 2
    assert list((tmp_path / "data" / "canonical").glob("**/*.json")) == []
    quarantine = tmp_path / "data" / "quarentena" / "cid10" / "quarentena.jsonl"
    assert quarantine.exists()
    row = json.loads(quarantine.read_text(encoding="utf-8").splitlines()[0])
    assert row["motivo"] == "validador_nao_conforme"
    manifest = json.loads(
        (tmp_path / "data" / "kernel" / "drive" / FOLDER_ID / "manifest.json").read_text()
    )
    statuses = {row["id"]: row["status"] for row in manifest["items"]}
    assert statuses["mix"] == "AMBIGUO"
    assert statuses["cid"] == "OBTIDO"


def test_long_paragraph_is_quarantined_whole(tmp_path):
    def fetch(folder, token, page_token=None):
        if folder != FOLDER_ID:
            return {"files": []}
        return {
            "files": [
                {
                    "id": "longo",
                    "name": "COFEN-longo.txt",
                    "mimeType": "text/plain",
                    "size": "900",
                }
            ]
        }

    def download(file_id, token, export_mime=None):
        return ("Art. 9 " + ("norma " * 200)).encode()

    code = run_drive_cycle(
        FOLDER_ID,
        tmp_path,
        token_loader=lambda: "token-teste",
        fetch=fetch,
        download=download,
        now=WHEN,
    )
    assert code == 2
    assert list((tmp_path / "data" / "canonical" / "atoms" / "cofen").glob("*.json")) == []
    quarantine = (tmp_path / "data" / "quarentena" / "cofen" / "quarentena.jsonl").read_text()
    row = json.loads(quarantine.splitlines()[0])
    assert row["motivo"] == "acima_contrato"
    assert row["preservado"] is True
    assert len(row["texto_regra_inteiro"]) > 800


def test_classify_path_is_unique_or_ambiguous():
    assert classify_path("normas/COFEN/resolucao.txt") == ["KERNEL-POLICY-001"]
    assert classify_path("cid-10/categorias.csv") == ["KERNEL-POLICY-003"]
    matched = classify_path("cofen_portaria_ms.txt")
    assert "KERNEL-POLICY-001" in matched
    assert "KERNEL-POLICY-019" in matched
    assert classify_path("notas-internas.txt") == []
