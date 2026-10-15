"""FIND registra o achado. Não autoriza correção e não apaga o histórico."""
import hashlib
import json
from pathlib import Path

import pytest
import typer

from packages.cli.finds import carregar
from packages.cli.kernel import encerrar_find, registrar_find, vincular_find
from packages.cli.pep import carregar_wo
from packages.cli.registry import set_status

QUANDO = "2026-10-15"


def _wo(task_id: str, task_type: str, parametros: dict, *, checker: bool = False) -> dict:
    doc = {
        "id": f"WO-{task_type.upper()}-TESTE-001",
        "contract_version": "CKO-TAREFA-1.0.0",
        "authorized_by": "IndiciumFIN",
        "checker_id": "kernel-find" if checker else None,
        "task_id": task_id,
        "task_version": "1.0.0",
        "task_type": task_type,
        "policy_version": "1.0.0",
        "state": "PREAUTHORIZED",
        "entradas": [],
        "parametros": parametros,
    }
    if not checker:
        doc.pop("checker_id")
    return doc


def _gravar(tmp_path: Path, doc: dict) -> Path:
    caminho = tmp_path / "wo.json"
    caminho.write_text(json.dumps(doc), encoding="utf-8")
    return caminho


def _preparar(tmp_path, monkeypatch):
    monkeypatch.setattr("packages.cli.finds.REGISTRO", tmp_path / "registro.json")
    monkeypatch.setattr("packages.cli.finds.BASE", tmp_path)


def _registro():
    return {
        "codigo": "KER-001",
        "objeto": "packages/cli/llm_runner.py",
        "severidade": "CRITICA",
        "descricao": "Autorização da Work Order não é autenticada.",
        "impacto": "Uma ordem compatível pode correr sem aprovação.",
        "detector": "auditoria",
        "quando": QUANDO,
    }


def test_registrar_nao_autoriza_correcao(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch)
    registrar_find(work_order=_gravar(tmp_path, _wo("TAREFA-FIND-REGISTRAR", "registrar-find", _registro())))
    doc = carregar(tmp_path / "registro.json")
    assert doc["finds"][0]["status"] == "ABERTO"
    assert doc["finds"][0]["correcao_autorizada"] is False
    assert doc["eventos"][0]["tipo"] == "REGISTRADO"
    assert doc["eventos"][0]["antes"]["status"] is None
    assert doc["eventos"][0]["depois"]["status"] == "ABERTO"


def test_reincidencia_nao_cria_outro_find(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch)
    ordem = _gravar(tmp_path, _wo("TAREFA-FIND-REGISTRAR", "registrar-find", _registro()))
    registrar_find(work_order=ordem)
    registrar_find(work_order=ordem)
    doc = carregar(tmp_path / "registro.json")
    assert len(doc["finds"]) == 1
    assert doc["finds"][0]["deteccoes"] == 2
    assert [evento["tipo"] for evento in doc["eventos"]] == ["REGISTRADO", "REINCIDENCIA"]
    assert doc["eventos"][1]["antes"]["deteccoes"] == 1
    assert doc["eventos"][1]["depois"]["deteccoes"] == 2


def test_correcao_nao_esta_qualificada(tmp_path):
    doc = _wo("TAREFA-FIND-CORRIGIR", "corrigir-find", _registro())
    doc["task_version"] = "0.0.0"
    with pytest.raises(ValueError, match="não qualificada"):
        carregar_wo(_gravar(tmp_path, doc))


