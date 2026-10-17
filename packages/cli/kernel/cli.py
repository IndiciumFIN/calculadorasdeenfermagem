"""Kernel CLI — interface Typer para o Kernel determinístico.

Uso:
    kernel ingest   --policy KERNEL-POLICY-001 --source DOU --date 2026-10-01
    kernel atomize  --policy KERNEL-POLICY-001 --input data/raw/
    kernel validate --policy KERNEL-POLICY-001 --input data/canonical/atoms/
    kernel gate     --policy KERNEL-POLICY-001
    kernel list-policies
    kernel show-policy KERNEL-POLICY-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import typer

from kernel.core import Kernel, Decision
from kernel.policy_registry import get_policy, list_policies
from validators.registry import list_validators

app = typer.Typer(help="Kernel determinístico — executor de políticas normativas")
kernel_cli = Kernel()


@app.command()
def gate(
    policy_id: str = typer.Argument(..., help="ID da política para verificar"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Executa gate determinístico para uma política."""
    exit_code = kernel_cli.gate(policy_id)
    if exit_code == 2:
        typer.secho(f"❌ Gate FAILED: {policy_id}", fg=typer.colors.RED)
        raise typer.Exit(2)
    typer.secho(f"✅ Gate PASSED: {policy_id}", fg=typer.colors.GREEN)


@app.command()
def list_policies_cmd(
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Lista todas as políticas registradas no Kernel."""
    policies = list_policies()
    if not policies:
        typer.secho("Nenhuma política registrada. Verifique contracts/policies/.", fg=typer.colors.YELLOW)
        raise typer.Exit(1)

    typer.secho(f"\n{len(policies)} políticas registradas:\n", fg=typer.colors.CYAN)
    for p in policies:
        typer.echo(f"  {p.id}")
        typer.echo(f"    Nome:        {p.name}")
        typer.echo(f"    Version:      {p.version}")
        typer.echo(f"    Validadores:  {', '.join(p.validators)}")
        typer.echo(f"    WO required: {p.wo_required} | Revisão humana: {p.requires_human_review}")
        if verbose:
            typer.echo(f"    Output:       {p.atoms_output}")
            typer.echo(f"    Fail-closed:  {p.fail_closed}")
            typer.echo(f"    Updated:       {p.updated_at}")
        typer.echo()


@app.command()
def show_policy(
    policy_id: str = typer.Argument(..., help="ID da política"),
) -> None:
    """Mostra detalhes de uma política."""
    try:
        p = get_policy(policy_id)
    except (KeyError, FileNotFoundError) as e:
        typer.secho(f"❌ Política não encontrada: {policy_id}", fg=typer.colors.RED)
        typer.secho(f"   {e}", fg=typer.colors.RED)
        raise typer.Exit(2)

    import json
    typer.echo(json.dumps(p.to_dict(), indent=2, ensure_ascii=False))


@app.command()
def validate(
    policy_id: str = typer.Option(..., "--policy", "-p", help="ID da política"),
    input: Path = typer.Option(..., "--input", "-i", help="Arquivo JSON ou diretório de átomos"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Valida átomos contra uma política do Kernel."""
    if not input.exists():
        typer.secho(f"❌ Input não encontrado: {input}", fg=typer.colors.RED)
        raise typer.Exit(2)

    import json
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

    decision = kernel_cli.evaluate_batch(atoms, policy_id)
    decision.print_summary()

    if decision.has_failures():
        typer.secho("❌ Validação REJEITADA", fg=typer.colors.RED)
        raise typer.Exit(2)
    elif decision.decision == Decision.PENDING_REVIEW:
        typer.secho("⚠️  Validação PENDENTE — requer revisão humana.", fg=typer.colors.YELLOW)
    else:
        typer.secho("✅ Validação APROVADA", fg=typer.colors.GREEN)


@app.command()
def list_validators_cmd() -> None:
    """Lista todos os validadores registrados."""
    validators = list_validators()
    typer.secho(f"\n{len(validators)} validadores registrados:\n", fg=typer.colors.CYAN)
    for v in validators:
        typer.echo(f"  - {v}")
    typer.echo()


@app.command()
def test_validators() -> None:
    """Executa test_suite de todos os validadores."""
    from validators.registry import VALIDATORS
    failures = []
    for name, validator in sorted(VALIDATORS.items()):
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
