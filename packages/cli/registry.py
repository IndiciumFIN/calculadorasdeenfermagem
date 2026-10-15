import json
import re
from datetime import date
from pathlib import Path

import typer

app = typer.Typer(help="Gerencia o Registry canônico local (JSON)")

REGISTRY_FILE = Path("data/registry.json")

# Máquina de estados explícita (GOV-007): status livres e transições
# arbitrárias deixavam o registry sem valor probatório.
ESTADOS = ["bruto", "candidato", "validado", "canonico", "quarentena"]
TRANSICOES = {
    "bruto": {"candidato", "quarentena"},
    "candidato": {"validado", "quarentena"},
    "validado": {"canonico", "quarentena"},
    "canonico": {"quarentena"},
    "quarentena": {"bruto"},
}

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def load_registry() -> list:
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text())
    return []


def save_registry(data: list):
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def _validar_hash(hash_sha: str):
    if not hash_sha or not SHA256_RE.match(hash_sha):
        typer.secho(
            "FAIL: hash SHA-256 obrigatório e válido (64 hex). "
            "Registro sem hash não comprova integridade (GOV-007 / teste T3).",
            fg=typer.colors.RED,
        )
        raise typer.Exit(2)


@app.command()
def add(
    id_canonico: str = typer.Option(..., "--id"),
    tipo: str = typer.Option(..., "--tipo"),
    origem: str = typer.Option(..., "--origem"),
    hash_sha: str = typer.Option(..., "--hash", help="SHA-256 do conteúdo (obrigatório)"),
    status: str = typer.Option("bruto", "--status"),
):
    """Adiciona um item ao registry local. Hash obrigatório; status em allowlist."""
    _validar_hash(hash_sha)
    if status not in ESTADOS:
        typer.secho(f"FAIL: status '{status}' fora da allowlist {ESTADOS}", fg=typer.colors.RED)
        raise typer.Exit(2)
    if status != "bruto":
        typer.secho(
            "FAIL: item novo entra como 'bruto'. Promoção só via set-status com transição válida.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(2)

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
        "versao_contrato": "1.2.0",
        "data_ingestao": str(date.today()),
        "find_ids": [],
        "historico": [{"de": None, "para": status, "data": str(date.today())}],
    }
    registry.append(item)
    save_registry(registry)
    typer.secho(f"✓ {id_canonico} adicionado ({status})", fg=typer.colors.GREEN)


@app.command()
def set_status(
    id_canonico: str = typer.Option(..., "--id"),
    novo_status: str = typer.Option(..., "--para"),
    evidencia: str = typer.Option(..., "--evidencia", help="Referência da evidência da transição"),
):
    """Transiciona o estado de um item validando a máquina de estados."""
    if novo_status not in ESTADOS:
        typer.secho(f"FAIL: status '{novo_status}' fora da allowlist {ESTADOS}", fg=typer.colors.RED)
        raise typer.Exit(2)
    registry = load_registry()
    for item in registry:
        if item.get("id_canonico") == id_canonico:
            atual = item.get("status")
            permitidas = TRANSICOES.get(atual, set())
            if novo_status not in permitidas:
                typer.secho(
                    f"FAIL: transição {atual} -> {novo_status} proibida. Permitidas: {sorted(permitidas)}",
                    fg=typer.colors.RED,
                )
                raise typer.Exit(2)
            from packages.cli.finds import promocao_bloqueada

            bloqueados = promocao_bloqueada(novo_status, item.get("find_ids") or [])
            if bloqueados:
                typer.secho(
                    f"FAIL: promoção bloqueada por FIND aberto: {', '.join(bloqueados)}",
                    fg=typer.colors.RED,
                )
                raise typer.Exit(2)
            item["status"] = novo_status
            item.setdefault("historico", []).append(
                {"de": atual, "para": novo_status, "data": str(date.today()), "evidencia": evidencia}
            )
            save_registry(registry)
            typer.secho(f"✓ {id_canonico}: {atual} -> {novo_status}", fg=typer.colors.GREEN)
            return
    typer.secho(f"FAIL: id {id_canonico} não encontrado", fg=typer.colors.RED)
    raise typer.Exit(2)


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