def test_vincular_nao_fecha(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch)
    registrar_find(work_order=_gravar(tmp_path, _wo("TAREFA-FIND-REGISTRAR", "registrar-find", _registro())))
    run = tmp_path / "run.json"
    run.write_text('{"resultado":"FAIL"}\n', encoding="utf-8")
    vincular_find(
        work_order=_gravar(
            tmp_path,
            _wo(
                "TAREFA-FIND-VINCULAR",
                "vincular-find",
                {
                    "find_id": "FIND-0001",
                    "work_order_ref": "WO-REGISTRAR-FIND-TESTE-001",
                    "run_caminho": "run.json",
                    "quando": QUANDO,
                },
            ),
        )
    )
    doc = carregar(tmp_path / "registro.json")
    assert doc["finds"][0]["status"] == "ABERTO"
    assert doc["finds"][0]["ciclos"] == 1
    assert doc["finds"][0]["correcao_autorizada"] is False
    assert doc["eventos"][-1]["tipo"] == "VINCULADO"
    assert len(doc["eventos"][-1]["extra"]["run_sha256"]) == 64


def test_encerrar_exige_hash_e_preserva_historico(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch)
    registrar_find(work_order=_gravar(tmp_path, _wo("TAREFA-FIND-REGISTRAR", "registrar-find", _registro())))
    evid = tmp_path / "reteste.txt"
    evid.write_text("reteste passou\n", encoding="utf-8")
    sha = hashlib.sha256(evid.read_bytes()).hexdigest()
    ruim = _wo(
        "TAREFA-FIND-ENCERRAR",
        "encerrar-find",
        {
            "find_id": "FIND-0001",
            "evidencia_caminho": "reteste.txt",
            "evidencia_sha256": "b" * 64,
            "quando": QUANDO,
        },
        checker=True,
    )
    with pytest.raises(typer.Exit) as exc:
        encerrar_find(work_order=_gravar(tmp_path, ruim))
    assert exc.value.exit_code == 2
    assert carregar(tmp_path / "registro.json")["finds"][0]["status"] == "ABERTO"

    igual = ruim | {"checker_id": "IndiciumFIN"}
    with pytest.raises(ValueError, match="checker_id"):
        carregar_wo(_gravar(tmp_path, igual))

    bom = ruim | {
        "parametros": {
            "find_id": "FIND-0001",
            "evidencia_caminho": "reteste.txt",
            "evidencia_sha256": sha,
            "quando": QUANDO,
        }
    }
    encerrar_find(work_order=_gravar(tmp_path, bom))
    doc = carregar(tmp_path / "registro.json")
    assert doc["finds"][0]["status"] == "FECHADO"
    assert doc["finds"][0]["correcao_autorizada"] is False
    assert [evento["tipo"] for evento in doc["eventos"]] == ["REGISTRADO", "FECHADO"]

    registrar_find(work_order=_gravar(tmp_path, _wo("TAREFA-FIND-REGISTRAR", "registrar-find", _registro())))
    de_novo = carregar(tmp_path / "registro.json")
    assert len(de_novo["finds"]) == 1
    assert de_novo["finds"][0]["status"] == "ABERTO"
    assert [evento["tipo"] for evento in de_novo["eventos"]] == ["REGISTRADO", "FECHADO", "REABERTO"]


def test_promocao_a_canonico_bloqueia_find_critico_aberto(tmp_path, monkeypatch):
    _preparar(tmp_path, monkeypatch)
    monkeypatch.chdir(tmp_path)
    registrar_find(work_order=_gravar(tmp_path, _wo("TAREFA-FIND-REGISTRAR", "registrar-find", _registro())))
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "registry.json").write_text(
        json.dumps(
            [
                {
                    "id_canonico": "X-9",
                    "tipo": "atomo",
                    "hash_sha256": "a" * 64,
                    "status": "validado",
                    "origem": "manual",
                    "versao_contrato": "1.2.0",
                    "find_ids": ["FIND-0001"],
                    "historico": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    with pytest.raises(typer.Exit) as exc:
        set_status(id_canonico="X-9", novo_status="canonico", evidencia="tentativa com FIND critico aberto")
    assert exc.value.exit_code == 2
    estado = json.loads((tmp_path / "data" / "registry.json").read_text(encoding="utf-8"))
    assert estado[0]["status"] == "validado"
