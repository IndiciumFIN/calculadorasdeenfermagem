"""WO do Kernel antes de obter ou atomizar uma pasta do Drive."""
import json
from pathlib import Path

import pytest

from packages.cli.kernel.work_orders import _download_bytes, run_drive_folder

FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
NOW = "2026-11-11T12:43:49Z"


def _repo(tmp_path: Path, folder_id: str | None = None) -> Path:
    roots = tmp_path / "config"
    roots.mkdir()
    listed = []
    if folder_id:
        listed.append({"id": folder_id, "label": "AUTORIZADA"})
    (roots / "drive_inventory_roots_20261016.json").write_text(
        json.dumps({"roots": listed}), encoding="utf-8"
    )
    if folder_id:
        authority = tmp_path / "data" / "legado"
        authority.mkdir(parents=True)
        (authority / "drive_raizes.json").write_text(
            json.dumps({"roots": listed}), encoding="utf-8"
        )
    return tmp_path


def test_unregistered_folder_is_blocked_without_download(tmp_path, monkeypatch):
    def explode(*_args, **_kwargs):
        raise AssertionError("Drive não pode ser chamado com WO bloqueada")

    monkeypatch.setattr("urllib.request.urlopen", explode)
    result = run_drive_folder(
        FOLDER,
        repo=_repo(tmp_path),
        credential_present_flag=False,
        now=NOW,
        acquire=explode,
    )
    assert result["exit_code"] == 2
    assert result["bytes_acquired"] is False
    assert result["atoms_written"] == 0
    assert result["credential_present"] is False
    assert {order["estado"] for order in result["orders"]} == {"BLOQUEADO"}
    assert all(order["submitted_by"] == "kernel" for order in result["orders"])
    assert any(order["tarefa"] == "atomizar" and "não infere" in order["motivo"] for order in result["orders"])
    assert not (tmp_path / "data" / "canonical").exists()
    again = run_drive_folder(
        FOLDER,
        repo=tmp_path,
        credential_present_flag=False,
        now="2026-11-11T13:43:49Z",
        acquire=explode,
    )
    assert again["files_written"] == []
    stored = json.loads(
        (tmp_path / "data" / "legado" / f"autorizacao_WO-OBTER-{FOLDER}.json").read_text(encoding="utf-8")
    )
    assert stored["tentativas"] == 1
    assert stored["submitted_at"] == NOW
    gates = {item["id"]: item["exit_code"] for item in result["policy_gates"]}
    assert gates["KERNEL-POLICY-001"] == 0
    assert gates["KERNEL-POLICY-002"] == 0
    assert gates["KERNEL-POLICY-019"] == 0
    assert gates["KERNEL-POLICY-020"] == 0


def test_authorized_text_is_atomized_under_named_policy(tmp_path):
    folder_id = "PastaAutorizada01"
    calls = []

    def acquire(requested):
        calls.append(requested)
        body = (
            "Art. 1º O enfermeiro cumpre o prazo de 30 dias previsto no ato oficial. "
            "Fonte: https://www.in.gov.br/web/dou/exemplo-norma\n"
            "linha sem dispositivo legal e sem fonte\n"
            "curto\n"
        )
        return [{"id": "arq1", "name": "norma.txt", "mime_type": "text/plain", "error": None, "data": body.encode()}]

    result = run_drive_folder(
        folder_id,
        repo=_repo(tmp_path, folder_id),
        policy_id="KERNEL-POLICY-001",
        credential_present_flag=True,
        now=NOW,
        acquire=acquire,
    )
    assert calls == [folder_id]
    assert result["exit_code"] == 0
    assert result["atoms_written"] == 1
    atoms = list((tmp_path / "data" / "canonical" / "atoms" / "cofen").glob("*.json"))
    assert len(atoms) == 1
    atom = json.loads(atoms[0].read_text(encoding="utf-8"))
    assert atom["vigencia"] == "NAO_VERIFICADO"
    assert atom["fonte_slug"] == "cofen_dou"
    assert atom["wo_id"].startswith("CE-WO-ATOMIZAR-")
    quarantine = (tmp_path / "data" / "quarentena" / "cofen" / "validacao_invalida.jsonl").read_text(encoding="utf-8")
    assert "sem_dispositivo" in quarantine
    assert "texto_curto" in quarantine
    assert "linha sem dispositivo legal e sem fonte" in quarantine


def test_html_payload_is_rejected(monkeypatch):
    class Response:
        def read(self, _n=-1):
            return b"<!DOCTYPE html><html>login</html>"

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr("packages.cli.kernel.work_orders.urlopen", lambda *_args, **_kwargs: Response())
    with pytest.raises(ValueError, match="HTML"):
        _download_bytes("arquivo", "text/plain", lambda: "token-de-teste", 32)
