"""
Re-verificação periódica de vigência (GAP-06).

A publicação não encerra a responsabilidade sobre o conteúdo (decisão de
13/09/2026). Átomos com status 'Vigente' cuja verificação é mais antiga que o
limite entram em violação e o job falha, exigindo nova verificação com
evidência. Corpus ausente é reportado como tal — nunca como sucesso implícito
de verificação.
"""
import json
from datetime import date
from pathlib import Path

import typer

app = typer.Typer(help="Re-verificação periódica de vigência do corpus")

CAMINHOS_CORPUS = [Path("data/atomos.json"), Path("data/pipeline/atomos.json")]


@app.callback()
def _callback():
    """Força o modo subcomando."""


@app.command()
def run(max_idade_dias: int = typer.Option(90, "--max-idade-dias")):
    corpora = [p for p in CAMINHOS_CORPUS if p.exists()]
    if not corpora:
        typer.secho(
            "Nenhum corpus local encontrado (data/atomos.json). Nada a re-verificar "
            "neste repositório; o corpus publicado deve ser coberto pelo sync-check.",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit(0)

    hoje = date.today()
    violacoes = []
    total_vigentes = 0
    for caminho in corpora:
        atomos = json.loads(caminho.read_text())
        if isinstance(atomos, dict):
            atomos = [atomos]
        for atomo in atomos:
            if atomo.get("status") != "Vigente":
                continue
            total_vigentes += 1
            dv = atomo.get("data_verificacao")
            if not dv:
                violacoes.append((caminho, atomo.get("id_atomo"), "sem data_verificacao"))
                continue
            idade = (hoje - date.fromisoformat(dv)).days
            if idade > max_idade_dias:
                violacoes.append(
                    (caminho, atomo.get("id_atomo"), f"verificado há {idade} dias (limite {max_idade_dias})")
                )

    typer.echo(f"Átomos 'Vigente' avaliados: {total_vigentes}")
    if violacoes:
        for caminho, id_atomo, motivo in violacoes:
            typer.secho(f"FAIL [{caminho}] {id_atomo}: {motivo}", fg=typer.colors.RED)
        typer.secho(
            f"{len(violacoes)} átomo(s) exigem re-verificação de vigência com evidência.",
            fg=typer.colors.RED,
        )
        raise typer.Exit(2)
    typer.secho("PASS: nenhuma vigência vencida", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
