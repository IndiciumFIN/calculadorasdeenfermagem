"""WO do Kernel para obter/atomizar Drive — fail-closed, sem bytes."""
import json
from pathlib import Path

import pytest

from packages.cli.kernel_work_order import (
    KernelWorkOrderError,
    submit_work_order,
    wo_id_for,
)

FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"


def _write_policy(directory: Path, policy_id: str, extra: dict | None = None) -> None:
    document = {
        "schema": "CE-KERNEL-POLICY-1.0.0",
        "id": policy_id,
        "name": policy_id,
        "validators": ["atomo_schema_validator"],
        "wo_required": True,
        "source_contract": "contracts/fontes/cofen_dou.json",
    }
    if extra:
        document.update(extra)
    (directory / f"{policy_id}.json").write_text(
        json.dumps(document), encoding="utf-8"
    )


def _repo(tmp_path: Path, *, roots: list[dict], restrictions: list[str]) -> tuple[Path, Path, Path]:
    policies = tmp_path / "contracts" / "policies"
    policies.mkdir(parents=True)
    _write_policy(policies, "KERNEL-POLICY-001")
    fontes = tmp_path / "contracts" / "fontes"
    fontes.mkdir(parents=True)
    (fontes / "cofen_dou.json").write_text(
        json.dumps({"fonte_slug": "cofen_dou", "url_oficial": "https://www.in.gov.br/"}),
        encoding="utf-8",
    )
    roots_path = tmp_path / "config" / "drive_inventory_roots_20261016.json"
    roots_path.parent.mkdir(parents=True)
    roots_path.write_text(
        json.dumps({"roots": roots, "restrictions": restrictions}),
        encoding="utf-8",
    )
    return tmp_path, policies, roots_path


def test_unregistered_folder_blocks_obter_and_writes_wo(tmp_path: Path):
    root, policies, roots_path = _repo(
        tmp_path,
        roots=[{"id": "registered-root-id", "label": "CE_MASTER"}],
        restrictions=["READ_ONLY", "NO_DELETE", "NO_PUBLICATION", "NO_CANONICAL_PROMOTION"],
    )
    document = submit_work_order(
        activity="obter",
        folder_id=FOLDER,
        repo_root=root,
        policies_dir=policies,
        roots_path=roots_path,
        env={},
    )
    assert document["estado"] == "BLOQUEADO"
    assert document["submitted_by"] == "kernel"
    assert document["bytes_acquired"] is False
    assert document["atoms_written"] == 0
    assert document["policy_ids_authorizing"] == []
    assert document["wo_id"] == wo_id_for("obter", FOLDER)
    stored = json.loads(
        (root / "data" / "legado" / f"autorizacao_{document['wo_id']}.json").read_text()
    )
    assert stored["folder_id"] == FOLDER
    assert not (root / "data" / "canonical").exists()
    assert not (root / "data" / "raw").exists()


def test_atomizar_applies_canonical_promotion_ban(tmp_path: Path):
    root, policies, roots_path = _repo(
        tmp_path,
        roots=[{"id": FOLDER, "label": "PEDIDO"}],
        restrictions=["NO_CANONICAL_PROMOTION", "NO_PUBLICATION"],
    )
    document = submit_work_order(
        activity="atomizar",
        folder_id=FOLDER,
        repo_root=root,
        policies_dir=policies,
        roots_path=roots_path,
        env={"GDRIVE_SA_KEY": "present-but-not-read"},
    )
    joined = " ".join(document["motivos"])
    assert "NO_CANONICAL_PROMOTION" in joined
    assert "NO_PUBLICATION" in joined
    assert "drive_folder_id" in joined
    assert document["bytes_acquired"] is False
    assert "Credencial ausente" not in joined


def test_second_submit_keeps_the_original_timestamp(tmp_path: Path):
    root, policies, roots_path = _repo(
        tmp_path,
        roots=[{"id": "registered-root-id", "label": "CE_MASTER"}],
        restrictions=["NO_CANONICAL_PROMOTION"],
    )
    kwargs = dict(
        activity="obter",
        folder_id=FOLDER,
        repo_root=root,
        policies_dir=policies,
        roots_path=roots_path,
        env={},
    )
    from datetime import datetime, timezone

    first = submit_work_order(now=datetime(2026, 11, 12, 3, 45, tzinfo=timezone.utc), **kwargs)
    second = submit_work_order(now=datetime(2026, 11, 12, 4, 45, tzinfo=timezone.utc), **kwargs)
    assert second["timestamp"] == first["timestamp"]
    assert second == first


def test_invalid_activity_and_folder_id_fail_closed(tmp_path: Path):
    root, policies, roots_path = _repo(
        tmp_path,
        roots=[{"id": "registered-root-id", "label": "CE_MASTER"}],
        restrictions=[],
    )
    with pytest.raises(KernelWorkOrderError, match="atividade"):
        submit_work_order(
            activity="publicar",
            folder_id=FOLDER,
            repo_root=root,
            policies_dir=policies,
            roots_path=roots_path,
            env={},
        )
    with pytest.raises(KernelWorkOrderError, match="folder_id"):
        submit_work_order(
            activity="obter",
            folder_id="../etc/passwd",
            repo_root=root,
            policies_dir=policies,
            roots_path=roots_path,
            env={},
        )


def test_explicit_folder_binding_still_refuses_bytes(tmp_path: Path):
    root, policies, roots_path = _repo(
        tmp_path,
        roots=[{"id": FOLDER, "label": "PEDIDO"}],
        restrictions=["READ_ONLY"],
    )
    _write_policy(
        policies,
        "KERNEL-POLICY-099",
        extra={"drive_folder_id": FOLDER},
    )
    document = submit_work_order(
        activity="obter",
        folder_id=FOLDER,
        repo_root=root,
        policies_dir=policies,
        roots_path=roots_path,
        env={"DRIVE_ACCESS_TOKEN": "present-but-not-read"},
    )
    assert document["policy_ids_authorizing"] == ["KERNEL-POLICY-099"]
    assert document["estado"] == "BLOQUEADO"
    assert document["bytes_acquired"] is False
    assert any("BYTES_NOT_ACQUIRED" in motivo for motivo in document["motivos"])


def test_empty_policy_registry_fails_closed(tmp_path: Path):
    policies = tmp_path / "contracts" / "policies"
    policies.mkdir(parents=True)
    roots_path = tmp_path / "config" / "drive_inventory_roots_20261016.json"
    roots_path.parent.mkdir()
    roots_path.write_text(json.dumps({"roots": [{"id": "abc"}], "restrictions": []}))
    with pytest.raises(KernelWorkOrderError, match="nenhuma KERNEL-POLICY"):
        submit_work_order(
            activity="atomizar",
            folder_id=FOLDER,
            repo_root=tmp_path,
            policies_dir=policies,
            roots_path=roots_path,
            env={},
        )
