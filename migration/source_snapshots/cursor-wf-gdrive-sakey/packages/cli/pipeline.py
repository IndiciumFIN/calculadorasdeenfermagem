#!/usr/bin/env python3
"""
Pipeline determinístico - Calculadoras de Enfermagem

Executa: ingest → process → validate → registry_check

Regras:
- Exit 0 só se TODAS as etapas obrigatórias passarem.
- Artefato sem registro no registry → exit 2.
- Qualquer omissão crítica ou invariante violada → exit 2.
"""
import json
import sys
from pathlib import Path
import typer

app = typer.Typer(help="Pipeline determinístico com gates obrigatórios")

@app.command()
def run(
    source: str = typer.Option(..., "--source", "-s"),
    workdir: Path = typer.Option(Path("data/pipeline"), "--workdir"),
    require_registry: bool = typer.Option(True, "--require-registry"),
):
    """Executa o pipeline completo com validação."""
    workdir.mkdir(parents=True, exist_ok=True)
    raw = workdir / "raw.json"
    atomos = workdir / "atomos.json"
    
    # Etapa 1: ingest
    typer.echo("=== GATE 1: INGEST ===")
    from packages.cli.main import ingest as do_ingest
    # Chamada direta simplificada
    import subprocess
    r = subprocess.run([
        sys.executable, "-m", "packages.cli.main",
        "ingest", "--source", source, "--output", str(raw)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        typer.secho(f"FAIL ingest: {r.stderr}", fg=typer.colors.RED)
        raise typer.Exit(2)
    typer.secho("PASS ingest", fg=typer.colors.GREEN)
    
    # Etapa 2: process
    typer.echo("=== GATE 2: PROCESS ===")
    r = subprocess.run([
        sys.executable, "-m", "packages.cli.main",
        "process", "--input", str(raw), "--output", str(atomos)
    ], capture_output=True, text=True)
    if r.returncode != 0:
        typer.secho(f"FAIL process: {r.stderr}", fg=typer.colors.RED)
        raise typer.Exit(2)
    typer.secho("PASS process", fg=typer.colors.GREEN)
    
    # Etapa 3: validate
    typer.echo("=== GATE 3: VALIDATE ===")
    r = subprocess.run([
        sys.executable, "-m", "packages.cli.main",
        "validate", "--input", str(atomos)
    ], capture_output=True, text=True)
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
        ids = {a.get("id_atomo") for a in atomos_data if isinstance(atomos_data, list)}
        registered = {item.get("id_canonico") for item in registry}
        missing = ids - registered
        if missing:
            typer.secho(f"FAIL: átomos sem registro no registry: {missing}", fg=typer.colors.RED)
            raise typer.Exit(2)
        typer.secho("PASS registry", fg=typer.colors.GREEN)
    
    typer.secho("\n✓ PIPELINE COMPLETO - TODOS OS GATES PASSARAM", fg=typer.colors.GREEN)
    raise typer.Exit(0)

if __name__ == "__main__":
    app()
