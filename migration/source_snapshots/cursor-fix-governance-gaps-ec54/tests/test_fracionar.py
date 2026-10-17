"""Fração em bytes. A concatenação repete o SHA-256 do original."""
import hashlib
import json
from pathlib import Path

from packages.cli.fracionar import fracionar, recomposto_confere
from packages.cli.retirada import ItemRetirada, hashes_conferem


def test_concatenacao_repete_o_original(tmp_path):
    origem = tmp_path / "grande.json"
    origem.write_bytes(b"abc" * 1000)
    pasta = tmp_path / "fracoes" / "grande.json"
    doc = fracionar(
        origem,
        pasta,
        tamanho_parte=1000,
        limite_repositorio=1500,
        id_origem="id-grande",
        caminho_obter="lote/inteiros/grande.json",
    )
    assert doc["bytes"] == 3000
    assert doc["sha256"] == hashlib.sha256(origem.read_bytes()).hexdigest()
    assert [parte["bytes"] for parte in doc["partes"]] == [1000, 1000, 1000]
    assert all(parte["bytes"] < 1500 for parte in doc["partes"])
    assert recomposto_confere(pasta / "manifesto.json", doc["sha256"])
    item = ItemRetirada(
        origem="drive",
        id_origem="id-grande",
        disposicao="IMPLANTADO",
        sha256=doc["sha256"],
        copia="fracoes/grande.json/manifesto.json",
        estado_origem="AUSENTE",
    )
    assert hashes_conferem(item, tmp_path)


def test_parte_alterada_nao_confere(tmp_path):
    origem = tmp_path / "grande.bin"
    origem.write_bytes(b"x" * 2200)
    pasta = tmp_path / "saida"
    doc = fracionar(origem, pasta, tamanho_parte=1000, limite_repositorio=1500)
    parte = pasta / "part-000"
    parte.write_bytes(b"y" * parte.stat().st_size)
    assert recomposto_confere(pasta / "manifesto.json", doc["sha256"]) is False


def test_arquivo_abaixo_do_limite_nao_fraciona(tmp_path):
    origem = tmp_path / "pequeno.json"
    origem.write_bytes(b"{}")
    try:
        fracionar(origem, tmp_path / "saida")
    except ValueError as exc:
        assert "abaixo do limite" in str(exc)
    else:
        raise AssertionError("arquivo pequeno foi fracionado")


def test_manifesto_trocado_nao_passa(tmp_path):
    origem = tmp_path / "grande.bin"
    origem.write_bytes(b"z" * 1800)
    pasta = tmp_path / "saida"
    doc = fracionar(origem, pasta, tamanho_parte=1000, limite_repositorio=1200)
    manifesto = pasta / "manifesto.json"
    bruto = json.loads(manifesto.read_text(encoding="utf-8"))
    bruto["sha256"] = "a" * 64
    manifesto.write_text(json.dumps(bruto), encoding="utf-8")
    assert recomposto_confere(manifesto, doc["sha256"]) is False
    assert recomposto_confere(manifesto, "a" * 64) is False
