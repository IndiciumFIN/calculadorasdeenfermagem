"""A cópia do Drive recusa escrita e a checagem não escolhe lado."""
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def carregar(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_migrar_drive_nao_copia(tmp_path, monkeypatch, capsys):
    origem = tmp_path / "origem"
    origem.mkdir()
    (origem / "ato.txt").write_text("texto", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["migrar_drive.py", str(origem)])
    modulo = carregar("migrar_drive", REPO / "scripts" / "migrar_drive.py")
    assert modulo.main() == 2
    assert not (tmp_path / "data").exists()
    assert "cópia recusada" in capsys.readouterr().out


def test_duplicata_identica_nao_e_conflito(tmp_path, monkeypatch, capsys):
    um = tmp_path / "um" / "lei.txt"
    dois = tmp_path / "dois" / "copia.txt"
    um.parent.mkdir()
    dois.parent.mkdir()
    um.write_text("mesmo texto", encoding="utf-8")
    dois.write_text("mesmo texto", encoding="utf-8")
    modulo = carregar("drive_duplicidade_check", REPO / "scripts" / "drive_duplicidade_check.py")
    monkeypatch.setattr(sys, "argv", ["drive_duplicidade_check.py", str(tmp_path)])
    assert modulo.main() == 0
    relatorio = json.loads(capsys.readouterr().out)
    assert relatorio["status"] == "PASS"
    assert relatorio["duplicatas_identicas"] == 1
    assert relatorio["conflitos"] == 0


def test_mesmo_nome_com_conteudo_diferente_nao_escolhe_lado(tmp_path, monkeypatch, capsys):
    um = tmp_path / "um" / "lei.txt"
    dois = tmp_path / "dois" / "lei.txt"
    um.parent.mkdir()
    dois.parent.mkdir()
    um.write_text("texto a", encoding="utf-8")
    dois.write_text("texto b", encoding="utf-8")
    modulo = carregar("drive_duplicidade_check", REPO / "scripts" / "drive_duplicidade_check.py")
    monkeypatch.setattr(sys, "argv", ["drive_duplicidade_check.py", str(tmp_path)])
    assert modulo.main() == 2
    relatorio = json.loads(capsys.readouterr().out)
    assert relatorio["status"] == "FAIL"
    assert relatorio["conflitos"] == 1
    assert relatorio["detalhes_conflitos"][0]["tipo"] == "mesmo_nome_conteudo_diferente"
    assert set(relatorio["detalhes_conflitos"][0]["caminhos"]) == {"um/lei.txt", "dois/lei.txt"}
