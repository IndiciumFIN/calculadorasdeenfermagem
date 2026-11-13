"""Atividades de pasta Drive: WO do kernel, fail-closed e atomização."""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "packages" / "cli"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(CLI))

from packages.cli.drive_recursive_inventory import CredentialError
from packages.cli.utils import aplicar_mascara

from kernel.activities import (
    atom_id,
    classificar_caminho,
    executar_atomizar,
    executar_obter,
    executar_pasta,
    policy_maps,
    split_candidates,
    valid_policy_ids,
)
from kernel.policy_registry import get_policy
from kernel.work_order import load_work_order, work_order_id

FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
CLOCK = lambda: "2026-11-12T14:40:00+00:00"
COFEN_ID = "cofenfile0001"
RAW = """Introdução sem dispositivo legal neste arquivo.

Art. 1

Art. 8º O enfermeiro registra o procedimento no prontuário.

Art. 5º O enfermeiro registra o procedimento do CPF 123.456.789-09 no prontuário em 2026.

Art. 9º Em 2026 recomenda-se registrar o procedimento no prontuário da unidade.
"""


def _crawl(_roots, _token):
    files = [
        (COFEN_ID, "cofen_dou/resolucao.txt", "text/plain"),
        ("mixfile000001", "cofen_dou/anvisa_dou/mistura.txt", "text/plain"),
        ("cid10file0001", "cid10/capitulo.txt", "text/plain"),
        ("notasfile0001", "notas/livre.txt", "text/plain"),
        ("pdffile000001", "binario/lote.pdf", "application/pdf"),
    ]
    return {
        "items": [
            {"id": file_id, "path": path, "mime_type": mime, "kind": "file", "size_bytes": 20}
            for file_id, path, mime in files
        ]
    }


def _download(file_id, _mime, _token):
    if file_id == "pdffile000001":
        return b"%PDF-1.4"
    if file_id == COFEN_ID:
        return RAW.encode("utf-8")
    return "Art. 4º Texto suficiente para o dispositivo em 2026 no prontuário.".encode("utf-8")


def test_politicas_validas_sao_as_que_passam_no_gate():
    assert valid_policy_ids() == [
        "KERNEL-POLICY-001",
        "KERNEL-POLICY-002",
        "KERNEL-POLICY-019",
        "KERNEL-POLICY-020",
    ]
    assert get_policy("KERNEL-POLICY-001").cuarentena_output == "data/quarentena/cofen/"


def test_classificacao_deterministica():
    valid_map, invalid_map = policy_maps()
    assert classificar_caminho("cofen_dou/resolucao.txt", valid_map, invalid_map) == (
        "ok",
        "KERNEL-POLICY-001",
    )
    assert classificar_caminho("cofen_dou/anvisa_dou/x.txt", valid_map, invalid_map)[0] == (
        "politica_ambigua"
    )
    assert classificar_caminho("cid10/capitulo.txt", valid_map, invalid_map)[0] == (
        "politica_invalida"
    )
    assert classificar_caminho("notas/livre.txt", valid_map, invalid_map)[0] == (
        "politica_ausente"
    )


def test_id_de_pasta_invalido_nao_grava_wo(tmp_path):
    assert executar_pasta("../segredo", root=tmp_path, clock=CLOCK) == 2
    assert not (tmp_path / "data" / "legado").exists()


def test_sem_credencial_bloqueia_obter_e_atomizar(tmp_path):
    def explode():
        raise CredentialError(
            "Neither GDRIVE_SA_KEY nor DRIVE_ACCESS_TOKEN is configured; fail closed."
        )

    assert (
        executar_pasta(FOLDER, root=tmp_path, token_loader=explode, clock=CLOCK) == 2
    )
    obter = load_work_order(tmp_path, work_order_id("obter", FOLDER))
    atom = load_work_order(tmp_path, work_order_id("atomizar", FOLDER))
    assert obter["submitted_by"] == "kernel"
    assert obter["estado"] == "BLOQUEADO"
    assert "GDRIVE_SA_KEY" in obter["motivo"]
    assert obter["politicas_validas"] == valid_policy_ids()
    assert obter["historico"][0]["estado"] == "SUBMITTED"
    assert atom["estado"] == "BLOQUEADO"
    assert atom["depends_on"] == obter["wo_id"]
    assert atom["sha256_fonte"] is None
    assert not list((tmp_path / "data").rglob("NORM-*.json"))

    again = executar_obter(FOLDER, root=tmp_path, token_loader=explode, clock=CLOCK)
    assert again == 2
    updated = load_work_order(tmp_path, obter["wo_id"])
    assert updated["tentativas"] == obter["tentativas"] + 1
    assert len(list((tmp_path / "data" / "legado").glob("autorizacao_WO-*.json"))) == 2


