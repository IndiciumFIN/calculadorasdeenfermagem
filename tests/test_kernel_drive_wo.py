"""A pasta Drive pedida não é baixada nem atomizada sem WO do Kernel."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "packages" / "cli"
sys.path.insert(0, str(CLI))

from kernel.activities import executar_pasta  # noqa: E402
from kernel.core import Kernel  # noqa: E402
from kernel.work_order import load_work_order, work_order_id  # noqa: E402

FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
OBTER_ID = "CE-WO-OBTER-d3271721ab03"
ATOMIZAR_ID = "CE-WO-ATOMIZAR-95b66f37ea49"


def _clock():
    stamps = iter(
        f"2026-11-13T12:45:{index:02d}+00:00" for index in range(20)
    )
    return lambda: next(stamps)


def _tree(tmp_path: Path) -> Path:
    config = tmp_path / "config"
    config.mkdir()
    source = ROOT / "config" / "drive_inventory_roots_20261016.json"
    (config / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    policies = tmp_path / "contracts" / "policies"
    policies.mkdir(parents=True)
    origin = ROOT / "contracts" / "policies"
    for path in sorted(origin.glob("KERNEL-POLICY-*.json")):
        (policies / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return tmp_path


def test_ids_sao_deterministicos():
    assert work_order_id("obter", FOLDER) == OBTER_ID
    assert work_order_id("atomizar", FOLDER) == ATOMIZAR_ID


def test_pasta_bloqueada_sem_rede(tmp_path, monkeypatch):
    def rede(*_args, **_kwargs):
        raise AssertionError("a rede não pode ser aberta")

    monkeypatch.setattr("urllib.request.urlopen", rede)
    root = _tree(tmp_path)
    calls: list[str] = []
    original = Kernel.submit_wo

    def wrapped(self, **kwargs):
        calls.append(kwargs["estado"])
        return original(self, **kwargs)

    monkeypatch.setattr(Kernel, "submit_wo", wrapped)
    code = executar_pasta(FOLDER, root=root, clock=_clock(), environ={})

    assert code == 2
    assert calls == ["SUBMITTED", "BLOQUEADO", "SUBMITTED", "BLOQUEADO"]
    assert not (root / "data" / "raw").exists()

    obter = load_work_order(root, OBTER_ID)
    atomizar = load_work_order(root, ATOMIZAR_ID)
    assert obter["submitted_by"] == "kernel"
    assert obter["estado"] == "BLOQUEADO"
    assert obter["sha256_fonte"] is None
    assert obter["contagens"] == {"arquivos": 0, "bytes": 0}
    assert obter["politicas_validas"] == []
    assert "ausente das raízes registradas" in obter["motivo"]
    assert "drive_raizes.json inexistente" in obter["motivo"]
    assert "drive_folder_ids" in obter["motivo"]
    assert "NO_CANONICAL_PROMOTION" in obter["motivo"]
    assert "DRIVE_ACCESS_TOKEN" in obter["motivo"]
    assert [item["estado"] for item in obter["historico"]] == ["SUBMITTED", "BLOQUEADO"]

    assert atomizar["submitted_by"] == "kernel"
    assert atomizar["estado"] == "BLOQUEADO"
    assert atomizar["depends_on"] == OBTER_ID
    assert atomizar["sha256_fonte"] is None
    assert "não possui sha256_fonte" in atomizar["motivo"]
    assert atomizar["contagens"] == {"atomos": 0, "bytes": 0}


def test_id_invalido_nao_grava_wo(tmp_path):
    code = executar_pasta("../fora", root=tmp_path, environ={})
    assert code == 2
    assert not (tmp_path / "data").exists()


def test_rerun_acrescenta_historico(tmp_path):
    root = _tree(tmp_path)
    clock = _clock()
    assert executar_pasta(FOLDER, root=root, clock=clock, environ={}) == 2
    assert executar_pasta(FOLDER, root=root, clock=clock, environ={}) == 2
    obter = load_work_order(root, OBTER_ID)
    assert [item["estado"] for item in obter["historico"]] == [
        "SUBMITTED",
        "BLOQUEADO",
        "SUBMITTED",
        "BLOQUEADO",
    ]
    assert obter["tentativas"] == 2
    assert obter["estado"] == "BLOQUEADO"


def test_politica_e_raiz_nao_autorizam_bytes(tmp_path, monkeypatch):
    def rede(*_args, **_kwargs):
        raise AssertionError("a rede não pode ser aberta")

    monkeypatch.setattr("urllib.request.urlopen", rede)
    root = _tree(tmp_path)
    roots_path = root / "config" / "drive_inventory_roots_20261016.json"
    payload = json.loads(roots_path.read_text(encoding="utf-8"))
    payload["roots"].append({"id": FOLDER, "label": "PEDIDO"})
    payload["restrictions"] = ["READ_ONLY"]
    payload["scope"] = "conteudo"
    roots_path.write_text(json.dumps(payload), encoding="utf-8")
    authority = root / "data" / "legado" / "drive_raizes.json"
    authority.parent.mkdir(parents=True)
    authority.write_text(json.dumps({"roots": [{"id": FOLDER}]}), encoding="utf-8")
    parser = root / "packages" / "cli" / "adapters" / "dou.py"
    parser.parent.mkdir(parents=True)
    parser.write_text("# parser\n", encoding="utf-8")
    policy = {
        "id": "KERNEL-POLICY-001",
        "drive_folder_ids": [FOLDER],
        "parser": "packages/cli/adapters/dou.py",
    }
    (root / "contracts" / "policies" / "KERNEL-POLICY-001.json").write_text(
        json.dumps(policy),
        encoding="utf-8",
    )

    code = executar_pasta(
        FOLDER,
        root=root,
        clock=_clock(),
        environ={"GDRIVE_SA_KEY": "presente-nao-usar", "DRIVE_ACCESS_TOKEN": "presente-nao-usar"},
    )
    assert code == 2
    obter = load_work_order(root, OBTER_ID)
    assert obter["estado"] == "BLOQUEADO"
    assert obter["politicas_validas"] == ["KERNEL-POLICY-001"]
    assert "parser executável" in obter["motivo"]
    assert not (root / "data" / "raw").exists()
