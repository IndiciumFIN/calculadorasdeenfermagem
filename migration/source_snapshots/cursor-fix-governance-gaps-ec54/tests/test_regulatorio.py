"""Condição normativa, fonte oficial, parecer e publicação ficam separados."""
import json
from datetime import date

import pytest
import typer
from pydantic import ValidationError

from packages.cli.main import atomizar_heuristica as process
from packages.cli.pep import RAIZ, carregar_wo
from packages.cli.regulatorio import avaliar
from packages.schemas.invariantes import AtomoBlindado

POLITICA = json.loads((RAIZ / "policies" / "regulatorio.json").read_text(encoding="utf-8"))
MIGRATION = (RAIZ / "supabase" / "migrations" / "20261014000000_governance_fixes.sql").read_text(encoding="utf-8")


def _atomo(**troca):
    base = {
        "id_atomo": "NORM-2026-010",
        "texto_regra": "Art. 3º O prazo de adequação é de 30 dias contados da publicação.",
        "dispositivo_legal": "Art. 3º",
        "norma_origem": "Resolução COFEN 800/2025",
        "link_fonte": "https://www.in.gov.br/web/dou/-/resolucao",
        "status": "Não verificado",
        "data_verificacao": None,
        "versao_contrato": "1.2.0",
    }
    base.update(troca)
    return base


def test_politicas_regulatorias_nao_entram_na_tarefa_qualificada():
    assert [item["policy_id"] for item in POLITICA["politicas"]] == [f"POL-REG-{n:03d}" for n in range(1, 6)]
    assert all(item["authorization"] is False for item in POLITICA["politicas"])
    definicao = json.loads((RAIZ / "policies" / "definicoes_tarefa.json").read_text(encoding="utf-8"))
    assert "VAL-REG-001" not in definicao["definicoes"]["TAREFA-OBTER"]["validadores"]
    wo = carregar_wo(RAIZ / "contracts" / "work_orders" / "WO-2026_10_15_0009.json")
    assert wo.task_type == "obter"


def test_planilha_nao_determina_condicao_e_dominio_oficial_determina():
    planilha = "https://docs.google.com/spreadsheets/d/16jA3isbkQuZqvsrkqU2FoIfp-JL1B8lyffNcb2f0ego"
    AtomoBlindado(**_atomo(link_fonte=planilha))
    for status in ("Vigente", "Alterado", "Revogado"):
        with pytest.raises(ValidationError, match="domínio oficial"):
            AtomoBlindado(**_atomo(status=status, data_verificacao=date(2026, 10, 15), link_fonte=planilha))
    AtomoBlindado(**_atomo(status="Revogado", data_verificacao=date(2026, 10, 15)))
    decisao = avaliar("POL-REG-002", {"atomo": _atomo(status="Alterado", data_verificacao="2026-10-15", link_fonte=planilha)})
    assert decisao["result"] == "HOLD"
    assert decisao["authorization"] is False


def test_corpus_legado_continua_candidato_sem_fonte_oficial():
    decisao = avaliar("POL-REG-001")
    assert decisao["result"] == "PASS_LOCAL"
    assert decisao["authorization"] is False
    alterado = avaliar("POL-REG-001", {"resumo": {"status_distintos": ["Vigente"], "candidatos": 1, "fontes": {}}})
    assert alterado["result"] == "HOLD"


def test_parecer_do_piloto_nao_homologa_e_o_manifesto_novo_declara_isso():
    piloto = avaliar("POL-REG-003")
    assert piloto["result"] == "HOLD"
    assert "ERR_PARECER_HOMOLOGA" in piloto["reason"]
    novo = avaliar("POL-REG-003", {"manifest": {"estagio": "raw", "promotable": True, "homologacao_juridica": False, "efeito": "CANDIDATE_ONLY"}})
    assert novo["result"] == "PASS_LOCAL"
    assert novo["authorization"] is False


def test_publicacao_nao_segue_o_status():
    assert "autorizacao_publicacao = 'AUTORIZADA'" in MIGRATION
    assert "status in ('Vigente', 'Alterado', 'Revogado')" not in MIGRATION
    por_status = avaliar("POL-REG-004", {"registro": {"status": "Vigente", "publica_por_status": True, "autorizacao_publicacao": "NAO_AUTORIZADA"}})
    assert por_status["result"] == "HOLD"
    separado = avaliar("POL-REG-004", {"registro": {"status": "Vigente", "autorizacao_publicacao": "NAO_AUTORIZADA", "publica_por_status": False}})
    assert separado["result"] == "PASS_LOCAL"
    assert separado["authorization"] is False


def test_process_conserva_numero_alem_de_quinhentos(tmp_path):
    linha = "Art. 4º " + ("texto " * 90) + "prazo de 90 dias."
    assert 500 < len(linha) <= 800
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps({
        "origem": "https://www.in.gov.br/web/dou/-/exemplo",
        "fonte_tipo": "DIARIO_OFICIAL_FEDERAL",
        "texto_sanitizado": linha,
    }), encoding="utf-8")
    out = tmp_path / "atomos.json"
    process(input_file=raw, output=out, block_on_omission=True)
    atomo = json.loads(out.read_text(encoding="utf-8"))[0]
    assert atomo["texto_regra"] == linha
    assert "90" in atomo["texto_regra"]
    assert avaliar("POL-REG-005", {"par": {"linha": linha, "texto_regra": atomo["texto_regra"]}})["result"] == "PASS_LOCAL"


def test_process_acima_do_contrato_falha_e_preserva_o_texto(tmp_path):
    linha = "Art. 5º " + ("clausula " * 90)
    assert len(linha) > 800
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps({"origem": "local", "texto_sanitizado": linha}), encoding="utf-8")
    out = tmp_path / "atomos.json"
    with pytest.raises(typer.Exit) as exc:
        process(input_file=raw, output=out, block_on_omission=True)
    assert exc.value.exit_code == 2
    atomo = json.loads(out.read_text(encoding="utf-8"))[0]
    assert atomo["texto_regra"] == linha.strip()
    assert atomo["_auditoria"]["motivo"] == "texto_acima_do_contrato"
