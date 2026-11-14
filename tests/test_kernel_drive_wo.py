"""WO do Kernel antes de obter ou atomizar uma pasta do Drive."""
import json
from pathlib import Path

from packages.cli.kernel.core import Kernel
from packages.cli.kernel.drive_cycle import media_url, run_drive_folder

REPO = Path(__file__).resolve().parents[1]
FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
TOKEN = "token-secreto-de-teste"
WHEN = "2026-11-14T00:41:00+00:00"


def _policy(identifier: str, folder: str) -> dict:
    return {
        "id": identifier,
        "validators": [
            "atomo_schema_validator",
            "norm_atom_id_validator",
            "texto_length_validator",
            "url_validator",
        ],
        "drive_folder_ids": [folder],
        "atoms_output": "atoms",
        "quarentena_output": "quarentena",
        "source_contract": "contracts/fontes/cofen_dou.json",
    }


def _roots(folder: str) -> dict:
    return {
        "scope": "authorized_bytes",
        "roots": [{"id": folder, "label": "LOTE"}],
        "restrictions": ["READ_ONLY", "NO_DELETE"],
    }


def _texts(root: Path) -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in root.rglob("*") if path.is_file())


def test_kernel_admits_only_policies_whose_validators_pass():
    kernel = Kernel()
    assert kernel.admission("KERNEL-POLICY-001")[0] is True
    assert kernel.admission("KERNEL-POLICY-002")[0] is True
    assert kernel.admission("KERNEL-POLICY-019")[0] is True
    assert kernel.admission("KERNEL-POLICY-020")[0] is True
    failed, reason = kernel.admission("KERNEL-POLICY-003")
    assert failed is False
    assert "test_suite reprovou" in reason


def test_drive_folder_blocks_without_downloading(tmp_path):
    calls = {"list": 0, "download": 0}

    def probe(folder_id):
        document = json.loads(
            (tmp_path / "wo" / f"autorizacao_WO-OBTER-{folder_id}.json").read_text(encoding="utf-8")
        )
        assert document["estado"] == "EM_AVALIACAO"
        assert document["submitted_by"] == "kernel"
        return {"list_http": 403, "page_http": 200, "page_host": "accounts.google.com"}

    def lister(folder_id, env):
        calls["list"] += 1
        return []

    def fetcher(item, env):
        calls["download"] += 1
        return b""

    code = run_drive_folder(
        f"https://drive.google.com/drive/folders/{FOLDER}?hl=pt-br",
        root=tmp_path,
        policies_dir=REPO / "contracts" / "policies",
        roots_path=REPO / "config" / "drive_inventory_roots_20261016.json",
        wo_dir=tmp_path / "wo",
        evidence_path=tmp_path / "evidence.json",
        env={"DRIVE_ACCESS_TOKEN": TOKEN},
        clock=lambda: WHEN,
        probe=probe,
        list_children=lister,
        download_bytes=fetcher,
    )
    assert code == 2
    assert calls == {"list": 0, "download": 0}
    evidence = json.loads((tmp_path / "evidence.json").read_text(encoding="utf-8"))
    assert evidence["bytes_baixados"] == 0
    assert evidence["atomos_escritos"] == 0
    assert evidence["politicas_gate_aprovado"] == [
        "KERNEL-POLICY-001",
        "KERNEL-POLICY-002",
        "KERNEL-POLICY-019",
        "KERNEL-POLICY-020",
    ]
    assert evidence["probe"]["list_http"] == 403
    assert evidence["probe"]["page_host"] == "accounts.google.com"
    obter = json.loads(
        (tmp_path / "wo" / f"autorizacao_WO-OBTER-{FOLDER}.json").read_text(encoding="utf-8")
    )
    atom = json.loads(
        (tmp_path / "wo" / f"autorizacao_WO-ATOMIZAR-{FOLDER}.json").read_text(encoding="utf-8")
    )
    assert obter["estado"] == "BLOQUEADO"
    assert atom["estado"] == "BLOQUEADO"
    assert atom["depends_on"] == obter["wo_id"]
    assert "NO_CANONICAL_PROMOTION" in " ".join(atom["motivos"])
    assert TOKEN not in _texts(tmp_path)
    assert not (tmp_path / "atoms").exists()


