"""Escrita do CLI antigo. T01, T02, T04 e T07 continuam não qualificadas."""
from pathlib import Path

import typer

from packages.cli.pep import carregar_wo


def recusar_escrita_fora_do_kernel(work_order: Path | None) -> None:
    if work_order is None:
        typer.secho("FAIL: escrita sem Work Order", fg=typer.colors.RED)
        raise typer.Exit(2)
    try:
        wo = carregar_wo(work_order)
    except Exception as exc:
        typer.secho(f"FAIL: {exc}", fg=typer.colors.RED)
        raise typer.Exit(2)
    typer.secho(
        f"FAIL: Work Order {wo.id} é {wo.task_type} e não autoriza esta escrita. "
        "T01, T02, T04 e T07 permanecem não qualificadas. "
        "A escrita qualificada entra por packages.cli.kernel.",
        fg=typer.colors.RED,
    )
    raise typer.Exit(2)
