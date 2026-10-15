"""Migração do acervo legado: contrato, quarentena sem truncar, duplicata em conflito."""
import json
from pathlib import Path

import pytest
import typer

from packages.cli.migrate_legado import migrar
from packages.schemas.invariantes import AtomoBlindado

REPO = Path(__file__).resolve().parents[1]


def _fonte(tmp_path: Path, linhas: list[dict], nome="lote.csv", drive_id="driveTeste123"):
    fontes = tmp_path / "fontes"
    fontes.mkdir(parents=True, exist_ok=True)
    import csv
    campos = [
        "NORM_ATOM_ID", "DOCUMENT_ID", "Tipo", "Texto atômico", "Artigo/Seção",
        "Obrigação", "Aplicabilidade", "Jurisdição", "Effective from", "Effective to",
        "Concept IDs", "Status", "Validator", "Evidence span",
    ]
    with (fontes / nome).open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=campos)
        writer.writeheader()
        for linha in linhas:
            base = {c: "" for c in campos}
            base.update(linha)
            writer.writerow(base)
    manifesto = {
        "origem": "teste",
        "arquivos": [{"arquivo": nome, "drive_file_id": drive_id, "titulo": nome}],
    }
    (fontes / "manifest.json").write_text(json.dumps(manifesto), encoding="utf-8")
    return fontes


def _linha(**kwargs):
    base = {
        "NORM_ATOM_ID": "BR_FED_COFEN_RES_2024_N_00736_ART_001",
        "DOCUMENT_ID": "BR_FED_COFEN_RES_2024_N_00736",
        "Tipo": "artigo",
        "Texto atômico": "Art. 1º O Processo de Enfermagem deve ser realizado em todos os contextos de cuidado.",
        "Artigo/Seção": "Art. 1º",
        "Status": "ATOMIZADO_PENDENTE_REVISAO",
        "Evidence span": "RES_0736.pdf",
    }
    base.update(kwargs)
    return base


def test_candidato_nasce_nao_verificado_com_link_da_planilha(tmp_path):
    fontes = _fonte(tmp_path, [_linha()])
    resumo = migrar(fontes, tmp_path / "saida")
    atomos = json.loads((tmp_path / "saida" / "atomos_candidatos.json").read_text())
    assert resumo["candidatos"] == 1
    assert atomos[0]["status"] == "Não verificado"
    assert atomos[0]["data_verificacao"] is None
    assert atomos[0]["link_fonte"] == "https://docs.google.com/spreadsheets/d/driveTeste123"
    assert atomos[0]["fonte_tipo"] == "LEGADO_DRIVE"
    assert atomos[0]["id_atomo"].startswith("NORM-2024-")
    AtomoBlindado(**atomos[0])
    prov = (tmp_path / "saida" / "proveniencia.jsonl").read_text().strip()
    assert "BR_FED_COFEN_RES_2024_N_00736_ART_001" in prov
    assert "ATOMIZADO_PENDENTE_REVISAO" in prov


def test_so_quarentena_reprova_corpus_vazio(tmp_path):
    longo = "Art. 1º " + ("prazo de 30 dias. " * 80)
    fontes = _fonte(tmp_path, [_linha(**{"Texto atômico": longo})])
    with pytest.raises(typer.Exit) as exc:
        migrar(fontes, tmp_path / "saida")
    assert exc.value.exit_code == 2


def test_texto_longo_preservado_quando_ha_candidato(tmp_path):
    longo = "Art. 9º " + ("renovação em 60 dias. " * 60)
    fontes = _fonte(tmp_path, [
        _linha(),
        _linha(**{
            "NORM_ATOM_ID": "BR_FED_COFEN_RES_2024_N_00736_ART_009",
            "Texto atômico": longo,
            "Artigo/Seção": "Art. 9º",
        }),
    ])
    resumo = migrar(fontes, tmp_path / "saida")
    atomos = json.loads((tmp_path / "saida" / "atomos_candidatos.json").read_text())
    assert len(atomos) == 1
    assert resumo["motivos"]["texto_acima_do_contrato"] == 1
    quarentena = [
        json.loads(l) for l in (tmp_path / "saida" / "quarentena.jsonl").read_text().splitlines()
    ]
    assert quarentena[0]["texto_regra"] == longo.strip()
    assert len(quarentena[0]["texto_regra"]) > 800


def test_conflito_de_duplicata_nao_escolhe_lado(tmp_path):
    fontes = _fonte(tmp_path, [
        _linha(),
        _linha(**{"Texto atômico": "Art. 1º Texto divergente sobre o mesmo dispositivo legal da resolução."}),
        _linha(**{
            "NORM_ATOM_ID": "BR_FED_COFEN_RES_2024_N_00736_ART_002",
            "Texto atômico": "Art. 2º Esta Resolução entra em vigor na data de sua publicação oficial.",
            "Artigo/Seção": "Art. 2º",
        }),
    ])
    resumo = migrar(fontes, tmp_path / "saida")
    atomos = json.loads((tmp_path / "saida" / "atomos_candidatos.json").read_text())
    assert len(atomos) == 1
    assert atomos[0]["dispositivo_legal"] == "Art. 2º"
    assert resumo["motivos"]["conflito_duplicata"] == 2
    ids = [a["texto_regra"] for a in atomos]
    assert all("divergente" not in t for t in ids)


def test_duplicata_identica_deduplica(tmp_path):
    fontes = _fonte(tmp_path, [_linha(), _linha()])
    resumo = migrar(fontes, tmp_path / "saida")
    assert resumo["candidatos"] == 1
    assert resumo["motivos"]["duplicata_identica"] == 1


def test_coluna_ausente_reprova(tmp_path):
    fontes = tmp_path / "fontes"
    fontes.mkdir()
    (fontes / "lote.csv").write_text("foo,bar\n1,2\n", encoding="utf-8")
    (fontes / "manifest.json").write_text(json.dumps({
        "arquivos": [{"arquivo": "lote.csv", "drive_file_id": "abc"}],
    }), encoding="utf-8")
    with pytest.raises(typer.Exit) as exc:
        migrar(fontes, tmp_path / "saida")
    assert exc.value.exit_code == 2


def test_corpus_migrado_so_tem_nao_verificado():
    resumo_path = REPO / "data" / "legado" / "resumo.json"
    if not resumo_path.exists():
        pytest.skip("corpus legado ainda não gerado")
    resumo = json.loads(resumo_path.read_text(encoding="utf-8"))
    atomos = json.loads((REPO / "data" / "legado" / "atomos_candidatos.json").read_text(encoding="utf-8"))
    assert resumo["candidatos"] == len(atomos)
    assert resumo["status_distintos"] == ["Não verificado"]
    assert all(a["status"] == "Não verificado" and a["data_verificacao"] is None for a in atomos)
    for atomo in atomos:
        AtomoBlindado(**atomo)
