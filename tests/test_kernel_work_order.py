"""WO de Drive submetida pelo Kernel: fail-closed, sem rede e sem bytes."""
import json
from pathlib import Path

import pytest

from packages.cli.kernel_work_order import submit_drive_work_order

FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
REGISTERED = "1FDBAMQ3-WT-8l6xU0664u7QjABd0FbEH"


def _repo(tmp: Path) -> Path:
    roots = {
        "schema": "CE-DRIVE-ROOTS-1.0.0",
        "scope": "registered_roots_metadata_only",
        "roots": [
            {"id": REGISTERED, "label": "CE_MASTER"},
            {"id": "1c9vErI_It3XwzAcAFOnbxw9V0Mn6xfB9", "label": "CE_SITE"},
        ],
        "restrictions": ["READ_ONLY", "NO_DELETE", "NO_PUBLICATION", "NO_CANONICAL_PROMOTION"],
    }
    (tmp / "config").mkdir()
    (tmp / "config/drive_inventory_roots_20261016.json").write_text(
        json.dumps(roots), encoding="utf-8"
    )
    policy_dir = tmp / "contracts/policies"
    policy_dir.mkdir(parents=True)
    (policy_dir / "KERNEL-POLICY-001.json").write_text(json.dumps({
        "id": "KERNEL-POLICY-001",
        "validators": ["atomo_schema_validator"],
        "wo_required": True,
    }), encoding="utf-8")
    validators = tmp / "packages/cli/validators"
    validators.mkdir(parents=True)
    (validators / "sha256_validator.py").write_text(
        '    NAME = "atomo_schema_validator"\n', encoding="utf-8"
    )
    (tmp / "data/legado").mkdir(parents=True)
    return tmp


def _codes(document: dict) -> set[str]:
    return {item["code"] for item in document["reasons"]}


def test_unregistered_folder_is_rejected_without_bytes(tmp_path: Path):
    repo = _repo(tmp_path)
    document = submit_drive_work_order(
        repo, FOLDER, ["obter", "atomizar"], env={}, now=None,
    )
    assert document["status"] == "REJECTED"
    assert document["exit_code"] == 2
    assert document["submitted_by"] == "kernel"
    assert document["bytes_acquired"] is False
    assert document["atoms_written"] == 0
    assert document["network_access"] is False
    assert document["credentials_present"] is False
    assert document["folder_registered"] is False
    codes = _codes(document)
    assert {
        "UNREGISTERED_DRIVE_ROOT",
        "METADATA_ONLY",
        "NO_CANONICAL_PROMOTION",
        "POLICY_REQUIRED",
        "NO_MATCHING_AUTHORIZATION",
        "CREDENTIALS_MISSING",
    } <= codes
    stored = json.loads(
        (repo / "data/legado/kernel_wo" / f"CE-WO-KERNEL-DRIVE-{FOLDER}.json").read_text()
    )
    assert stored["wo_id"] == document["wo_id"]
    assert list(repo.rglob("*.pdf")) == []
    assert not (repo / "data/canonical").exists()


def test_registered_root_still_cannot_download_or_promote(tmp_path: Path):
    repo = _repo(tmp_path)
    auth = repo / "data/legado/autorizacao_WO-0090.json"
    auth.write_text(json.dumps({"wo_id": "x", "folder_id": REGISTERED}), encoding="utf-8")
    document = submit_drive_work_order(
        repo,
        REGISTERED,
        ["obter", "atomizar"],
        "KERNEL-POLICY-001",
        env={"GDRIVE_SA_KEY": "present"},
    )
    assert document["folder_registered"] is True
    assert document["credentials_present"] is True
    assert "CREDENTIALS_MISSING" not in _codes(document)
    assert "WO_AUTHORIZATION_MISSING" not in _codes(document)
    assert {"METADATA_ONLY", "NO_CANONICAL_PROMOTION"} <= _codes(document)
    assert document["bytes_acquired"] is False
    assert document["status"] == "REJECTED"


def test_unknown_activity_and_missing_policy_fail_closed(tmp_path: Path):
    repo = _repo(tmp_path)
    document = submit_drive_work_order(repo, FOLDER, ["publicar"], env={})
    assert "UNKNOWN_ACTIVITY" in _codes(document)
    assert document["bytes_acquired"] is False


def test_repeat_submission_keeps_timestamp(tmp_path: Path):
    repo = _repo(tmp_path)
    from datetime import datetime, timezone
    first_now = datetime(2026, 11, 14, 6, 40, tzinfo=timezone.utc)
    later = datetime(2026, 11, 14, 7, 40, tzinfo=timezone.utc)
    first = submit_drive_work_order(repo, FOLDER, ["atomizar", "obter"], env={}, now=first_now)
    second = submit_drive_work_order(repo, FOLDER, ["obter", "atomizar"], env={}, now=later)
    assert second["submitted_at"] == first["submitted_at"]
    assert second["activities"] == ["atomizar", "obter"]


def test_output_cannot_escape_repository(tmp_path: Path):
    repo = _repo(tmp_path)
    with pytest.raises(ValueError, match="output fora"):
        submit_drive_work_order(
            repo, FOLDER, ["obter"], env={}, output_path=tmp_path.parent / "fora.json",
        )


def test_illegible_existing_wo_is_not_overwritten(tmp_path: Path):
    repo = _repo(tmp_path)
    target = repo / "data/legado/kernel_wo" / f"CE-WO-KERNEL-DRIVE-{FOLDER}.json"
    target.parent.mkdir(parents=True)
    target.write_text("{garbled", encoding="utf-8")
    with pytest.raises(ValueError, match="não sobrescrever"):
        submit_drive_work_order(repo, FOLDER, ["obter"], env={})
    assert target.read_text(encoding="utf-8") == "{garbled"
