"""A tarefa só corre com Work Order. Referência não vira átomo."""
import json
from pathlib import Path

import pytest
import typer

from packages.cli.kernel import atomizar, obter, retirar, validar
from packages.cli.pep import carregar_wo

SHA = "a" * 64
DEFINICAO = {
    "obter": "TAREFA-OBTER",
    "atomizar": "TAREFA-ATOMIZAR",
    "validar": "TAREFA-VALIDAR",
    "retirar": "TAREFA-RETIRAR",
}
ORDEM = {
    "obter": "WO-2026_10_15_0001",
    "atomizar": "WO-2026_10_15_0002",
    "validar": "WO-2026_10_15_0003",
    "retirar": "WO-2026_10_15_0004",
}


def _base(task_type: str, *, sha: str | None, classe: str = "REFERENCIA") -> dict:
    entrada = {
        "id_origem": "id-origem-1",
        "caminho": "cid10/capitulos.csv",
        "classe": classe,
    }
    if sha is not None:
        entrada["sha256"] = sha
    doc = {
        "id": ORDEM[task_type],
        "contract_version": "CKO-TAREFA-1.0.0",
        "authorized_by": "IndiciumFIN",
        "task_id": DEFINICAO[task_type],
        "task_version": "1.0.0",
        "task_type": task_type,
        "policy_version": "1.0.0",
        "state": "PREAUTHORIZED",
        "entradas": [entrada],
        "parametros": {},
    }
    if task_type in {"validar", "retirar"}:
        doc["checker_id"] = "kernel-validar"
    if task_type == "validar":
        doc["parametros"] = {"atomizar_work_order": ORDEM["atomizar"]}
    if task_type == "retirar":
        doc["parametros"] = {"parecer_work_order": ORDEM["validar"]}
    return doc


def _gravar(tmp_path: Path, doc: dict) -> Path:
    caminho = tmp_path / "wo.json"
    caminho.write_text(json.dumps(doc), encoding="utf-8")
    return caminho


def test_tarefa_nao_qualificada_reprova(tmp_path):
    doc = _base("obter", sha=None)
    doc["task_id"] = "TAREFA-T07"
    doc["task_version"] = "0.0.0"
    doc["task_type"] = "set-status"
    with pytest.raises(ValueError, match="não qualificada"):
        carregar_wo(_gravar(tmp_path, doc))


def test_wo_nao_redefine_procedimento(tmp_path):
    doc = _base("obter", sha=None)
    doc["task_type"] = "atomizar"
    with pytest.raises(ValueError, match="não redefine"):
        carregar_wo(_gravar(tmp_path, doc))


def test_definicao_ausente_reprova(tmp_path):
    doc = _base("obter", sha=None)
    doc["task_id"] = "TAREFA-INEXISTENTE"
    with pytest.raises(ValueError, match="definição ausente"):
        carregar_wo(_gravar(tmp_path, doc))


def test_wos_do_repositorio_apontam_para_definicao_qualificada():
    from packages.cli.pep import RAIZ

    pasta = RAIZ / "contracts" / "work_orders"
    vistos = sorted(pasta.glob("WO-2026_10_15_*.json"))
    assert len(vistos) == 66
    for caminho in vistos:
        wo = carregar_wo(caminho)
        assert wo.task_id.startswith("TAREFA-")
        assert wo.task_version == "1.0.0"


def test_id_fora_do_padrao_reprova(tmp_path):
    doc = _base("obter", sha=None)
    doc["id"] = "WO-2026_13_15_0001"
    with pytest.raises(ValueError, match="data da Work Order"):
        carregar_wo(_gravar(tmp_path, doc))
    doc["id"] = "WO-26_10_15_0001"
    with pytest.raises(ValueError):
        carregar_wo(_gravar(tmp_path, doc))


def test_wo_ausente_sai_2(tmp_path):
    with pytest.raises(typer.Exit) as exc:
        obter(work_order=tmp_path / "nao-existe.json")
    assert exc.value.exit_code == 2


def test_obter_rejeita_sha_declarado(tmp_path):
    caminho = _gravar(tmp_path, _base("obter", sha=SHA))
    with pytest.raises(ValueError, match="sha256"):
        carregar_wo(caminho)
    with pytest.raises(typer.Exit) as exc:
        obter(work_order=caminho)
    assert exc.value.exit_code == 2


def test_checker_igual_ao_autorizador_reprova(tmp_path):
    doc = _base("validar", sha=SHA)
    doc["checker_id"] = doc["authorized_by"]
    caminho = _gravar(tmp_path, doc)
    with pytest.raises(ValueError, match="checker_id"):
        carregar_wo(caminho)


def test_referencia_nao_vira_atomo(tmp_path, monkeypatch):
    saida = tmp_path / "saida"
    monkeypatch.setattr("packages.cli.kernel.SAIDA", saida)

    def baixar(file_id, dest: Path):
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(f"tabela-{file_id}".encode())

    monkeypatch.setattr("packages.cli.kernel._baixar", baixar)
    obter(work_order=_gravar(tmp_path, _base("obter", sha=None)))
    manifesto = json.loads((saida / "manifesto_obter_WO-2026_10_15_0001.json").read_text(encoding="utf-8"))
    sha = manifesto["itens"][0]["sha256"]
    assert len(sha) == 64

    atom = _base("atomizar", sha=sha)
    atomizar(work_order=_gravar(tmp_path, atom))
    feito = json.loads((saida / "manifesto_atomizar_WO-2026_10_15_0002.json").read_text(encoding="utf-8"))
    assert feito["itens"][0]["resultado"] == "NAO_APLICAVEL"
    assert feito["itens"][0]["atomos"] == []

    val = _base("validar", sha=sha)
    val["id"] = "WO-2026_10_15_0003"
    validar(work_order=_gravar(tmp_path, val))
    parecer = json.loads((saida / "parecer_validar_WO-2026_10_15_0003.json").read_text(encoding="utf-8"))
    assert parecer["itens"][0]["resultado"] == "PASS"
    assert parecer["itens"][0]["atomos"] == 0
    assert parecer["checker_id"] != parecer["authorized_by"]

    retirar(work_order=_gravar(tmp_path, _base("retirar", sha=sha)))
    autorizacao = json.loads((saida / "autorizacao_retirada_WO-2026_10_15_0004.json").read_text(encoding="utf-8"))
    assert autorizacao["ids"] == ["id-origem-1"]


