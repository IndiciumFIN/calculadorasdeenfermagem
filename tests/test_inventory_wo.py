"""M03: audit metadata through qualified Work Order / Kernel."""
import json
import shutil
from pathlib import Path

import pytest

from packages.cli.inventory import auditar
from packages.cli.pep import RAIZ, carregar_wo

WO = RAIZ / "contracts/work_orders/WO-2026_10_16_0104.json"
SNAPSHOT = RAIZ / "data/grc/drive_inventory_20261016_pilot.json"


def _preparar(tmp_path):
    dest = tmp_path / "data/grc/drive_inventory_20261016_pilot.json"
    dest.parent.mkdir(parents=True)
    shutil.copy2(SNAPSHOT, dest)
    return carregar_wo(WO), dest


def test_inventario_piloto_gera_evidencia_nao_promovivel(tmp_path):
    wo, _ = _preparar(tmp_path)
    rel, dest = auditar(wo, tmp_path)
    assert dest.is_file()
    assert rel["status"] == "PARCIAL"
    assert rel["arquivos_observados"] == 230
    assert rel["zips_observados"] == 49
    assert rel["homologacao"] is False
    assert rel["exclusao_autorizada"] is False
    assert any(x["listagem_parcial"] for x in rel["raizes"])


def test_sha_alterado_falha_sem_criar_evidencia(tmp_path):
    wo, path = _preparar(tmp_path)
    path.write_text(path.read_text() + "modificado")
    with pytest.raises(ValueError, match="SHA-256"):
        auditar(wo, tmp_path)
    assert not list(tmp_path.rglob("auditar_inventario_*.json"))


def test_contagem_adulterada_mesmo_com_wo_invalida(tmp_path):
    wo, _ = _preparar(tmp_path)
    wo.entradas[0].sha256 = "b" * 64
    with pytest.raises(ValueError, match="SHA-256"):
        auditar(wo, tmp_path)
