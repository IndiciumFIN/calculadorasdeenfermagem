"""WO do Kernel antes de obter ou atomizar uma pasta Drive."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _entry in (str(ROOT), str(ROOT / "packages" / "cli")):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

import pytest

from kernel.core import Kernel
from kernel.work_orders import DriveProbes, exigir_wo_do_kernel, run_drive_folder
from packages.schemas.invariantes import AtomoBlindado

ROOT = Path(__file__).resolve().parents[1]
PASTA_DRIVE = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"
NORMA = (
    "Art. 5º O enfermeiro registra o procedimento no prontuário do paciente "
    "conforme o protocolo institucional vigente."
)


def test_gate_aprova_somente_politica_com_validadores_reais():
    kernel = Kernel()
    assert kernel.gate("KERNEL-POLICY-001") == 0
    assert kernel.gate("KERNEL-POLICY-003") == 2


def test_pasta_real_fica_bloqueada_sem_download(tmp_path: Path):
    chamadas: list[str] = []

    def baixar(folder_id: str, dest: Path):
        chamadas.append(folder_id)
        return []

    codigo = run_drive_folder(
        PASTA_DRIVE,
        folder_url=f"https://drive.google.com/drive/folders/{PASTA_DRIVE}",
        repo_root=tmp_path,
        policies_dir=ROOT / "contracts" / "policies",
        probes=DriveProbes("AUSENTE", "NEGADO", download=baixar),
    )
    assert codigo == 2
    assert chamadas == []
    wos = sorted((tmp_path / "data" / "legado").glob("autorizacao_WO-*.json"))
    assert len(wos) == 2
    for path in wos:
        wo = json.loads(path.read_text(encoding="utf-8"))
        assert wo["submitted_by"] == "kernel"
        assert wo["authorized_by"] == "kernel"
        assert wo["status"] == "BLOQUEADO"
        assert wo["estado"] == "BLOQUEADO"
        assert PASTA_DRIVE in wo["motivo"]
        assert wo["politicas_validas"] == [
            "KERNEL-POLICY-001",
            "KERNEL-POLICY-002",
            "KERNEL-POLICY-019",
            "KERNEL-POLICY-020",
        ]
    decisao = json.loads(
        (tmp_path / "evidence" / f"CE-WO-KERNEL-DRIVE-{PASTA_DRIVE}" / "decisao.json").read_text(
            encoding="utf-8"
        )
    )
    assert decisao["resultado"] == "BLOQUEADO"
    assert not (tmp_path / "data" / "canonical").exists()
    primeira = wos[0].read_text(encoding="utf-8")
    de_novo = run_drive_folder(
        PASTA_DRIVE,
        repo_root=tmp_path,
        policies_dir=ROOT / "contracts" / "policies",
        probes=DriveProbes("AUSENTE", "NEGADO", download=baixar),
    )
    assert de_novo == 2
    assert wos[0].read_text(encoding="utf-8") == primeira


def test_politica_que_autoriza_o_alvo_baixa_e_atomiza(tmp_path: Path):
    policies = tmp_path / "contracts" / "policies"
    fontes = tmp_path / "contracts" / "fontes"
    policies.mkdir(parents=True)
    fontes.mkdir(parents=True)
    alvo = "pasta-teste-01"
    (fontes / "cofen_dou.json").write_text(
        json.dumps(
            {
                "fonte_slug": "cofen_dou",
                "kernel_policy_id": "KERNEL-POLICY-001",
                "source_contract": "contracts/fontes/cofen_dou.json",
                "pasta_drive": alvo,
            }
        ),
        encoding="utf-8",
    )
    (policies / "KERNEL-POLICY-001.json").write_text(
        json.dumps(
            {
                "id": "KERNEL-POLICY-001",
                "name": "Normativo COFEN",
                "description": "teste",
                "source_contract": "contracts/fontes/cofen_dou.json",
                "validators": [
                    "atomo_schema_validator",
                    "norm_atom_id_validator",
                    "texto_length_validator",
                    "url_validator",
                ],
                "atoms_output": "data/canonical/atoms/cofen",
                "quarentena_output": "data/quarentena/cofen",
                "version": "1.0.0",
                "wo_required": True,
            }
        ),
        encoding="utf-8",
    )

    def baixar(folder_id: str, dest: Path):
        dest.mkdir(parents=True, exist_ok=True)
        arquivos = {
            "norma.txt": NORMA,
            "curto.txt": "curto",
            "opiniao.txt": (
                "Recomenda-se registrar o procedimento de enfermagem neste prontuario institucional."
            ),
        }
        registros = []
        for nome, texto in arquivos.items():
            path = dest / nome
            path.write_text(texto, encoding="utf-8")
            registros.append(
                {
                    "id": nome,
                    "name": nome,
                    "path": str(path),
                    "sha256": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
                    "baixado": True,
                }
            )
        pdf = dest / "nota.pdf"
        pdf.write_bytes(b"%PDF-1.4")
        registros.append(
            {
                "id": "nota.pdf",
                "name": "nota.pdf",
                "path": str(pdf),
                "sha256": hashlib.sha256(b"%PDF-1.4").hexdigest(),
                "baixado": True,
            }
        )
        return registros

    codigo = run_drive_folder(
        alvo,
        repo_root=tmp_path,
        policies_dir=policies,
        probes=DriveProbes("PRESENTE", "ABERTO", download=baixar),
        ano=2026,
    )
    assert codigo == 0
    atomos = list((tmp_path / "data" / "canonical" / "atoms" / "cofen").glob("*.json"))
    assert len(atomos) == 1
    atomo = json.loads(atomos[0].read_text(encoding="utf-8"))
    AtomoBlindado.model_validate(atomo)
    assert atomo["vigencia"] == "NAO_VERIFICADO"
    assert atomo["fonte_slug"] == "cofen_dou"
    assert atomo["texto_regra"] == NORMA
    assert atomo["wo_id"].startswith("CE-WO-KERNEL-ATOMIZAR-")
    assert atomo["sha256_texto"]
    linhas = (
        tmp_path / "data" / "quarentena" / "cofen" / "validacao_invalida.jsonl"
    ).read_text(encoding="utf-8").splitlines()
    assert len(linhas) == 3
    motivos = [json.loads(linha)["motivo"] for linha in linhas]
    assert any("texto_curto" in motivo for motivo in motivos)
    assert any("recomenda-se" in motivo for motivo in motivos)
    assert any("extracao_indisponivel" in motivo for motivo in motivos)
    wo = json.loads(
        (tmp_path / "data" / "legado" / f"autorizacao_WO-KERNEL-ATOMIZAR-{alvo}.json").read_text(
            encoding="utf-8"
        )
    )
    assert wo["status"] == "PASS"
    assert wo["submitted_by"] == "kernel"


def test_wo_de_terceiro_nao_executa():
    with pytest.raises(PermissionError):
        exigir_wo_do_kernel({"submitted_by": "humano", "status": "AUTHORIZED"})
    with pytest.raises(PermissionError):
        exigir_wo_do_kernel({"submitted_by": "kernel", "status": "BLOQUEADO"})
