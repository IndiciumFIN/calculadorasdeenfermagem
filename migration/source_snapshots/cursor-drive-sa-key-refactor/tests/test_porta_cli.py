"""ingest, process, pipeline e registry recusam escrita fora do kernel."""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WO_OBTER = REPO / "contracts" / "work_orders" / "WO-2026_10_15_0009.json"


def run_cli(args, cwd):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO)
    return subprocess.run(
        [sys.executable, "-m"] + args,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )


def test_process_sem_work_order_nao_grava(tmp_path):
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps({"origem": "local", "texto_sanitizado": "Art. 1º Prazo de 30 dias para cumprimento integral."}))
    out = tmp_path / "atomos.json"
    r = run_cli(["packages.cli.main", "process", "--input", str(raw), "--output", str(out)], tmp_path)
    assert r.returncode == 2
    assert "escrita sem Work Order" in r.stdout
    assert not out.exists()


def test_process_com_work_order_de_outro_procedimento_nao_grava(tmp_path):
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps({"origem": "local", "texto_sanitizado": "Art. 1º Prazo de 30 dias para cumprimento integral."}))
    out = tmp_path / "atomos.json"
    r = run_cli(
        ["packages.cli.main", "process", "--input", str(raw), "--output", str(out), "--work-order", str(WO_OBTER)],
        tmp_path,
    )
    assert r.returncode == 2
    assert "não autoriza esta escrita" in r.stdout
    assert "obter" in r.stdout
    assert not out.exists()


def test_ingest_registry_e_pipeline_sem_work_order_nao_gravam(tmp_path):
    fonte = tmp_path / "norma.txt"
    fonte.write_text("Art. 1º Prazo de 30 dias para o cumprimento.", encoding="utf-8")
    bruto = tmp_path / "raw.json"
    ingest = run_cli(
        ["packages.cli.main", "ingest", "--source", str(fonte), "--output", str(bruto)],
        tmp_path,
    )
    assert ingest.returncode == 2
    assert not bruto.exists()
    incluir = run_cli(
        ["packages.cli.registry", "add", "--id", "X-1", "--tipo", "atomo", "--origem", "manual", "--hash", "a" * 64],
        tmp_path,
    )
    assert incluir.returncode == 2
    assert not (tmp_path / "data" / "registry.json").exists()
    esteira = run_cli(
        ["packages.cli.pipeline", "run", "--source", str(fonte), "--workdir", str(tmp_path / "pipeline")],
        tmp_path,
    )
    assert esteira.returncode == 2
    assert not (tmp_path / "pipeline").exists()
