import typer
from pathlib import Path

app = typer.Typer(help="CLI de governança e processamento - Calculadoras de Enfermagem")

@app.command()
def validate(
    schema: str = typer.Option("atomo", help="Nome do schema a validar"),
    input_file: Path = typer.Option(..., "--input", "-i")
):
    """Valida um arquivo JSON contra o schema."""
    typer.echo(f"Validando {input_file} com schema {schema}...")
    # TODO: implementar validação com Pydantic
    typer.secho("✓ Válido (placeholder)", fg=typer.colors.GREEN)

@app.command()
def docs_generate():
    """Gera documentação viva a partir dos schemas."""
    typer.echo("Gerando docs a partir dos schemas...")
    # TODO: implementar geração
    typer.secho("Docs atualizados.", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()
