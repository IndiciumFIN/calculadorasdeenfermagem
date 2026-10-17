"""Regressões fail-closed para WOs de movimentação no Drive."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from packages.cli.drive_move import guard, preflight, reconcile
from packages.cli.pep import carregar_wo


def test_real_wos_have_qualified_contract():
    root = Path(__file__).resolve().parents[1]
    for number in ("0234", "0235"):
        wo = carregar_wo(root / "contracts/work_orders" / f"WO-2026_10_16_{number}.json")
        assert wo.task_type == "mover-drive"
        assert wo.checker_id != wo.authorized_by
        assert wo.entradas[0].sha256
        assert wo.parametros["source_parent_id"] != wo.parametros["target_parent_id"]


def make_pilot(tmp_path):
    p = tmp_path / "data/legado/extracao_bruta/TYPE_MOVE_PILOT/sample.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"SAFE PILOT")
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    config = tmp_path / "policies/drive_move_destinations.json"
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({
        "source_parents": ["original"], "type_destinations": {"MD":"destination"},
        "mime_by_type": {"MD":"text/markdown"}}))
    wo = SimpleNamespace(id="WO-2026_10_16_0234",
        entradas=[SimpleNamespace(classe="REFERENCIA",id_origem="drive-id",
        caminho="data/legado/extracao_bruta/TYPE_MOVE_PILOT/sample.md",sha256=digest)],
        parametros={"source_parent_id":"original","target_parent_id":"destination",
                    "file_type":"MD","expected_title":"sample.md",
                    "expected_mime":"text/markdown","expected_bytes":"10"})
    return wo,p


def test_preflight_reconciliation_and_rollback(tmp_path):
    wo, source = make_pilot(tmp_path)
    permit, _ = preflight(wo,tmp_path)
    assert permit["phase"] == "PREFLIGHT_PASS"
    assert permit["copy_authorized"] is False
    receipt = tmp_path / "data/grc/receipts/WO-2026_10_16_0234.json"
    receipt.parent.mkdir(parents=True)
    obj={"work_order":wo.id,"file_id":"drive-id","source_parent_id":"original",
         "target_parent_id":"destination","before_parent_ids":["original"],
         "after_parent_ids":["destination"],"name":"sample.md",
         "mime_type":"text/markdown","bytes":10,
         "postmove_sha256":permit["sha256"],
         "postmove_local_path":"data/legado/extracao_bruta/TYPE_MOVE_PILOT/sample.md",
         "connector_update_success":True}
    receipt.write_text(json.dumps(obj))
    report, proof = reconcile(wo,tmp_path,receipt)
    assert report["phase"] == "MOVE_CONFIRMED"
    assert report["rollback"] == {"addParents":"original","removeParents":"destination"}
    assert proof.exists()


def test_wrong_target_rejected(tmp_path):
    wo,_ = make_pilot(tmp_path)
    wo.parametros["target_parent_id"]="other"
    with pytest.raises(ValueError,match="destino sem autorização"):
        guard(wo,tmp_path)


def test_tampered_source_rejected(tmp_path):
    wo,source = make_pilot(tmp_path)
    source.write_bytes(b"tampered")
    with pytest.raises(ValueError,match="SHA-256"):
        preflight(wo,tmp_path)
    assert not list(tmp_path.rglob("move_preflight_*.json"))


def test_incorrect_parent_receipt_rejected(tmp_path):
    wo,_=make_pilot(tmp_path)
    permit,_=preflight(wo,tmp_path)
    receipt=tmp_path/"data/grc/receipts/WO-2026_10_16_0234.json"
    receipt.parent.mkdir(parents=True)
    receipt.write_text(json.dumps({"work_order":wo.id,"file_id":"drive-id",
       "source_parent_id":"original","target_parent_id":"destination",
       "before_parent_ids":["original"],"after_parent_ids":["wrong"],
       "name":"sample.md","mime_type":"text/markdown","bytes":10,
       "postmove_sha256":permit["sha256"],"connector_update_success":True}))
    with pytest.raises(ValueError,match="parent ou SHA"):
        reconcile(wo,tmp_path,receipt)
