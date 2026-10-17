"""Políticas GRC candidatas e validadores chamáveis pelo kernel."""
import importlib
import json
from pathlib import Path

from packages.cli.grc_politica import avaliar
from packages.cli.pep import RAIZ, carregar_wo

GRC = json.loads((RAIZ / "policies" / "grc.json").read_text(encoding="utf-8"))
REGISTRO = json.loads((RAIZ / "policies" / "validadores.json").read_text(encoding="utf-8"))["validadores"]


def test_pacote_entra_como_candidato_e_adicional_fica_identificada():
    assert len(GRC["politicas"]) == 16
    assert {item["policy_id"] for item in GRC["politicas"]} == {f"POL-GRC-{n:03d}" for n in range(1, 17)}
    assert all(item["status"] == "CANDIDATE_NOT_HOMOLOGATED" for item in GRC["politicas"])
    adicionais = {item["policy_id"] for item in GRC["adicionais"]}
    assert adicionais == {f"POL-GRC-{n:03d}" for n in (17, 18, 19, 20, 21, 22, 23, 24, 25)}
    assert all(item["status"] == "IDENTIFICADA" for item in GRC["adicionais"])


def test_validador_implementado_esta_no_kernel_e_o_identificado_fica_de_fora():
    for vid, item in GRC["validadores"].items():
        if item["implementado"]:
            assert REGISTRO[vid] == item["funcao"]
            modulo, _, nome = item["funcao"].rpartition(".")
            assert hasattr(importlib.import_module(modulo), nome)
        else:
            assert vid not in REGISTRO
            assert item["funcao"] is None


def test_pass_local_nao_autoriza_e_hold_externo_permanece():
    base = avaliar("POL-GRC-002")
    assert base["result"] == "PASS_LOCAL"
    assert base["authorization"] is False
    assert avaliar("POL-GRC-006")["result"] == "PASS_LOCAL"
    assert avaliar("POL-GRC-011")["result"] == "PASS_LOCAL"
    assert avaliar("POL-GRC-019")["result"] == "PASS_LOCAL"
    assert avaliar("POL-GRC-020")["result"] == "PASS_LOCAL"
    for pid in ("POL-GRC-001", "POL-GRC-010", "POL-GRC-015", "POL-GRC-016", "POL-GRC-017", "POL-GRC-022"):
        decisao = avaliar(pid)
        assert decisao["result"] == "HOLD"
        assert decisao["reason"] == "EXTERNAL_HOLD"
        assert decisao["authorization"] is False
    assert avaliar("POL-GRC-999")["reason"] == "ERR_POLITICA_DESCONHECIDA"


def test_validadores_reprovam_autoridade_eficacia_e_pedido_autorizado():
    agente = {
        "agent_id": "AG-TESTE",
        "allowed_effects": ["AUTHORIZE_WO"],
        "may_approve_work_order": False,
        "may_execute_correction": False,
        "may_change_status": False,
        "enunciado_oficial_armazenado": False,
    }
    assert avaliar("POL-GRC-002", {"agentes": [agente]})["result"] == "HOLD"
    controle = {
        "control_id": "CTL-TESTE",
        "template_status": "MODEL_DRAFT_NOT_IMPLEMENTED",
        "implementation_status": "NOT_VERIFIED",
        "effectiveness_status": "EFICAZ",
        "evaluation_status": "NOT_TESTED",
    }
    assert avaliar("POL-GRC-006", {"controles": [controle]})["result"] == "HOLD"
    pedido = avaliar(
        "POL-GRC-003",
        {
            "pedido": {"state": "PREAUTHORIZED", "approval_reference": None, "task_definition_id": "TD-X"},
            "definicao": {"status": "CANDIDATE_NOT_HOMOLOGATED", "allowed_effects": []},
        },
    )
    assert pedido["result"] == "HOLD"
    pedido_ok = avaliar(
        "POL-GRC-003",
        {
            "pedido": {"state": "REQUESTED", "approval_reference": None, "task_definition_id": "TD-X"},
            "definicao": {"status": "CANDIDATE_NOT_HOMOLOGATED", "allowed_effects": []},
        },
    )
    assert pedido_ok["result"] == "PASS_LOCAL"
    assert pedido_ok["authorization"] is False


def test_enunciado_oficial_e_reteste_do_mesmo_agente_ficam_em_hold():
    assert avaliar("POL-GRC-020", {"texto": "ICIF 2013 · Princípio 1: exemplo"})["result"] == "HOLD"
    assert avaliar(
        "POL-GRC-012",
        {"reteste": {"implementer_id": "A", "tester_id": "A", "result": "PASS", "evidence_ids": ["E1"]}},
    )["result"] == "HOLD"


def test_politica_grc_nao_muda_a_ordem_ja_qualificada():
    wo = carregar_wo(RAIZ / "contracts" / "work_orders" / "WO-2026_10_15_0009.json")
    assert wo.task_type == "obter"
    assert "VAL-GRC-002" not in json.loads((RAIZ / "policies" / "definicoes_tarefa.json").read_text(encoding="utf-8"))["definicoes"]["TAREFA-OBTER"]["validadores"]
