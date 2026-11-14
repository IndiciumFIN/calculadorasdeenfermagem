"""WO de Drive submetida pelo Kernel: registra e recusa sem política."""
import json
from pathlib import Path

import pytest

from packages.cli.kernel.work_orders import (
    build_work_order,
    execution_exit_code,
    human_authorization_present,
    load_policy_documents,
    load_registered_root_ids,
    parse_folder_id,
    submit_drive_activities,
    write_work_order,
)

FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
REPO = Path(__file__).resolve().parents[1]


def _order(**overrides):
    params = dict(
        folder_id=FOLDER,
        tarefa="obter",
        policies=[{"id": "KERNEL-POLICY-001", "wo_required": True}],
        registered_root_ids={"outra-raiz"},
        credential_present=False,
        drive_api_http_status=403,
        human_authorization=False,
    )
    params.update(overrides)
    return build_work_order(**params)


def test_parse_folder_url():
    url = "https://drive.google.com/drive/folders/" + FOLDER + "?hl=pt-br"
    assert parse_folder_id(url) == FOLDER
    assert parse_folder_id(FOLDER) == FOLDER
    with pytest.raises(ValueError):
        parse_folder_id("pasta-curta")


def test_kernel_blocks_without_self_approval():
    order = _order()
    assert order["submitted_by"] == "kernel"
    assert order["authorized_by"] is None
    assert order["estado"] == "BLOQUEADO"
    assert order["status"] != "PREAUTHORIZED"
    assert order["bytes_acquired"] is False
    assert order["atoms_emitted"] == 0
    assert order["sha256_fonte"] is None
    assert order["policies_authorizing_folder"] == []
    assert execution_exit_code([order]) == 2


def test_explicit_policy_field_is_the_only_authorization():
    named = _order(policies=[{"id": "KERNEL-POLICY-001", "drive_folder_ids": [FOLDER]}])
    assert named["policies_authorizing_folder"] == ["KERNEL-POLICY-001"]
    mentioned = _order(policies=[{"id": "KERNEL-POLICY-001", "description": FOLDER}])
    assert mentioned["policies_authorizing_folder"] == []


def test_real_registry_does_not_authorize_this_folder():
    policies = load_policy_documents(REPO / "contracts/policies")
    roots = load_registered_root_ids(REPO / "config/drive_inventory_roots_20261016.json")
    assert len(policies) >= 20
    assert FOLDER not in roots
    for tarefa in ("obter", "atomizar"):
        order = build_work_order(
            folder_id=FOLDER,
            tarefa=tarefa,
            policies=policies,
            registered_root_ids=roots,
            credential_present=False,
            drive_api_http_status=403,
            human_authorization=human_authorization_present(REPO / "data/legado", FOLDER),
        )
        assert order["estado"] == "BLOQUEADO"
        assert order["policies_authorizing_folder"] == []
        assert "sha256_fonte ausente" in order["motivos"] or tarefa == "obter"


def test_submit_writes_one_wo_per_activity(tmp_path: Path):
    (tmp_path / "contracts/policies").mkdir(parents=True)
    (tmp_path / "contracts/policies/KERNEL-POLICY-001.json").write_text(
        json.dumps({"id": "KERNEL-POLICY-001", "wo_required": True}),
        encoding="utf-8",
    )
    (tmp_path / "config").mkdir()
    (tmp_path / "config/drive_inventory_roots_20261016.json").write_text(
        json.dumps({"roots": [{"id": "raiz-registrada", "label": "CE_MASTER"}]}),
        encoding="utf-8",
    )
    orders = submit_drive_activities(
        folder="https://drive.google.com/drive/folders/" + FOLDER,
        tarefas=["obter", "atomizar"],
        repo_root=tmp_path,
        drive_api_http_status=403,
    )
    assert [order["tarefa"] for order in orders] == ["obter", "atomizar"]
    paths = list((tmp_path / "data/legado").glob("autorizacao_WO-*.json"))
    assert len(paths) == 2
    again = submit_drive_activities(
        folder=FOLDER,
        tarefas=["obter", "atomizar"],
        repo_root=tmp_path,
        drive_api_http_status=403,
    )
    assert again == orders
    assert execution_exit_code(again) == 2


def test_unknown_activity_is_refused(tmp_path: Path):
    with pytest.raises(ValueError, match="tarefa desconhecida"):
        submit_drive_activities(folder=FOLDER, tarefas=["publicar"], repo_root=tmp_path)


def test_write_does_not_stamp_human_approver(tmp_path: Path):
    path = write_work_order(tmp_path, _order())
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["authorized_by"] is None
    assert saved["submitted_by"] == "kernel"
    assert saved["estado"] != "PREAUTHORIZED"
    assert saved["status"] != "PREAUTHORIZED"
