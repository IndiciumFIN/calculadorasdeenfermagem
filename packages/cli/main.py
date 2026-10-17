"""CLI canônica e blindada — Calculadoras de Enfermagem.

Comandos:
  ingest    — ingere texto de fonte oficial (DOU, secundária, ou URL)
  process   — atomiza texto em regras atômicas
  validate  — valida átomos contra schema AtomoBlindado (Pydantic v2)
  kernel    — executor de políticas do Kernel (subcommand)
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Optional

import requests
import typer
from bs4 import BeautifulSoup

from packages.cli.utils import aplicar_mascara, calcular_hash
from packages.cli.auditor import auditar_omissao
from packages.schemas.invariantes import AtomoBlindado
from packages.cli.adapters.dou import fetch_dou_federal
from packages.cli.adapters.secundaria import fetch_secundaria

# Kernel subcommands
from kernel.core import Kernel, Decision
from kernel.policy_registry import get_policy, list_policies
from validators.registry import list_validators

app = typer.Typer(help="CLI canônica e blindada — Calculadoras de Enfermagem")
kernel_app = typer.Typer(help="Kernel — executor de políticas determinísticas")
app.add_typer(kernel_app, name="kernel", invoke_without_command=True)


# ══════════════════════════════════════════════════════════════
# COMANDOS EXISTENTES
# ══════════════════════════════════════════════════════════════

@app.command()
def ingest(
    source: str = typer.Option(..., "--source", "-s"),
    output: Path = typer.Option("data/raw.json", "--output", "-o"),
    fonte: str = typer.Option("auto", "--fonte", help="auto | dou_federal | secundaria"),
) -> None:
    """Ingesta + máscara + hash de fonte oficial."""
    typer.echo(f"Ingerindo: {source} (fonte={fonte})")

    if fonte == "dou_federal" or (fonte == "auto" and "in.gov.br" in source):
        payload = fetch_dou_federal(source)
    elif fonte == "secundaria":
        payload = fetch_secundaria(source)
    else:
        if source.startswith("http"):
            resp = requests.get(source, timeout=30, headers={"User-Agent": "Mozilla/5.0 CE-CLI/1.1"})
            resp.raise_for_status()
            text = BeautifulSoup(resp.text, "html.parser").get_text(separator="\n", strip=True)
        else:
            path = Path(source)
            if not path.exists():
                typer.secho("Arquivo não encontrado", fg=typer.colors.RED)
                raise typer.Exit(1)
            text = path.read_text(encoding="utf-8")
        texto_limpo = aplicar_mascara(text)
        payload = {
            "origem": source,
            "fonte_tipo": "GENERICA",
            "texto_sanitizado": texto_limpo[:30000],
            "hash": calcular_hash(texto_limpo),
            "data_ingestao": str(date.today()),
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    typer.secho(f"✓ Ingestão salva (tipo: {payload.get('fonte_tipo', payload.get('esfera'))})", fg=typer.colors.GREEN)


@app.command()
def process(
    input_file: Path = typer.Option(..., "--input", "-i"),
    output: Path = typer.Option("data/atomos.json", "--output", "-o"),
    block_on_omission: bool = typer.Option(False, "--block-on-omission"),
) -> None:
    """Atomiza texto em regras atômicas."""
    data = json.loads(input_file.read_text())
    texto = data.get("texto_sanitizado") or ""
    atomos = []
    linhas = [l.strip() for l in texto.split("\n") if len(l.strip()) > 40]
    has_critical = False
    for i, linha in enumerate(linhas[:15]):
        if any(k in linha.lower() for k in ["art.", "artigo", "§", "inciso", "parágrafo"]):
            atomo = {
                "id_atomo": f"NORM-{date.today().year}-{i+1:03d}",
                "texto_regra": linha[:500],
                "dispositivo_legal": linha[:100],
                "norma_origem": data.get("origem", "desconhecida"),
                "link_fonte": data.get("origem", "https://example.com"),
                "status": "Vigente",
                "data_verificacao": str(date.today()),
                "versao_contrato": "1.2.0",
                "fonte_tipo": data.get("fonte_tipo", "GENERICA"),
            }
            audit = auditar_omissao(texto, atomo["texto_regra"])
            atomo["_auditoria"] = audit
            if audit.get("omissao_critica"):
                has_critical = True
            atomos.append(atomo)
    output.write_text(json.dumps(atomos, ensure_ascii=False, indent=2))
    typer.secho(f"✓ {len(atomos)} átomos", fg=typer.colors.GREEN)
    if block_on_omission and has_critical:
        typer.secho("❌ Omissão crítica detectada — bloqueado.", fg=typer.colors.RED)
        raise typer.Exit(2)


@app.command()
def validate(
    input_file: Path = typer.Option(..., "--input", "-i"),
    strict: bool = typer.Option(False, "--strict", help="Fail-closed (exit 2)"),
) -> None:
    """Valida átomos contra schema AtomoBlindado (Pydantic v2)."""
    data = json.loads(input_file.read_text())
    if isinstance(data, dict):
        data = [data]
    validos = 0
    erros = 0
    for item in data:
        item_limpo = {k: v for k, v in item.items() if not k.startswith("_")}
        try:
            AtomoBlindado(**item_limpo)
            validos += 1
        except Exception as e:
            erros += 1
            typer.secho(f"  ✗ {item_limpo.get('id_atomo', '?')}: {e}", fg=typer.colors.RED)
    typer.secho(f"✓ {validos} válidos | ✗ {erros} inválidos", fg=typer.colors.GREEN if erros == 0 else typer.colors.YELLOW)
    if strict and erros > 0:
        raise typer.Exit(2)


# ══════════════════════════════════════════════════════════════
# KERNEL SUBCOMMANDS
# ══════════════════════════════════════════════════════════════

@kernel_app.callback(invoke_without_command=True)
def kernel_main(ctx: typer.Context) -> None:
    """Kernel — executor de políticas determinísticas.
    Sem política registrada → rejeitado (exit 2).
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


