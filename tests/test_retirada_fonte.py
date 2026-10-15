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
    assert len(ledger["itens"]) == 123
    assert any(p["id_origem"] == "edge:cko-env-probe" for p in ledger["pendentes"])


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
