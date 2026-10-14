"""
LLM Runner — porta única de execução de modelo (GAP-01).

Antes desta porta, o passo de LLM acontecia por copy-paste manual, fora de
qualquer perímetro de controle. Regras:

- Nenhuma chamada sem Work Order pré-autorizada (contrato JSON).
- PEP deny-by-default: agente registrado e recertificado (GAP-09), prompt com
  hash conferido no manifesto, modelo pinado na allowlist do agente (GAP-05),
  temperatura 0 obrigatória, hash do input conferido.
- Saída SEMPRE aterrissa em estágio raw (CANDIDATE_ONLY) com manifesto de
  evidência: hashes de prompt, input e output, model_id e provider.
- Fail-closed: qualquer verificação ausente ou divergente termina com exit 2.

Providers: model_id usa prefixo 'anthropic:', 'openai:' ou 'mock:'. O provider
mock só roda com CE_ALLOW_MOCK=1, grava provider='mock' e promotable=false —
existe para testar o harness, nunca para produzir conteúdo promovível.
"""
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

import typer

from packages.cli.utils import calcular_hash

app = typer.Typer(help="Porta única e governada de execução de LLM")


@app.callback()
def _callback():
    """Força o modo subcomando mesmo com um único comando registrado."""

AGENTS_REGISTRY = Path("agents/registry.json")
PROMPTS_MANIFEST = Path("prompts/manifest.json")
OUTPUT_ROOT = Path("data/raw_llm")

CAMPOS_WO = [
    "id", "agent_id", "task_type", "prompt_id", "prompt_sha256",
    "model_id", "temperature", "input_file", "input_sha256", "authorized_by",
]


def _fail(msg: str):
    typer.secho(f"FAIL: {msg}", fg=typer.colors.RED)
    raise typer.Exit(2)


def _load_json(path: Path, descricao: str) -> dict:
    if not path.exists():
        _fail(f"{descricao} não encontrado: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _pep_check(wo: dict) -> dict:
    """Policy Enforcement Point: valida contrato, agente, prompt e modelo."""
    faltando = [c for c in CAMPOS_WO if c not in wo]
    if faltando:
        _fail(f"Work Order incompleta; campos ausentes: {faltando}")

    if wo["temperature"] != 0:
        _fail("temperatura diferente de 0 é proibida (regra inviolável dos agentes)")

    registro = _load_json(AGENTS_REGISTRY, "Registro de agentes")
    agente = registro.get("agentes", {}).get(wo["agent_id"])
    if agente is None:
        _fail(f"agente '{wo['agent_id']}' não registrado (deny-by-default)")

    recert = agente.get("recertificacao", {})
    if recert.get("status") != "vigente":
        _fail(f"agente '{wo['agent_id']}' sem recertificação vigente (GAP-09)")
    try:
        valido_ate = date.fromisoformat(recert.get("valido_ate", ""))
    except ValueError:
        _fail("recertificação sem data 'valido_ate' válida")
    if valido_ate < date.today():
        _fail(f"recertificação do agente expirou em {valido_ate} (GAP-09)")

    if wo["task_type"] not in agente.get("acoes_permitidas", []):
        _fail(f"task_type '{wo['task_type']}' fora da allowlist do agente")

    if wo["prompt_id"] not in agente.get("prompts_permitidos", []):
        _fail(f"prompt '{wo['prompt_id']}' fora da allowlist do agente")

    manifesto = _load_json(PROMPTS_MANIFEST, "Manifesto de prompts")
    entrada = manifesto.get("prompts", {}).get(wo["prompt_id"])
    if entrada is None:
        _fail(f"prompt '{wo['prompt_id']}' ausente do manifesto")
    prompt_path = Path(entrada["arquivo"])
    if not prompt_path.exists():
        _fail(f"arquivo de prompt inexistente: {prompt_path}")
    sha_prompt = calcular_hash(prompt_path.read_text(encoding="utf-8"))
    if sha_prompt != entrada["sha256"]:
        _fail("hash do prompt diverge do manifesto — prompt adulterado ou manifesto desatualizado")
    if sha_prompt != wo["prompt_sha256"]:
        _fail("hash do prompt diverge do declarado na Work Order")

    if wo["model_id"] not in agente.get("modelos_permitidos", []):
        _fail(f"model_id '{wo['model_id']}' fora da allowlist do agente (pinagem obrigatória, GAP-05)")

    input_path = Path(wo["input_file"])
    if not input_path.exists():
        _fail(f"input inexistente: {input_path}")
    sha_input = calcular_hash(input_path.read_text(encoding="utf-8"))
    if sha_input != wo["input_sha256"]:
        _fail("hash do input diverge do declarado na Work Order")

    return {
        "prompt_path": prompt_path,
        "prompt_sha256": sha_prompt,
        "input_path": input_path,
        "input_sha256": sha_input,
    }


def _chamar_provider(model_id: str, prompt: str, entrada: str) -> tuple[str, str, bool]:
    """Retorna (saida, provider, promotable)."""
    if model_id.startswith("mock:"):
        if os.environ.get("CE_ALLOW_MOCK") != "1":
            _fail("provider mock exige CE_ALLOW_MOCK=1 (uso restrito a teste do harness)")
        saida = json.dumps({
            "provider": "mock",
            "model_id": model_id,
            "echo_prompt_sha256": calcular_hash(prompt),
            "echo_input_sha256": calcular_hash(entrada),
        }, ensure_ascii=False)
        return saida, "mock", False

    if model_id.startswith("anthropic:"):
        _fail(
            "nenhum modelo Anthropic está na allowlist de agentes ainda; "
            "autorizar model_id real exige PR revisado em agents/registry.json "
            "e ANTHROPIC_API_KEY configurada como secret"
        )
    if model_id.startswith("openai:"):
        _fail(
            "nenhum modelo OpenAI está na allowlist de agentes ainda; "
            "autorizar model_id real exige PR revisado em agents/registry.json "
            "e OPENAI_API_KEY configurada como secret"
        )
    _fail(f"provider desconhecido para model_id '{model_id}'")
    raise AssertionError  # inalcançável; _fail sempre lança


@app.command()
def run(work_order: Path = typer.Option(..., "--work-order", "-w")):
    """Executa uma Work Order de agente. Saída sempre em data/raw_llm (CANDIDATE_ONLY)."""
    wo = _load_json(work_order, "Work Order")
    refs = _pep_check(wo)

    prompt = refs["prompt_path"].read_text(encoding="utf-8")
    entrada = refs["input_path"].read_text(encoding="utf-8")

    saida, provider, promotable = _chamar_provider(wo["model_id"], prompt, entrada)

    out_dir = OUTPUT_ROOT / wo["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / "output.json"
    output_path.write_text(saida, encoding="utf-8")

    manifest = {
        "work_order_id": wo["id"],
        "agent_id": wo["agent_id"],
        "task_type": wo["task_type"],
        "model_id": wo["model_id"],
        "provider": provider,
        "temperature": 0,
        "prompt_id": wo["prompt_id"],
        "prompt_sha256": refs["prompt_sha256"],
        "input_sha256": refs["input_sha256"],
        "output_sha256": calcular_hash(saida),
        "authorized_by": wo["authorized_by"],
        "estagio": "raw",
        "promotable": promotable,
        "executado_em": datetime.now(timezone.utc).isoformat(),
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    typer.secho(
        f"✓ WO {wo['id']} executada (provider={provider}, estagio=raw, promotable={promotable})",
        fg=typer.colors.GREEN,
    )


if __name__ == "__main__":
    app()
