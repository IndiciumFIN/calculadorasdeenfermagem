"""A pasta pedida fora do registry permanece bloqueada pelo Kernel."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER_ID = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
WO_PATH = ROOT / "data/legado/autorizacao_WO-DRIVE-1L0X3DQ0.json"
ROOTS_PATH = ROOT / "config/drive_inventory_roots_20261016.json"
POLICIES = ROOT / "contracts/policies"


def test_kernel_blocks_unregistered_drive_folder():
    wo = json.loads(WO_PATH.read_text(encoding="utf-8"))
    roots = json.loads(ROOTS_PATH.read_text(encoding="utf-8"))
    registered = {item["id"] for item in roots["roots"]}

    assert wo["schema"] == "CE-WO-AUTHORIZATION-1.0.0"
    assert wo["submitted_by"] == "kernel"
    assert wo["status"] == "BLOQUEADO"
    assert wo["estado"] == "BLOQUEADO"
    assert wo["kernel_decision"] == "REJECTED"
    assert wo["exit_code"] == 2
    assert wo["folder_id"] == FOLDER_ID
    assert wo["folder_id"] not in registered
    assert wo["folder_in_registered_roots"] is False
    assert wo["policy_mentions_folder"] is False
    assert wo["bytes_acquired"] is False
    assert wo["atomized"] is False
    assert wo["authorized_by"] is None
    assert wo["credentials"]["GDRIVE_SA_KEY"] is False
    assert wo["credentials"]["DRIVE_ACCESS_TOKEN"] is False
    assert "NO_CANONICAL_PROMOTION" in wo["restrictions"]
    assert roots["scope"] == "registered_roots_metadata_only"

    mentioned = [
        path.name
        for path in POLICIES.glob("KERNEL-POLICY-*.json")
        if FOLDER_ID in path.read_text(encoding="utf-8")
    ]
    assert mentioned == []
    assert wo["policies_consulted"] == sorted(
        path.stem for path in POLICIES.glob("KERNEL-POLICY-*.json")
    )
