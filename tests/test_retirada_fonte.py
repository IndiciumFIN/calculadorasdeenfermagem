"""Invariante FONTE_RETIRADA: implantação e descarte retiram a origem; conflito bloqueia."""
import json
from pathlib import Path

import pytest
import typer

from packages.cli.retirada import ItemRetirada, decidir, hashes_conferem, verificar_ledger

REPO = Path(__file__).resolve().parents[1]


def test_implantado_com_hash_igual_e_origem_ausente_retira():
    item = ItemRetirada(
        origem="drive",
        id_origem="abc123drive",
        disposicao="IMPLANTADO",
        sha256="a" * 64,
        copia="fonte.csv",
        estado_origem="AUSENTE",
    )
    assert decidir(item) == "RETIRAR"


def test_hash_obrigatorio_para_implantado():
    with pytest.raises(ValueError):
        ItemRetirada(
            origem="drive",
            id_origem="abc123drive",
            disposicao="IMPLANTADO",
            estado_origem="AUSENTE",
        )


def test_origem_ainda_presente_bloqueia():
    item = ItemRetirada(
        origem="drive",
        id_origem="abc123drive",
        disposicao="IMPLANTADO",
        sha256="b" * 64,
        copia="fonte.csv",
        estado_origem="PRESENTE",
    )
    assert decidir(item) == "BLOQUEAR"


def test_descarte_sem_motivo_reprova():
    with pytest.raises(ValueError):
        ItemRetirada(
            origem="supabase",
            id_origem="edge:exemplo",
            disposicao="DESCARTADO",
            estado_origem="AUSENTE",
            motivo_descarte="curto",
        )


def test_copia_com_hash_divergente_nao_confere(tmp_path):
    arquivo = tmp_path / "fonte.csv"
    arquivo.write_bytes(b"conteudo-real")
    item = ItemRetirada(
        origem="drive",
        id_origem="abc123drive",
        disposicao="IMPLANTADO",
        sha256="c" * 64,
        copia="fonte.csv",
        estado_origem="AUSENTE",
    )
    assert hashes_conferem(item, tmp_path) is False


def test_censo_registra_os_dois_projetos_e_bloqueia_exclusao():
    censo = json.loads((REPO / "data" / "legado" / "supabase_normativos.json").read_text(encoding="utf-8"))
    por_id = {p["id"]: p for p in censo["projetos"]}
    assert set(por_id) == {"aevqrmkdhffmursdtcmo", "bsawvgyideporzailnys"}
    ativo = por_id["aevqrmkdhffmursdtcmo"]
    assert ativo["esquema_regulatory"] is True
    assert ativo["contagens"]["regulatory.instruments"] == 0
    assert ativo["exclusao"] == "BLOQUEAR"
    pausado = por_id["bsawvgyideporzailnys"]
    assert len(pausado["topicos_que_nomeiam_norma"]) == 23
    assert len(pausado["arquivos"]) == 4
    assert all(a["sha256"] is None and a["bytes"] == 179679 for a in pausado["arquivos"])
    assert pausado["exclusao"] == "BLOQUEAR"
    ledger = json.loads((REPO / "data" / "legado" / "retirada_fontes.json").read_text(encoding="utf-8"))
    texto = " ".join(ledger["fora_da_regra"])
    assert "sem acervo" not in texto
    assert "bsawvgyideporzailnys" in texto