def test_authorized_text_is_atomized_and_masked(tmp_path):
    folder = "pastaAutorizada01"
    policies = tmp_path / "policies"
    policies.mkdir()
    (policies / "KERNEL-POLICY-001.json").write_text(
        json.dumps(_policy("KERNEL-POLICY-001", folder)),
        encoding="utf-8",
    )
    (tmp_path / "roots.json").write_text(json.dumps(_roots(folder)), encoding="utf-8")
    text = (
        "Art. 5o O enfermeiro registra o CPF 123.456.789-09 no prontuario assistencial.\n"
    )
    seen = {}

    def lister(folder_id, env):
        seen["token"] = env.get("DRIVE_ACCESS_TOKEN")
        return [
            {
                "id": "arq1",
                "name": "norma.txt",
                "mimeType": "text/plain",
                "size": len(text.encode()),
            }
        ]

    code = run_drive_folder(
        folder,
        root=tmp_path,
        policies_dir=policies,
        roots_path=tmp_path / "roots.json",
        wo_dir=tmp_path / "wo",
        evidence_path=tmp_path / "evidence.json",
        env={"DRIVE_ACCESS_TOKEN": TOKEN},
        clock=lambda: WHEN,
        probe=lambda _folder: (_ for _ in ()).throw(AssertionError("probe")),
        list_children=lister,
        download_bytes=lambda item, env: text.encode(),
    )
    assert code == 0
    assert seen["token"] == TOKEN
    atoms = list((tmp_path / "atoms").glob("*.json"))
    assert len(atoms) == 1
    body = json.loads(atoms[0].read_text(encoding="utf-8"))
    assert body["vigencia"] == "NAO_VERIFICADO"
    assert body["fonte_slug"] == "cofen_dou"
    assert body["wo_id"] == f"CE-WO-ATOMIZAR-{folder}"
    assert "[CPF_REDACT]" in body["texto_regra"]
    assert "123.456.789-09" not in body["texto_regra"]
    assert TOKEN not in _texts(tmp_path)
    obter = json.loads(
        (tmp_path / "wo" / f"autorizacao_WO-OBTER-{folder}.json").read_text(encoding="utf-8")
    )
    assert obter["estado"] == "EXECUTADA"
    assert obter["arquivos"][0]["sha256"]


def test_two_policies_do_not_download(tmp_path):
    folder = "pastaAmbiguamente01"
    policies = tmp_path / "policies"
    policies.mkdir()
    for identifier in ("KERNEL-POLICY-001", "KERNEL-POLICY-002"):
        (policies / f"{identifier}.json").write_text(
            json.dumps(_policy(identifier, folder)),
            encoding="utf-8",
        )
    (tmp_path / "roots.json").write_text(json.dumps(_roots(folder)), encoding="utf-8")
    calls = {"list": 0}

    def lister(folder_id, env):
        calls["list"] += 1
        return []

    code = run_drive_folder(
        folder,
        root=tmp_path,
        policies_dir=policies,
        roots_path=tmp_path / "roots.json",
        wo_dir=tmp_path / "wo",
        evidence_path=tmp_path / "evidence.json",
        env={"DRIVE_ACCESS_TOKEN": TOKEN},
        clock=lambda: WHEN,
        probe=lambda _folder: {"list_http": 200, "page_host": "drive.google.com"},
        list_children=lister,
        download_bytes=lambda item, env: b"",
    )
    assert code == 2
    assert calls["list"] == 0
    obter = json.loads(
        (tmp_path / "wo" / f"autorizacao_WO-OBTER-{folder}.json").read_text(encoding="utf-8")
    )
    assert any("Mais de uma política" in motivo for motivo in obter["motivos"])


def test_pdf_is_not_atomized(tmp_path):
    folder = "pastaSomentePdf01"
    policies = tmp_path / "policies"
    policies.mkdir()
    (policies / "KERNEL-POLICY-001.json").write_text(
        json.dumps(_policy("KERNEL-POLICY-001", folder)),
        encoding="utf-8",
    )
    (tmp_path / "roots.json").write_text(json.dumps(_roots(folder)), encoding="utf-8")
    calls = {"download": 0}

    code = run_drive_folder(
        folder,
        root=tmp_path,
        policies_dir=policies,
        roots_path=tmp_path / "roots.json",
        wo_dir=tmp_path / "wo",
        evidence_path=tmp_path / "evidence.json",
        env={"DRIVE_ACCESS_TOKEN": TOKEN},
        clock=lambda: WHEN,
        list_children=lambda folder_id, env: [
            {"id": "pdf1", "name": "norma.pdf", "mimeType": "application/pdf", "size": 20}
        ],
        download_bytes=lambda item, env: calls.__setitem__("download", calls["download"] + 1) or b"%PDF",
    )
    assert code == 2
    assert calls["download"] == 0
    assert list((tmp_path / "atoms").glob("*.json")) == []


def test_media_url_keeps_the_token_out_of_the_query():
    assert "alt=media" in media_url("abc", "text/plain")
    assert "Bearer" not in media_url("abc", "text/plain")
    assert "export?mimeType=text/plain" in media_url("abc", "application/vnd.google-apps.document")
