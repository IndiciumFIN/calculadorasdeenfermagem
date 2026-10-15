"""Extração em bytes. O compactado permanece e o membro grande vira fração."""
import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from packages.cli.extrair_compactado import extrair_compactado
from packages.cli.fracionar import recomposto_confere


def _zip(caminho: Path, membros: dict[str, bytes]) -> None:
    with zipfile.ZipFile(caminho, "w") as compactado:
        for nome, corpo in membros.items():
            compactado.writestr(nome, corpo)


def test_membro_novo_e_gravado_e_o_zip_permanece(tmp_path):
    arquivo = tmp_path / "fonte.zip"
    _zip(arquivo, {"tabela.csv": b"a,b\n1,2\n"})
    doc = extrair_compactado(arquivo, tmp_path / "extraido")
    assert arquivo.is_file()
    assert doc["membros"][0]["disposicao"] == "GRAVADO"
    assert (tmp_path / "extraido" / "tabela.csv").read_bytes() == b"a,b\n1,2\n"
    assert doc["membros"][0]["sha256"] == hashlib.sha256(b"a,b\n1,2\n").hexdigest()


def test_membro_identico_nao_e_gravado_de_novo(tmp_path):
    corpo = b"mesmos-bytes"
    arquivo = tmp_path / "fonte.zip"
    _zip(arquivo, {"cid.csv": corpo})
    doc = extrair_compactado(
        arquivo,
        tmp_path / "extraido",
        indice={hashlib.sha256(corpo).hexdigest(): "raw/cid.csv"},
    )
    assert doc["membros"][0]["disposicao"] == "IDENTICO_EXISTENTE"
    assert doc["membros"][0]["copia_existente"] == "raw/cid.csv"
    assert not (tmp_path / "extraido" / "cid.csv").exists()


def test_membro_grande_vira_fracao_sem_monolito(tmp_path):
    arquivo = tmp_path / "grande.zip"
    _zip(arquivo, {"massa.json": b"z" * 2500})
    doc = extrair_compactado(
        arquivo,
        tmp_path / "extraido",
        tamanho_parte=1000,
        limite_repositorio=1500,
    )
    membro = doc["membros"][0]
    assert membro["disposicao"] == "FRACIONADO"
    assert membro["partes"] == 3
    pasta = tmp_path / "extraido" / "fracoes" / "massa.json"
    assert recomposto_confere(pasta / "manifesto.json", membro["sha256"])
    assert not (tmp_path / "extraido" / "inteiros" / "massa.json").exists()


def test_membro_com_travessia_falha(tmp_path):
    arquivo = tmp_path / "mau.zip"
    _zip(arquivo, {"../fora.txt": b"x"})
    with pytest.raises(ValueError, match="fora do arquivo"):
        extrair_compactado(arquivo, tmp_path / "extraido")


def test_analise_gravada_confere_com_o_retorno(tmp_path):
    arquivo = tmp_path / "fonte.zip"
    _zip(arquivo, {"a.txt": b"a"})
    doc = extrair_compactado(arquivo, tmp_path / "extraido")
    gravado = json.loads((tmp_path / "extraido" / "analise.json").read_text(encoding="utf-8"))
    assert gravado == doc