def test_quatro_raizes_do_drive_bloqueiam_exclusao():
    doc = json.loads((REPO / "data" / "legado" / "drive_raizes.json").read_text(encoding="utf-8"))
    por_id = {r["id"]: r for r in doc["raizes"]}
    assert set(por_id) == {
        "1FDBAMQ3-WT-8l6xU0664u7QjABd0FbEH",
        "1xhNiG35r_1_Cb211b3oz5IvcCE_Ql0K7",
        "1l519_P-9o6bnQcItydKvEEDpEYeE8R8s",
        "1c9vErI_It3XwzAcAFOnbxw9V0Mn6xfB9",
    }
    assert all(r["exclusao"] == "BLOQUEAR" for r in por_id.values())
    arvores = por_id["1FDBAMQ3-WT-8l6xU0664u7QjABd0FbEH"]["arvores_cofen"]
    assert {a["id"] for a in arvores} == {
        "1CuNVo6TSwMcEyHabRhCVnBJ8W4dRfo7R",
        "1LP6uKkBJ5y9VDEQJTxIPyaEFKDLQNWxo",
    }
    assert por_id["1FDBAMQ3-WT-8l6xU0664u7QjABd0FbEH"]["acesso"] == "anyone_reader"
    assert por_id["1l519_P-9o6bnQcItydKvEEDpEYeE8R8s"]["acesso"] == "anyone_reader"
    assert por_id["1xhNiG35r_1_Cb211b3oz5IvcCE_Ql0K7"]["acesso"] == "somente_dono"
    assert "não prova pasta vazia" in por_id["1c9vErI_It3XwzAcAFOnbxw9V0Mn6xfB9"]["nota"]


def test_ledger_do_repositorio_confere_com_as_copias():
    ledger = json.loads((REPO / "data" / "legado" / "retirada_fontes.json").read_text(encoding="utf-8"))
    assert verificar_ledger(ledger, REPO) == []
    assert len(ledger["itens"]) == 152
    assert any(p["id_origem"] == "edge:cko-env-probe" for p in ledger["pendentes"])
    assert ledger["lixeira"]["mover_implantado"] == "EFETUADO"
    assert ledger["lixeira"]["esvaziar"] == "BLOQUEAR"
    assert ledger["lixeira"]["esvaziar_executor"] == "somente_humano"
    politica = json.loads((REPO / "policies" / "retirada_fonte.json").read_text(encoding="utf-8"))
    assert politica["esvaziar_lixeira"] == "BLOQUEAR"
    assert politica["esvaziar_lixeira_executor"] == "somente_humano"
    assert {item["titulo"] for item in ledger["pastas_vazias"]} == {
        "cid10",
        "sepse",
        "ferimentos",
        "medlineplus",
    }
    assert all(item["estado"] == "AUSENTE" for item in ledger["pastas_vazias"])


def test_raw_nao_repete_nome_e_tamanho_das_wo_ate_0040():
    doc = json.loads((REPO / "data" / "legado" / "comparacao_raw_wo_0040.json").read_text(encoding="utf-8"))
    assert doc["recorte"] == "WO-2026_10_15_0001 a WO-2026_10_15_0040"
    assert doc["work_orders_sem_arquivo"] == ["0037", "0038", "0039", "0040"]
    assert doc["arquivos_implantados"] == 101
    assert doc["listagens_raw_fechadas"] == 50
    assert doc["mesmo_nome_e_mesmo_tamanho"] == 0
    assert len(doc["mesmo_nome_tamanho_diferente"]) == 16
    assert len(doc["nome_reescrito_tamanho_diferente"]) == 6
    assert len(doc["sem_nome_nas_wo_ate_0040"]) == 28
    for item in doc["mesmo_nome_tamanho_diferente"] + doc["nome_reescrito_tamanho_diferente"]:
        assert item["bytes_drive"] != item["bytes_implantado"]


def test_cli_reprova_ledger_inconsistente(tmp_path):
    ledger = {
        "invariante": "FONTE_RETIRADA",
        "itens": [
            {
                "origem": "drive",
                "id_origem": "abc123drive",
                "disposicao": "IMPLANTADO",
                "sha256": "d" * 64,
                "copia": "ausente.csv",
                "estado_origem": "AUSENTE",
            }
        ],
        "pendentes": [],
    }
    erros = verificar_ledger(ledger, tmp_path)
    assert any("SHA-256" in erro for erro in erros)
    with pytest.raises(typer.Exit) as exc:
        from packages.cli.retirada import verificar
        caminho = tmp_path / "ledger.json"
        caminho.write_text(json.dumps(ledger), encoding="utf-8")
        verificar(ledger=caminho, raiz=tmp_path)
    assert exc.value.exit_code == 2
