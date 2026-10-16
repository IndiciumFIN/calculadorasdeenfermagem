"""
Gate de sincronização Git <-> Supabase (GAP-04).

O corpus versionado no Git é a fonte canônica; o Supabase é projeção de
runtime (HIST-015). Este gate detecta drift comparando o conteúdo das tabelas
com o corpus local por hash do texto. Fail-closed: credenciais ausentes ou
impossibilidade de comparar reprovam — nunca retornam sucesso implícito.

Enforcement: deve ser executado no pipeline de deploy do site. Enquanto não
estiver acoplado ao deploy, o workflow sync-check.yml permite execução manual.
"""
import json
import os
from pathlib import Path

import requests
import typer

from packages.cli.utils import calcular_hash

app = typer.Typer(help="Detecção de drift entre corpus Git e Supabase")

CORPUS_LOCAL = Path("data/atomos.json")


@app.callback()
def _callback():
    """Força o modo subcomando."""


@app.command()
def run():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY")
    if not url or not key:
        typer.secho(
            "FAIL: SUPABASE_URL e SUPABASE_ANON_KEY são obrigatórios. "
            "Sem credenciais não há como comparar — fail-closed (GAP-04).",
            fg=typer.colors.RED,
        )
        raise typer.Exit(2)

    if not CORPUS_LOCAL.exists():
        typer.secho(
            "FAIL: corpus local data/atomos.json ausente; não há baseline para comparar.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(2)

    local = json.loads(CORPUS_LOCAL.read_text())
    local_por_id = {a["id_atomo"]: calcular_hash(a["texto_regra"]) for a in local}

    # Paginação explícita: nunca tratar a primeira página como universo remoto.
    # PostgREST pode impor max_rows; a página curta NÃO encerra a coleta.
    remoto_por_id = {}
    pagina = 1000
    offset = 0
    while True:
        resp = requests.get(
            f"{url.rstrip('/')}/rest/v1/atoms",
            params={"select": "id_atomo,texto_regra,status", "order": "id_atomo.asc", "limit": str(pagina), "offset": str(offset)},
            headers={"apikey": key, "Authorization": f"Bearer {key}", "Prefer": "count=exact"},
            timeout=30,
        )
        resp.raise_for_status()
        lote = resp.json()
        if not isinstance(lote, list):
            typer.secho("FAIL: resposta remota não é lista", fg=typer.colors.RED)
            raise typer.Exit(2)
        for atomo in lote:
            ident = atomo["id_atomo"]
            if ident in remoto_por_id:
                typer.secho(f"FAIL: ID remoto duplicado entre páginas: {ident}", fg=typer.colors.RED)
                raise typer.Exit(2)
            remoto_por_id[ident] = calcular_hash(atomo.get("texto_regra") or "")
        offset += len(lote)
        content_range = resp.headers.get("Content-Range", "")
        # Com count=exact, o total deve ser conhecido e estável.
        if "/" not in content_range or not content_range.rsplit("/", 1)[1].isdigit():
            typer.secho("FAIL: total remoto não informado (Content-Range)", fg=typer.colors.RED)
            raise typer.Exit(2)
        total = int(content_range.rsplit("/", 1)[1])
        if offset >= total:
            if len(remoto_por_id) != total:
                typer.secho("FAIL: contagem remota incompatível", fg=typer.colors.RED)
                raise typer.Exit(2)
            break
        if not lote:
            typer.secho("FAIL: paginação remota interrompida", fg=typer.colors.RED)
            raise typer.Exit(2)

    apenas_local = sorted(set(local_por_id) - set(remoto_por_id))
    apenas_remoto = sorted(set(remoto_por_id) - set(local_por_id))
    divergentes = sorted(
        i for i in set(local_por_id) & set(remoto_por_id) if local_por_id[i] != remoto_por_id[i]
    )

    typer.echo(f"Local: {len(local_por_id)} átomos | Supabase: {len(remoto_por_id)} átomos")
    drift = False
    if apenas_remoto:
        typer.secho(f"DRIFT: no Supabase sem baseline Git: {apenas_remoto[:10]}", fg=typer.colors.RED)
        drift = True
    if divergentes:
        typer.secho(f"DRIFT: conteúdo divergente (hash): {divergentes[:10]}", fg=typer.colors.RED)
        drift = True
    if apenas_local:
        typer.secho(
            f"AVISO: no Git e ainda não publicados: {apenas_local[:10]} (não é drift)",
            fg=typer.colors.YELLOW,
        )
    if drift:
        raise typer.Exit(2)
    typer.secho("PASS: sem drift entre Git e Supabase", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
