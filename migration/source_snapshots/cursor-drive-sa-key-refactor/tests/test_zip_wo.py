"""M04: ZIP pilot by qualified WO, no extraction and no deletion."""
import shutil
import zipfile
from pathlib import Path

import pytest
from packages.cli.pep import RAIZ, carregar_wo
from packages.cli.archive_audit import auditar_zip_wo, zip_scan


def test_zip_de_controle_com_sha_declarado(tmp_path):
    wo = carregar_wo(RAIZ / "contracts/work_orders/WO-2026_10_16_0105.json")
    src = RAIZ / wo.entradas[0].caminho
    dst = tmp_path / wo.entradas[0].caminho
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    outcome, output = auditar_zip_wo(wo, tmp_path)
    assert output.exists()
    assert outcome["status"] == "ANALISADO"
    assert outcome["membros"] > 0
    assert outcome["exclusao_autorizada"] is False
    assert outcome["extracao_em_disco"] is False
    assert all(x["sha256"] for x in outcome["manifesto_membros"] if not x["path"].endswith("/"))


def test_member_traversal_fica_em_hold(tmp_path):
    archive = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("../secreto.txt", "material")
    result = zip_scan(archive)
    assert any(x["type"] == "UNSAFE_MEMBER" for x in result["findings"])
