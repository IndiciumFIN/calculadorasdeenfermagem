import json
from pathlib import Path
from datetime import date
import typer

app = typer.Typer(help="Gerencia o Registry canônico local (JSON)")

REGISTRY_FILE = Path("data/registry.json")

def load_registry() -> list:
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text())
    return []

def save_registry(data: list):
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

@app.command()
def add(
    id_canonico: str = typer.Option(..., "--id"),
    tipo: str = typer.Option(..., "--tipo"),
    origem: str = typer.Option(..., "--origem"),
    hash_sha: str = typer.Option(None, "--hash"),
    status: str = typer.Option("bruto", "--status"),
):
    """Adiciona um item ao registry local."""
    registry = load_registry()
    if any(item.get("id_canonico") == id_canonico for item in registry):
        typer.secho(f"ID {id_canonico} já existe", fg=typer.colors.YELLOW)
        raise typer.Exit(1)
    
    item = {
        "id_canonico": id_canonico,
        "tipo": tipo,
        "hash_sha256": hash_sha,
        "status": status,
        "origem": origem,
        "versao_contrato": "1.1.0",
        "data_ingestao": str(date.today()),
        "find_ids": []
    }
    registry.append(item)
    save_registry(registry)
    typer.secho(f"✓ {id_canonico} adicionado", fg=typer.colors.GREEN)

@app.command()
def list_status(status: str = typer.Option(None, "--status")):
    """Lista itens do registry."""
    registry = load_registry()
    if status:
        registry = [i for i in registry if i.get("status") == status]
    typer.echo(f"{len(registry)} itens")
    for item in registry[:20]:
        typer.echo(f"  {item['id_canonico']} | {item['status']} | {item['tipo']}")

if __name__ == "__main__":
    app()