def test_hash_divergente_falha_fechado(tmp_path, monkeypatch):
    saida = tmp_path / "saida"
    monkeypatch.setattr("packages.cli.kernel.SAIDA", saida)
    monkeypatch.setattr(
        "packages.cli.kernel._baixar",
        lambda file_id, dest: dest.parent.mkdir(parents=True, exist_ok=True) or dest.write_bytes(b"real"),
    )
    obter(work_order=_gravar(tmp_path, _base("obter", sha=None)))
    with pytest.raises(typer.Exit) as exc:
        atomizar(work_order=_gravar(tmp_path, _base("atomizar", sha="b" * 64)))
    assert exc.value.exit_code == 2
    assert not (saida / "manifesto_atomizar_WO-2026_10_15_0002.json").exists()


def test_ato_sem_extrator_nao_inventa_atomo(tmp_path, monkeypatch):
    saida = tmp_path / "saida"
    monkeypatch.setattr("packages.cli.kernel.SAIDA", saida)
    monkeypatch.setattr(
        "packages.cli.kernel._baixar",
        lambda file_id, dest: dest.parent.mkdir(parents=True, exist_ok=True) or dest.write_bytes(b"ato"),
    )
    obter(work_order=_gravar(tmp_path, _base("obter", sha=None, classe="ATO")))
    sha = json.loads((saida / "manifesto_obter_WO-2026_10_15_0001.json").read_text(encoding="utf-8"))["itens"][0]["sha256"]
    with pytest.raises(typer.Exit) as exc:
        atomizar(work_order=_gravar(tmp_path, _base("atomizar", sha=sha, classe="ATO")))
    assert exc.value.exit_code == 2
    assert not (saida / "manifesto_atomizar_WO-2026_10_15_0002.json").exists()


def test_retirar_sem_pass_falha(tmp_path, monkeypatch):
    saida = tmp_path / "saida"
    saida.mkdir()
    monkeypatch.setattr("packages.cli.kernel.SAIDA", saida)
    (saida / "cid10").mkdir()
    arquivo = saida / "cid10" / "capitulos.csv"
    arquivo.write_bytes(b"tabela")
    import hashlib

    sha = hashlib.sha256(arquivo.read_bytes()).hexdigest()
    (saida / "parecer_validar_WO-2026_10_15_0003.json").write_text(
        json.dumps(
            {
                "work_order": "WO-2026_10_15_0003",
                "itens": [{"id_origem": "id-origem-1", "resultado": "FAIL", "sha256": sha}],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(typer.Exit) as exc:
        retirar(work_order=_gravar(tmp_path, _base("retirar", sha=sha)))
    assert exc.value.exit_code == 2
    assert not (saida / "autorizacao_retirada_WO-2026_10_15_0004.json").exists()


def test_confirmacao_de_varredura_baixa_o_arquivo(tmp_path, monkeypatch):
    saida = tmp_path / "saida"
    monkeypatch.setattr("packages.cli.kernel.SAIDA", saida)
    html = """<!DOCTYPE html><html><head><title>Google Drive - Virus scan warning</title></head>
    <body><form id="download-form" action="https://drive.usercontent.google.com/download" method="get">
    <input type="hidden" name="id" value="id-origem-1">
    <input type="hidden" name="export" value="download">
    <input type="hidden" name="confirm" value="t">
    <input type="hidden" name="uuid" value="uuid-deste-pedido">
    </form></body></html>""".encode()
    pedidos = []

    class Resposta:
        def __init__(self, content):
            self.status_code = 200
            self.content = content

    def get(url, **kwargs):
        pedidos.append(url)
        if len(pedidos) == 1:
            return Resposta(html)
        return Resposta(b"print('coleta')\n")

    monkeypatch.setattr("packages.cli.kernel.requests.get", get)
    obter(work_order=_gravar(tmp_path, _base("obter", sha=None)))
    assert len(pedidos) == 2
    assert "id=id-origem-1" in pedidos[1]
    assert "confirm=t" in pedidos[1]
    assert (saida / "cid10" / "capitulos.csv").read_bytes() == b"print('coleta')\n"


def test_download_html_nao_grava_arquivo(tmp_path, monkeypatch):
    saida = tmp_path / "saida"
    monkeypatch.setattr("packages.cli.kernel.SAIDA", saida)

    class Resposta:
        status_code = 200
        content = b"<!DOCTYPE html><html>confirme o download</html>"

    monkeypatch.setattr("packages.cli.kernel.requests.get", lambda *args, **kwargs: Resposta())
    with pytest.raises(typer.Exit) as exc:
        obter(work_order=_gravar(tmp_path, _base("obter", sha=None)))
    assert exc.value.exit_code == 2
    assert not (saida / "manifesto_obter_WO-2026_10_15_0001.json").exists()
    assert not (saida / "cid10" / "capitulos.csv").exists()
