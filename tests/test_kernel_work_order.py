"""WO de obter e atomizar submetida pelo Kernel, sem aquisição de bytes."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from kernel.work_order import (
    TARGET_FOLDER,
    KernelWorkOrderError,
    submit_folder_activities,
    submit_work_order,
)

ROOT = Path(__file__).resolve().parents[1]
ROOTS = ROOT / "config" / "drive_inventory_roots_20261016.json"
WHEN = datetime(2026, 11, 12, 4, 40, tzinfo=timezone.utc)


def _submit(tmp_path: Path, **kwargs):
    params = {
        "repo_root": ROOT,
        "wo_dir": tmp_path,
        "env": {},
        "now": WHEN,
    }
    params.update(kwargs)
    return submit_work_order(**params)


def test_folder_activities_are_blocked_without_bytes(tmp_path: Path) -> None:
    documents = submit_folder_activities(
        TARGET_FOLDER,
        repo_root=ROOT,
        wo_dir=tmp_path,
        env={},
        now=WHEN,
    )

    assert [item["tarefa"] for item in documents] == ["obter", "atomizar"]
    assert sorted(path.name for path in tmp_path.glob("*.json")) == [
        f"autorizacao_CE-WO-ATOMIZAR-{TARGET_FOLDER}.json",
        f"autorizacao_CE-WO-OBTER-{TARGET_FOLDER}.json",
    ]
    for document in documents:
        assert document["schema"] == "CE-WO-AUTHORIZATION-1.0.0"
        assert document["estado"] == "BLOQUEADO"
        assert document["status"] == "BLOQUEADO"
        assert document["submitted_by"] == "kernel"
        assert document["authorized_by"] is None
        assert document["bytes_acquired"] is False
        assert document["atoms_written"] == 0
        assert document["policy_ids_binding_folder"] == []
        assert document["credential_present"] is False
        assert len(document["policies_consulted"]) == 20
        assert document["policies_consulted"][0] == "KERNEL-POLICY-001"
        assert document["policies_consulted"][-1] == "KERNEL-POLICY-020"
        assert TARGET_FOLDER not in document["registered_drive_roots"]
        assert "CE_MASTER" not in document["registered_drive_roots"]
        assert any("KernelPolicy" in motivo for motivo in document["motivos"])
        assert any("BYTES_NOT_ACQUIRED" in motivo for motivo in document["motivos"])
        assert any("registry canônico" in motivo for motivo in document["motivos"])

    obter, atomizar = documents
    assert any("Credencial ausente" in motivo for motivo in obter["motivos"])
    assert not any("Credencial ausente" in motivo for motivo in atomizar["motivos"])
    assert any("NO_CANONICAL_PROMOTION" in motivo for motivo in atomizar["motivos"])
    assert not any("NO_CANONICAL_PROMOTION" in motivo for motivo in obter["motivos"])


def test_repeat_submit_keeps_the_original_timestamp(tmp_path: Path) -> None:
    first = _submit(tmp_path, activity="obter", folder_id=TARGET_FOLDER)
    later = datetime(2026, 11, 12, 5, 40, tzinfo=timezone.utc)
    second = _submit(tmp_path, activity="obter", folder_id=TARGET_FOLDER, now=later)

    assert second == first
    assert second["timestamp"] == "2026-11-12T04:40:00Z"
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_bound_folder_still_blocks_and_drops_credential_value(tmp_path: Path) -> None:
    policies = tmp_path / "policies"
    policies.mkdir()
    (policies / "KERNEL-POLICY-001.json").write_text(
        json.dumps(
            {
                "id": "KERNEL-POLICY-001",
                "drive_folder_id": TARGET_FOLDER,
                "source_contract": "contracts/fontes/cofen_dou.json",
            }
        ),
        encoding="utf-8",
    )
    wo_dir = tmp_path / "wo"
    document = submit_work_order(
        activity="obter",
        folder_id=TARGET_FOLDER,
        repo_root=ROOT,
        policies_dir=policies,
        roots_path=ROOTS,
        wo_dir=wo_dir,
        env={"GDRIVE_SA_KEY": "TEST_CREDENTIAL_MARKER"},
        now=WHEN,
    )

    assert document["policy_ids_binding_folder"] == ["KERNEL-POLICY-001"]
    assert document["estado"] == "BLOQUEADO"
    assert document["bytes_acquired"] is False
    assert document["atoms_written"] == 0
    assert document["credential_present"] is True
    assert not any("Credencial ausente" in motivo for motivo in document["motivos"])
    written = (wo_dir / f"autorizacao_{document['wo_id']}.json").read_text(encoding="utf-8")
    assert "TEST_CREDENTIAL_MARKER" not in written


def test_invalid_folder_and_activity_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(KernelWorkOrderError, match="folder_id"):
        _submit(tmp_path, activity="obter", folder_id="../segredo")
    with pytest.raises(KernelWorkOrderError, match="atividade"):
        _submit(tmp_path, activity="publicar", folder_id=TARGET_FOLDER)
    assert list(tmp_path.iterdir()) == []


def test_missing_source_contract_fails_closed(tmp_path: Path) -> None:
    policies = tmp_path / "policies"
    policies.mkdir()
    (policies / "KERNEL-POLICY-001.json").write_text(
        json.dumps(
            {
                "id": "KERNEL-POLICY-001",
                "source_contract": "contracts/fontes/nao_existe.json",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(KernelWorkOrderError, match="source_contract ausente"):
        submit_work_order(
            activity="atomizar",
            folder_id=TARGET_FOLDER,
            repo_root=ROOT,
            policies_dir=policies,
            roots_path=ROOTS,
            wo_dir=tmp_path / "wo",
            env={},
            now=WHEN,
        )


def test_module_does_not_call_drive() -> None:
    source = Path(submit_work_order.__code__.co_filename).read_text(encoding="utf-8")
    assert "urlopen" not in source
    assert "googleapis" not in source
    assert "bytes_acquired" in source
