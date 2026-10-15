#!/usr/bin/env python3
"""Pipeline antigo. TAREFA-T04 permanece não qualificada e o comando não grava."""
from pathlib import Path

import typer

from packages.cli.porta import recusar_escrita_fora_do_kernel

app = typer.Typer(help="Pipeline antigo. A execução qualificada está no kernel.")


@app.command()
def run(
    source: str = typer.Option(..., "--source", "-s"),
    workdir: Path = typer.Option(Path("data/pipeline"), "--workdir"),
    require_registry: bool = typer.Option(True, "--require-registry"),
    work_order: Path = typer.Option(None, "--work-order"),
):
    """Recusa a execução. TAREFA-T04 permanece não qualificada."""
    recusar_escrita_fora_do_kernel(work_order)


if __name__ == "__main__":
    app()
