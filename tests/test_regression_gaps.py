"""
Testes de regressão dos gaps e defeitos confirmados na revisão de 14/10/2026.

Cada teste reproduz um cenário que ANTES era aceito indevidamente (T1–T4, T9)
e agora deve falhar de forma fail-closed, além dos caminhos positivos.
Executar com: pytest tests/ (PYTHONPATH é resolvido automaticamente).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import typer

from packages.cli.main import atomizar_heuristica, ingerir
from packages.cli.registry import registrar_item, transicionar_status

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "contracts" / "fixtures"


def run_cli(args, cwd, extra_env=None):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(REPO)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, "-m"] + args,
        cwd=cwd, env=env, capture_output=True, text=True,
    )


# --- T1: corpus vazio não pode passar -------------------------------------

def test_t1_corpus_vazio_reprova(tmp_path):
    r = run_cli(
        ["packages.cli.main", "validate", "--input", str(FIXTURES / "negativo_corpus_vazio.json")],
        cwd=tmp_path,
    )
    assert r.returncode == 2, r.stdout + r.stderr


# --- T2: placeholder de fonte e omissão crítica não podem passar -----------

def test_t2_fonte_placeholder_reprova(tmp_path):
    r = run_cli(
        ["packages.cli.main", "validate", "--input", str(FIXTURES / "negativo_fonte_placeholder.json")],
        cwd=tmp_path,
    )
    assert r.returncode == 2, r.stdout + r.stderr


def test_t2_omissao_critica_reprova(tmp_path):
    r = run_cli(
        ["packages.cli.main", "validate", "--input", str(FIXTURES / "negativo_omissao_critica.json")],
        cwd=tmp_path,
    )
    assert r.returncode == 2, r.stdout + r.stderr
    assert "omissão crítica" in r.stdout


def test_vigente_sem_verificacao_reprova(tmp_path):
    r = run_cli(
        ["packages.cli.main", "validate", "--input", str(FIXTURES / "negativo_vigente_sem_verificacao.json")],
        cwd=tmp_path,
    )
    assert r.returncode == 2, r.stdout + r.stderr


def test_propriedade_desconhecida_reprova(tmp_path):
    r = run_cli(
        ["packages.cli.main", "validate", "--input", str(FIXTURES / "negativo_propriedade_desconhecida.json")],
        cwd=tmp_path,
    )
    assert r.returncode == 2, r.stdout + r.stderr


def test_fixtures_validas_passam(tmp_path):
    for nome in ["atomo_valido.json", "atomo_vigente_valido.json"]:
        r = run_cli(
            ["packages.cli.main", "validate", "--input", str(FIXTURES / nome)],
            cwd=tmp_path,
        )
        assert r.returncode == 0, f"{nome}: {r.stdout}{r.stderr}"


# --- T4: sem corte de 15 linhas e sem vigência automática ------------------

def test_t4_process_sem_corte_e_sem_vigencia(tmp_path):
    linhas = [
        f"Art. {i}º Dispositivo normativo de número {i} com prazo de {i * 10} dias para cumprimento."
        for i in range(1, 26)
    ]
    raw = tmp_path / "raw25.json"
    raw.write_text(json.dumps({
        "origem": "https://www.in.gov.br/web/dou/-/exemplo",
        "fonte_tipo": "DIARIO_OFICIAL_FEDERAL",
        "texto_sanitizado": "\n".join(linhas),
    }), encoding="utf-8")
    out = tmp_path / "atomos.json"
    atomizar_heuristica(raw, out)
    atomos = json.loads(out.read_text())
    assert len(atomos) == 25, "corte silencioso de linhas voltou (GOV-005)"
    assert {a["status"] for a in atomos} == {"Não verificado"}, "vigência automática voltou (GOV-004)"


def test_process_corpus_sem_atomos_reprova(tmp_path):
    raw = tmp_path / "raw_vazio.json"
    raw.write_text(json.dumps({"origem": "x", "texto_sanitizado": "texto sem dispositivos"}))
    with pytest.raises(typer.Exit) as exc:
        atomizar_heuristica(raw, tmp_path / "a.json")
    assert exc.value.exit_code == 2


# --- T9: regex de omissão preserva os números ------------------------------

def test_t9_regex_preserva_numeros():
    sys.path.insert(0, str(REPO))
    from packages.cli.utils import extrair_numeros_criticos
    nums = extrair_numeros_criticos("O prazo será de 30 dias e depois 60 dias para recurso.")
    assert "30 dias" in nums and "60 dias" in nums, f"grupo de captura voltou a perder números: {nums}"


# --- T3: registry com integridade e máquina de estados ----------------------

def test_t3_registry_hash_invalido_reprova(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(typer.Exit) as exc:
        registrar_item("X-1", "atomo", "manual", "nao-e-hash")
    assert exc.value.exit_code == 2


def test_t3_registry_status_livre_reprova(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(typer.Exit) as exc:
        registrar_item("X-2", "atomo", "manual", "a" * 64, "qualquer_coisa_inventada")
    assert exc.value.exit_code == 2


def test_registry_transicao_invalida_reprova(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    registrar_item("X-3", "atomo", "manual", "a" * 64)
    with pytest.raises(typer.Exit) as pulo:
        transicionar_status("X-3", "canonico", "tentativa de pulo de estado")
    assert pulo.value.exit_code == 2
    transicionar_status("X-3", "candidato", "validação de schema em CI")


# --- Allowlist de fontes na ingestão ----------------------------------------

def test_ingest_dominio_fora_da_allowlist_reprova(tmp_path, capsys):
    with pytest.raises(typer.Exit) as exc:
        ingerir("https://blog-nao-oficial.example.org/norma", tmp_path / "raw.json")
    assert exc.value.exit_code == 2
    assert "REFERENCE_ONLY" in capsys.readouterr().out
    assert not (tmp_path / "raw.json").exists()


# --- GAP-02: proveniência com hash duplo ------------------------------------

def test_heuristica_id_hash_e_proveniencia_incompleta(tmp_path, capsys):
    origem = "https://www.in.gov.br/web/dou/-/exemplo"
    linha = "Art. 1º Dispositivo normativo de número 1 com prazo de 10 dias para cumprimento."
    raw = tmp_path / "raw.json"
    raw.write_text(json.dumps({
        "origem": origem,
        "texto_sanitizado": linha,
        "sha256_original": "a" * 64,
    }))
    with pytest.raises(typer.Exit) as exc:
        atomizar_heuristica(raw, tmp_path / "out.json")
    assert exc.value.exit_code == 2
    assert "proveniência incompleto" in capsys.readouterr().out
    assert not (tmp_path / "out.json").exists()

    raw.write_text(json.dumps({
        "origem": origem,
        "texto_sanitizado": linha,
        "sha256_original": "a" * 64,
        "sha256_transformado": "b" * 64,
    }))
    out = tmp_path / "atomos.json"
    atomizar_heuristica(raw, out)
    atomos = json.loads(out.read_text())
    esperado = "NORM-" + hashlib.sha256(f"{linha}|{origem}".encode()).hexdigest()[:12]
    assert atomos[0]["id_atomo"] == esperado
    assert re.fullmatch(r"NORM-[0-9a-f]{12}", atomos[0]["id_atomo"])
    assert atomos[0]["status"] == "Não verificado"


def test_mascara_telefone_preserva_sequencia_longa():
    from packages.cli.utils import aplicar_mascara_com_diff
    texto = "Protocolo 2500012345678 e contato (11) 98765-4321."
    limpo, diff = aplicar_mascara_com_diff(texto)
    assert "2500012345678" in limpo
    assert "[TEL_REDACT]" in limpo
    assert any(item["padrao"] == "TELEFONE" for item in diff)


def test_ingest_local_preserva_original_com_hash_duplo(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fonte = tmp_path / "norma.txt"
    fonte.write_text(
        "Art. 1º Prazo de 30 dias. Contato: (11) 98765-4321.\n"
        "Art. 2º Prazo de 60 dias para o recurso administrativo cabível.",
        encoding="utf-8",
    )
    ingerir(str(fonte), tmp_path / "raw.json")
    payload = json.loads((tmp_path / "raw.json").read_text())
    assert payload["sha256_original"] != payload["sha256_transformado"], "máscara aplicada deve alterar o hash"
    original = tmp_path / "data" / "sources" / f"{payload['sha256_original']}.txt"
    assert original.exists(), "original bruto não foi preservado (GAP-02)"
    assert any(d["padrao"] == "TELEFONE" for d in payload["mascara_diff"]), "diff da máscara ausente (GAP-08)"


# --- GAP-01/05/09: llm_runner (PEP) -----------------------------------------

def _preparar_workdir_llm(tmp_path):
    for pasta in ["agents", "prompts", "contracts"]:
        shutil.copytree(REPO / pasta, tmp_path / pasta)
    return tmp_path


def test_llm_runner_mock_executa_e_nao_e_promovivel(tmp_path):
    cwd = _preparar_workdir_llm(tmp_path)
    r = run_cli(
        ["packages.cli.llm_runner", "run", "--work-order", "contracts/work_orders/WO-EXEMPLO-001.json"],
        cwd=cwd, extra_env={"CE_ALLOW_MOCK": "1"},
    )
    assert r.returncode == 0, r.stdout + r.stderr
    manifest = json.loads((cwd / "data" / "raw_llm" / "WO-EXEMPLO-001" / "manifest.json").read_text())
    assert manifest["promotable"] is False
    assert manifest["estagio"] == "raw"
    assert manifest["model_id"] == "mock:echo-v1"


def test_llm_runner_mock_sem_flag_reprova(tmp_path):
    cwd = _preparar_workdir_llm(tmp_path)
    env = {k: v for k, v in os.environ.items() if k != "CE_ALLOW_MOCK"}
    env["PYTHONPATH"] = str(REPO)
    r = subprocess.run(
        [sys.executable, "-m", "packages.cli.llm_runner", "run",
         "--work-order", "contracts/work_orders/WO-EXEMPLO-001.json"],
        cwd=cwd, env=env, capture_output=True, text=True,
    )
    assert r.returncode == 2, r.stdout + r.stderr


def test_llm_runner_prompt_adulterado_reprova(tmp_path):
    cwd = _preparar_workdir_llm(tmp_path)
    prompt = cwd / "prompts" / "extractor_v1.txt"
    prompt.write_text(prompt.read_text() + "\nINSTRUÇÃO INJETADA", encoding="utf-8")
    r = run_cli(
        ["packages.cli.llm_runner", "run", "--work-order", "contracts/work_orders/WO-EXEMPLO-001.json"],
        cwd=cwd, extra_env={"CE_ALLOW_MOCK": "1"},
    )
    assert r.returncode == 2, r.stdout + r.stderr
    assert "hash do prompt" in r.stdout


def test_llm_runner_recertificacao_expirada_reprova(tmp_path):
    cwd = _preparar_workdir_llm(tmp_path)
    reg_path = cwd / "agents" / "registry.json"
    reg = json.loads(reg_path.read_text())
    reg["agentes"]["AGT-EXTRATOR-001"]["recertificacao"]["valido_ate"] = "2020-01-01"
    reg_path.write_text(json.dumps(reg, ensure_ascii=False, indent=2))
    r = run_cli(
        ["packages.cli.llm_runner", "run", "--work-order", "contracts/work_orders/WO-EXEMPLO-001.json"],
        cwd=cwd, extra_env={"CE_ALLOW_MOCK": "1"},
    )
    assert r.returncode == 2, r.stdout + r.stderr
    assert "recertificação" in r.stdout


def test_llm_runner_modelo_fora_da_allowlist_reprova(tmp_path):
    cwd = _preparar_workdir_llm(tmp_path)
    wo_path = cwd / "contracts" / "work_orders" / "WO-EXEMPLO-001.json"
    wo = json.loads(wo_path.read_text())
    wo["model_id"] = "anthropic:modelo-nao-aprovado"
    wo_path.write_text(json.dumps(wo, ensure_ascii=False, indent=2))
    r = run_cli(
        ["packages.cli.llm_runner", "run", "--work-order", str(wo_path)],
        cwd=cwd, extra_env={"CE_ALLOW_MOCK": "1"},
    )
    assert r.returncode == 2, r.stdout + r.stderr
    assert "allowlist" in r.stdout
