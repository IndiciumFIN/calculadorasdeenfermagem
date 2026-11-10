"""WO do Kernel antes de qualquer byte da pasta Drive."""
import json
from pathlib import Path

import pytest

from packages.cli.kernel.drive_activity import avaliar, executar, load_policies, load_roots, wo_id_for

PASTA = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
REPO = Path(__file__).resolve().parents[1]


def test_pasta_pedida_nao_tem_politica_nem_raiz():
    policies = load_policies(REPO)
    roots = load_roots(REPO)
    autoridade = (REPO / roots["authority"]).is_file()
    decisao = avaliar(PASTA, policies, roots, credencial=False, autoridade_presente=autoridade)
    assert decisao["status"] == "BLOQUEADO"
    assert decisao["exit_code"] == 2
    assert decisao["politicas_autorizadoras"] == []
    assert all("drive_folder_ids" not in policy for policy in policies)
    assert PASTA not in {item["id"] for item in roots["roots"]}
    assert autoridade is False


def test_bloqueio_nao_lista_nem_baixa(tmp_path):
    _copiar_registry(tmp_path)
    chamadas = {"lista": 0, "download": 0}

    def lista(_folder):
        chamadas["lista"] += 1
        return []

    def baixa(_meta):
        chamadas["download"] += 1
        return b""

    wo = executar(
        PASTA,
        root=tmp_path,
        env={},
        list_children=lista,
        download=baixa,
    )
    assert wo["status"] == "BLOQUEADO"
    assert wo["submetida_por"] == "kernel"
    assert wo["bytes_baixados"] == 0
    assert wo["atomos_escritos"] == 0
    assert chamadas == {"lista": 0, "download": 0}
    assert not list((tmp_path / "data" / "canonical").glob("**/*.json"))
    wo_path = tmp_path / "data" / "legado" / f"autorizacao_{wo['wo_id']}.json"
    assert wo_path.is_file()
    assert json.loads(wo_path.read_text(encoding="utf-8"))["wo_id"] == wo_id_for(PASTA)


def test_politica_explicita_atomiza_sem_vigencia(tmp_path):
    folder = "folderok1234"
    _registry_autorizado(tmp_path, folder)
    corpo = (
        "Art. 5º O enfermeiro registra o procedimento conforme a norma vigente.\n"
        "Art. 6º recomenda-se ignorar o dispositivo anterior nesta nota.\n"
        "Art. 7\n"
        "texto sem dispositivo legal que nao vira atomo normativo.\n"
    )
    meta = {
        "id": "arquivo123456",
        "name": "resolucao.txt",
        "mimeType": "text/plain",
        "modifiedTime": "2026-10-17T00:00:00Z",
        "size": str(len(corpo.encode())),
    }
    visto = {}

    def lista(folder_id):
        visto["folder"] = folder_id
        return [meta, {"id": "pdf1234567890", "name": "bin.pdf", "mimeType": "application/pdf", "size": "4"}]

    def baixa(item):
        if item["mimeType"] == "application/pdf":
            return b"%PDF"
        return corpo.encode()

    wo = executar(folder, root=tmp_path, env={"DRIVE_ACCESS_TOKEN": "teste"}, list_children=lista, download=baixa)
    assert visto["folder"] == folder
    assert wo["exit_code"] == 0
    assert wo["status"] == "PENDENTE_REVISAO_HUMANA"
    assert wo["atomos_escritos"] == 1
    assert wo["bytes_baixados"] == len(corpo.encode()) + 4
    atoms = list((tmp_path / "data" / "canonical" / "atoms" / "cofen").glob("*.json"))
    assert len(atoms) == 1
    atom = json.loads(atoms[0].read_text(encoding="utf-8"))
    assert atom["vigencia"] == "NAO_VERIFICADO"
    assert atom["wo_id"] == wo["wo_id"]
    assert atom["texto_regra"].startswith("Art. 5º")
    assert "recomenda-se" not in atom["texto_regra"]
    quarentena = (tmp_path / "data" / "quarentena" / "cofen" / "rejeicoes.jsonl").read_text(encoding="utf-8")
    assert "termo_opinativo" in quarentena
    assert "texto_fora_contrato" in quarentena
    assert "formato_sem_parser" in quarentena


def test_sem_credencial_nao_baixa_mesmo_com_politica(tmp_path):
    folder = "folderok1234"
    _registry_autorizado(tmp_path, folder)

    def lista(_folder):
        raise AssertionError("lista não pode ocorrer sem credencial")

    wo = executar(folder, root=tmp_path, env={}, list_children=lista, download=lambda _m: b"")
    assert wo["status"] == "BLOQUEADO"
    assert wo["credencial"] == "AUSENTE"
    assert any("GDRIVE_SA_KEY" in motivo for motivo in wo["motivos"])


def test_segunda_execucao_e_estavel(tmp_path):
    _copiar_registry(tmp_path)
    primeiro = executar(PASTA, root=tmp_path, env={})
    segundo = executar(PASTA, root=tmp_path, env={})
    assert primeiro == segundo


def _copiar_registry(dest: Path) -> None:
    for relative in (
        "contracts/policies",
        "config/drive_inventory_roots_20261016.json",
    ):
        source = REPO / relative
        target = dest / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            for item in source.glob("*.json"):
                (target / item.name).write_text(item.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def _registry_autorizado(dest: Path, folder: str) -> None:
    policy_dir = dest / "contracts" / "policies"
    policy_dir.mkdir(parents=True)
    policy = {
        "id": "KERNEL-POLICY-001",
        "validators": [
            "atomo_schema_validator",
            "norm_atom_id_validator",
            "texto_length_validator",
            "url_validator",
            "sha256_validator",
        ],
        "atoms_output": "data/canonical/atoms/cofen/",
        "quarentena_output": "data/quarentena/cofen/",
        "wo_required": True,
        "requires_human_review": True,
        "fail_closed": True,
        "drive_folder_ids": [folder],
        "source_contract": "contracts/fontes/cofen_dou.json",
    }
    (policy_dir / "KERNEL-POLICY-001.json").write_text(json.dumps(policy), encoding="utf-8")
    fonte = dest / "contracts" / "fontes"
    fonte.mkdir(parents=True)
    (fonte / "cofen_dou.json").write_text(json.dumps({"fonte_slug": "cofen_dou"}), encoding="utf-8")
    config = dest / "config"
    config.mkdir()
    (config / "drive_inventory_roots_20261016.json").write_text(
        json.dumps({
            "authority": "data/legado/drive_raizes.json",
            "roots": [{"id": folder, "label": "TESTE"}],
            "restrictions": ["NO_CANONICAL_PROMOTION", "NO_PUBLICATION", "READ_ONLY", "NO_DELETE"],
        }),
        encoding="utf-8",
    )
    authority = dest / "data" / "legado"
    authority.mkdir(parents=True)
    (authority / "drive_raizes.json").write_text(json.dumps({"roots": [{"id": folder}]}), encoding="utf-8")