def test_atomiza_so_politica_valida_e_preserva_quarentena(tmp_path):
    code = executar_pasta(
        FOLDER,
        root=tmp_path,
        token_loader=lambda: "token",
        crawl_fn=_crawl,
        download_fn=_download,
        clock=CLOCK,
    )
    assert code == 0
    masked = aplicar_mascara(RAW)
    index = next(
        i
        for i, chunk in enumerate(split_candidates(masked))
        if "123.456.789-09" not in chunk and "2026" in chunk and chunk.startswith("Art. 5")
    )
    identifier = atom_id(f"cofen_dou:{COFEN_ID}:{index:04d}", "2026")
    atom_path = tmp_path / "data" / "canonical" / "atoms" / "cofen" / f"{identifier}.json"
    atom = json.loads(atom_path.read_text(encoding="utf-8"))
    assert atom["vigencia"] == "NAO_VERIFICADO"
    assert atom["wo_id"].startswith("CE-WO-ATOMIZAR-")
    assert "123.456.789-09" not in atom_path.read_text(encoding="utf-8")
    assert "[CPF_REDACT]" in atom["texto_regra"]
    assert list((tmp_path / "data" / "canonical").rglob("*.json")) == [atom_path]

    manifesto = json.loads(
        (tmp_path / "data" / "raw" / "drive" / FOLDER / "MANIFESTO.json").read_text(
            encoding="utf-8"
        )
    )
    assert all("_text" not in item for item in manifesto["items"])
    blob = json.dumps(manifesto)
    assert "123.456.789-09" not in blob

    quarentena = (
        tmp_path / "data" / "quarentena" / "cofen" / "quarentena.jsonl"
    ).read_text(encoding="utf-8")
    assert "texto_curto" in quarentena
    assert "ano_ausente" in quarentena
    assert "termo_opinativo" in quarentena
    assert "sem_dispositivo" in quarentena
    assert "123.456.789-09" not in quarentena
    found = set()
    for path in (tmp_path / "data" / "quarentena").rglob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            found.add(json.loads(line)["motivo"])
    assert {"politica_ambigua", "politica_invalida", "politica_ausente", "parser_ausente"} <= found

    antes = atom_path.read_text(encoding="utf-8")
    linhas = sum(
        len(path.read_text(encoding="utf-8").splitlines())
        for path in (tmp_path / "data" / "quarentena").rglob("*.jsonl")
    )
    assert executar_atomizar(FOLDER, root=tmp_path, clock=CLOCK) == 0
    assert atom_path.read_text(encoding="utf-8") == antes
    linhas_depois = sum(
        len(path.read_text(encoding="utf-8").splitlines())
        for path in (tmp_path / "data" / "quarentena").rglob("*.jsonl")
    )
    assert linhas_depois == linhas
    atom_wo = load_work_order(tmp_path, work_order_id("atomizar", FOLDER))
    assert atom_wo["contagens"]["dedup"] == 1


def test_conflito_de_sha_nao_sobrescreve(tmp_path):
    masked = aplicar_mascara(RAW)
    index = next(
        i
        for i, chunk in enumerate(split_candidates(masked))
        if chunk.startswith("Art. 5")
    )
    identifier = atom_id(f"cofen_dou:{COFEN_ID}:{index:04d}", "2026")
    destino = tmp_path / "data" / "canonical" / "atoms" / "cofen" / f"{identifier}.json"
    destino.parent.mkdir(parents=True)
    destino.write_text('{"sha256_texto": "diferente", "vigencia": "NAO_VERIFICADO"}\n', encoding="utf-8")
    assert (
        executar_pasta(
            FOLDER,
            root=tmp_path,
            token_loader=lambda: "token",
            crawl_fn=_crawl,
            download_fn=_download,
            clock=CLOCK,
        )
        == 0
    )
    assert "diferente" in destino.read_text(encoding="utf-8")
    conflitos = (
        tmp_path / "data" / "quarentena" / "cofen" / "quarentena.jsonl"
    ).read_text(encoding="utf-8")
    assert "conflito_duplicata" in conflitos


def test_html_de_login_bloqueia_sem_atomo(tmp_path):
    def crawl(_roots, _token):
        return {
            "items": [
                {
                    "id": "loginfile0001",
                    "path": "cofen_dou/pagina.txt",
                    "mime_type": "text/plain",
                    "kind": "file",
                }
            ]
        }

    def download(_file_id, _mime, _token):
        return b"<html><body>Sign in</body></html>"

    assert (
        executar_pasta(
            FOLDER,
            root=tmp_path,
            token_loader=lambda: "token",
            crawl_fn=crawl,
            download_fn=download,
            clock=CLOCK,
        )
        == 2
    )
    obter = load_work_order(tmp_path, work_order_id("obter", FOLDER))
    assert obter["estado"] == "BLOQUEADO"
    assert "html_interstitial" in obter["motivo"]
    assert not list(tmp_path.rglob("NORM-*.json"))