@kernel_app.command("gate")
def kernel_gate(
    policy_id: str = typer.Argument(..., help="ID da política (ex: KERNEL-POLICY-001)"),
) -> None:
    """Executa gate determinístico para uma política."""
    kernel_cli = Kernel()
    exit_code = kernel_cli.gate(policy_id)
    if exit_code == 2:
        typer.secho(f"❌ Gate FAILED: {policy_id}", fg=typer.colors.RED)
        raise typer.Exit(2)
    typer.secho(f"✅ Gate PASSED: {policy_id}", fg=typer.colors.GREEN)


@kernel_app.command("validate")
def kernel_validate(
    policy_id: str = typer.Option(..., "--policy", "-p"),
    input: Path = typer.Option(..., "--input", "-i"),
) -> None:
    """Valida átomos contra uma política do Kernel."""
    if not input.exists():
        typer.secho(f"❌ Input não encontrado: {input}", fg=typer.colors.RED)
        raise typer.Exit(2)

    if input.is_file():
        with input.open() as f:
            atoms = json.load(f)
        if isinstance(atoms, dict):
            atoms = [atoms]
    else:
        atoms = []
        for fp in sorted(input.glob("*.json")):
            with fp.open() as f:
                atoms.append(json.load(f))

    if not atoms:
        typer.secho("⚠️  Nenhum átomo encontrado.", fg=typer.colors.YELLOW)
        raise typer.Exit(1)

    kernel_cli = Kernel()
    decision = kernel_cli.evaluate_batch(atoms, policy_id)
    decision.print_summary()

    if decision.has_failures():
        typer.secho("❌ Validação REJEITADA", fg=typer.colors.RED)
        raise typer.Exit(2)
    elif decision.decision == Decision.PENDING_REVIEW:
        typer.secho("⚠️  Validação PENDENTE — requer revisão humana.", fg=typer.colors.YELLOW)
    else:
        typer.secho("✅ Validação APROVADA", fg=typer.colors.GREEN)


@kernel_app.command("list-policies")
def kernel_list_policies() -> None:
    """Lista todas as políticas registradas."""
    kernel_cli = Kernel()
    kernel_cli.list_policies()


@kernel_app.command("show-policy")
def kernel_show_policy(policy_id: str = typer.Argument(...)) -> None:
    """Mostra detalhes de uma política."""
    try:
        p = get_policy(policy_id)
    except (KeyError, FileNotFoundError) as e:
        typer.secho(f"❌ Política não encontrada: {policy_id}", fg=typer.colors.RED)
        raise typer.Exit(2)
    typer.echo(json.dumps(p.to_dict(), indent=2, ensure_ascii=False))


@kernel_app.command("list-validators")
def kernel_list_validators() -> None:
    """Lista todos os validadores registrados."""
    validators = list_validators()
    typer.secho(f"\n{len(validators)} validadores registrados:\n", fg=typer.colors.CYAN)
    for v in validators:
        typer.echo(f"  - {v}")
    typer.echo()


@kernel_app.command("test-validators")
def kernel_test_validators() -> None:
    """Executa test_suite de todos os validadores."""
    from validators.registry import VALIDATORS
    failures = []
    for name, validator in sorted(VALIDATORS.items()):
        if hasattr(validator, "run_tests") and callable(validator.run_tests):
            if not validator.run_tests():
                failures.append(name)
    if failures:
        typer.secho(f"\n❌ {len(failures)} validadores falharam:", fg=typer.colors.RED)
        for f in failures:
            typer.echo(f"  - {f}")
        raise typer.Exit(2)
    typer.secho(f"\n✅ Todos os {len(VALIDATORS)} validadores passaram.", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
