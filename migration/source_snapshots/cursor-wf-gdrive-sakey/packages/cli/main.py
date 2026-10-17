import typer
import json
from pathlib import Path
from datetime import date
import requests
from bs4 import BeautifulSoup

from packages.cli.utils import aplicar_mascara, calcular_hash
from packages.cli.auditor import auditar_omissao
from packages.schemas.invariantes import AtomoBlindado
from packages.cli.adapters.dou import fetch_dou_federal
from packages.cli.adapters.secundaria import fetch_secundaria

app = typer.Typer(help="CLI canônica e blindada - Calculadoras de Enfermagem")

@app.command()
def ingest(
    source: str = typer.Option(..., "--source", "-s"),
    output: Path = typer.Option("data/raw.json", "--output", "-o"),
    fonte: str = typer.Option("auto", "--fonte", help="auto | dou_federal | secundaria"),
):
    """Ingesta + máscara + hash."""
    typer.echo(f"Ingerindo: {source} (fonte={fonte})")
    
    if fonte == "dou_federal" or (fonte == "auto" and "in.gov.br" in source):
        payload = fetch_dou_federal(source)
    elif fonte == "secundaria":
        payload = fetch_secundaria(source)
    else:
        if source.startswith("http"):
            resp = requests.get(source, timeout=30, headers={"User-Agent": "Mozilla/5.0 CE-CLI/1.1"})
            resp.raise_for_status()
            text = BeautifulSoup(resp.text, "html.parser").get_text(separator="\n", strip=True)
        else:
            path = Path(source)
            if not path.exists():
                typer.secho("Arquivo não encontrado", fg=typer.colors.RED)
                raise typer.Exit(1)
            text = path.read_text(encoding="utf-8")
        texto_limpo = aplicar_mascara(text)
        payload = {
            "origem": source,
            "fonte_tipo": "GENERICA",
            "texto_sanitizado": texto_limpo[:30000],
            "hash": calcular_hash(texto_limpo),
            "data_ingestao": str(date.today())
        }
    
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    typer.secho(f"✓ Ingestão salva (tipo: {payload.get('fonte_tipo', payload.get('esfera'))})", fg=typer.colors.GREEN)

@app.command()
def process(
    input_file: Path = typer.Option(..., "--input", "-i"),
    output: Path = typer.Option("data/atomos.json", "--output", "-o"),
    block_on_omission: bool = typer.Option(False, "--block-on-omission"),
):
    data = json.loads(input_file.read_text())
    texto = data.get("texto_sanitizado") or ""
    atomos = []
    linhas = [l.strip() for l in texto.split("\n") if len(l.strip()) > 40]
    has_critical = False
    for i, linha in enumerate(linhas[:15]):
        if any(k in linha.lower() for k in ["art.", "artigo", "§", "inciso", "parágrafo"]):
            atomo = {
                "id_atomo": f"NORM-{date.today().year}-{i+1:03d}",
                "texto_regra": linha[:500],
                "dispositivo_legal": linha[:100],
                "norma_origem": data.get("origem", "desconhecida"),
                "link_fonte": data.get("origem", "https://example.com"),
                "status": "Vigente",
                "data_verificacao": str(date.today()),
                "versao_contrato": "1.1.0",
                "fonte_tipo": data.get("fonte_tipo", "GENERICA")
            }
            audit = auditar_omissao(texto, atomo["texto_regra"])
            atomo["_auditoria"] = audit
            if audit.get("omissao_critica"):
                has_critical = True
            atomos.append(atomo)
    output.write_text(json.dumps(atomos, ensure_ascii=False, indent=2))
    typer.secho(f"✓ {len(atomos)} átomos", fg=typer.colors.GREEN)
    if block_on_omission and has_critical:
        raise typer.Exit(2)

@app.command()
def validate(input_file: Path = typer.Option(..., "--input", "-i")):
    data = json.loads(input_file.read_text())
    if isinstance(data, dict):
        data = [data]
    validos = 0
    for item in data:
        item_limpo = {k: v for k, v in item.items() if not k.startswith('_')}
        try:
            AtomoBlindado(**item_limpo)
            validos += 1
        except Exception as e:
            typer.secho(f"✗ {e}", fg=typer.colors.RED)
    if validos != len(data):
        raise typer.Exit(2)
    typer.secho(f"✓ {validos} válidos", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()
