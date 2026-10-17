#!/usr/bin/env python3
"""
Pipeline determinístico - Calculadoras de Enfermagem

Executa: ingest → process → validate → registry_check → KERNEL_GATE

Regras:
- Exit 0 só se TODAS as etapas obrigatórias passarem.
- Artefato sem registro no registry → exit 2.
- Qualquer omissão crítica ou invariante violada → exit 2.
- KERNEL_GATE: política não registrada → exit 2.

Novidade v1.2: Etapa KERNEL_GATE que delega ao Kernel determinístico.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import typer

app = typer.Typer(help="Pipeline determinístico com gates obrigatórios e Kernel")


@app.command()
def run(
    source: str = typer.Option(..., "--source", "-s", help="Fonte (ex: dou_federal, secundaria)"),
    workdir: Path = typer.Option(Path("data/pipeline"), "--workdir"),
    require_registry: bool = typer.Option(True, "--require-registry"),
    kernel_policy: str | None = typer.Option(
        None, "--kernel-policy", "-k",
        help="KERNEL-POLICY-* para validar após pipeline (ex: KERNEL-POLICY-001)"
    ),
) -> None:
    """Executa o pipeline completo com validação + gate opcional do Kernel."""
    workdir.mkdir(parents=True, exist_ok=True)
    raw = workdir / "raw.json"
    atomos = workdir / "atomos.json"

    # Etapa 1: ingest
    typer.echo("=== GATE 1: INGEST ===")
    r = subprocess.run(
        [sys.executable, "-m", "packages.cli.main",
         "ingest", "--source", source, "--output", str(raw)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        typer.secho(f"FAIL ingest: {r.stderr}", fg=typer.colors.RED)
        raise typer.Exit(2)
    typer.secho("PASS ingest", fg=typer.colors.GREEN)

    # Etapa 2: process
    typer.echo("=== GATE 2: PROCESS ===")
    r = subprocess.run(
        [sys.executable, "-m", "packages.cli.main",
         "process", "--input", str(raw), "--output", str(atomos)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        typer.secho(f"FAIL process: {r.stderr}", fg=typer.colors.RED)
        raise typer.Exit(2)
    typer.secho("PASS process", fg=typer.colors.GREEN)

    # Etapa 3: validate (schema Pydantic v2)
    typer.echo("=== GATE 3: VALIDATE (AtomoBlindado) ===")
    r = subprocess.run(
        [sys.executable, "-m", "packages.cli.main",
         "validate", "--input", str(atomos), "--strict"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        typer.secho(f"FAIL validate:\n{r.stdout}\n{r.stderr}", fg=typer.colors.RED)
        raise typer.Exit(2)
    typer.secho("PASS validate", fg=typer.colors.GREEN)

    # Etapa 4: registry check
    if require_registry:
        typer.echo("=== GATE 4: REGISTRY ===")
        registry_file = Path("data/registry.json")
        if not registry_file.exists():
            typer.secho("FAIL: registry.json não existe. Artefato sem registro.", fg=typer.colors.RED)
            raise typer.Exit(2)
        registry = json.loads(registry_file.read_text())
        atomos_data = json.loads(atomos.read_text())
        if isinstance(atomos_data, dict):
            atomos_data = [atomos_data]
        ids = {a.get("id_atomo") for a in atomos_data if isinstance(a, dict)}
        registered = {item.get("id_canonico") for item in registry if isinstance(item, dict)}
        missing = ids - registered
        if missing:
            typer.secho(f"FAIL: átomos sem registro: {missing}", fg=typer.colors.RED)
            raise typer.Exit(2)
        typer.secho("PASS registry", fg=typer.colors.GREEN)

    # Etapa 5: KERNEL_GATE (se política informada)
    if kernel_policy:
        typer.echo(f"=== GATE 5: KERNEL_GATE ({kernel_policy}) ===")
        r = subprocess.run(
            [sys.executable, "-m", "packages.cli.main",
             "kernel", "gate", kernel_policy],
            capture_output=True, text=True,
        )
        if r.returncode != 0:
            typer.secho(f"FAIL Kernel gate:\n{r.stdout}\n{r.stderr}", fg=typer.colors.RED)
            raise typer.Exit(2)
        typer.secho("PASS Kernel gate", fg=typer.colors.GREEN)

    typer.secho(
        "\n✓ PIPELINE COMPLETO — TODOS OS GATES PASSARAM", fg=typer.colors.GREEN,
    )
    raise typer.Exit(0)


if __name__ == "__main__":
    app()
