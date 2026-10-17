"""Importação privada local, sempre autorizada pela WO e Kernel."""
import hashlib
from pathlib import Path
from types import SimpleNamespace
import pytest
from packages.cli.staging import importar
from packages.cli.pep import carregar_wo


def _wo(path, sha):
    import json
    payload = {
        "id": "WO-2026_10_16_0108",
        "contract_version": "CKO-TAREFA-1.0.0",
        "authorized_by": "IndiciumFIN",
        "task_id": "TAREFA-IMPORTAR-DRIVE",
        "task_version": "1.0.0",
        "task_type": "importar-drive",
        "policy_version": "1.0.0",
        "state": "PREAUTHORIZED",
        "entradas": [{"id_origem": "drive-test-id", "caminho": "data/legado/extracao_bruta/piloto.bin", "classe": "REFERENCIA", "sha256": sha}],
        "parametros": {"source_mount": "source.bin", "source_provider": "google_drive"}
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return carregar_wo(path)


def test_importacao_hash_e_idempotencia(tmp_path, monkeypatch):
    mount = tmp_path / "mount"
    mount.mkdir()
    (mount / "source.bin").write_bytes(b"arquivo privado para teste")
    sha = hashlib.sha256((mount / "source.bin").read_bytes()).hexdigest()
    wo = _wo(tmp_path / "wo.json", sha)
    monkeypatch.setenv("CE_CONNECTOR_STAGING_ROOT", str(mount))
    repo = tmp_path / "repo"
    first, evidence = importar(wo, repo)
    assert first["status"] == "ESTAGIADO"
    assert evidence.exists()
    again, _ = importar(wo, repo)
    assert again["status"] == "JA_PRESENTE_IDEMPOTENTE"
    assert not again["deletion_authorized"]


def test_importacao_divergencia_nao_escreve(tmp_path, monkeypatch):
    mount = tmp_path / "mount"
    mount.mkdir()
    (mount / "source.bin").write_bytes(b"conteudo real")
    wo = _wo(tmp_path / "wo.json", "a" * 64)
    monkeypatch.setenv("CE_CONNECTOR_STAGING_ROOT", str(mount))
    with pytest.raises(ValueError, match="SHA-256"):
        importar(wo, tmp_path / "repo")
    assert not (tmp_path / "repo/data/legado/extracao_bruta/piloto.bin").exists()
