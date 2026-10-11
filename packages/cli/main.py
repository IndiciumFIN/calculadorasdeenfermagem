import typer
import json
import hashlib
from pathlib import Path
from datetime import date
import requests
from bs4 import BeautifulSoup

app = typer.Typer(help="CLI canônica - Calculadoras de Enfermagem\nIngestão, atomização e validação de normativos e conteúdos.")

@app.command()
def ingest(
    source: str = typer.Option(..., "--source", "-s", help="URL ou caminho de arquivo"),
    output: Path = typer.Option("data/raw.json", "--output", "-o"),
):
    """Ingesta normativo ou conteúdo (URL ou arquivo local)."""
    typer.echo(f"Ingerindo de: {source}")
    
    if source.startswith("http"):
        resp = requests.get(source, timeout=30, headers={"User-Agent": "CE-CLI/1.0"})
        resp.raise_for_status()
        text = BeautifulSoup(resp.text, "html.parser").get_text(separator="\n", strip=True)
        origem = source
    else:
        path = Path(source)
        if not path.exists():
            typer.secho("Arquivo não encontrado", fg=typer.colors.RED)
            raise typer.Exit(1)
        text = path.read_text(encoding="utf-8")
        origem = str(path)
    
    payload = {
        "origem": origem,
        "texto_bruto": text[:50000],  # limite seguro
        "hash": hashlib.sha256(text.encode()).hexdigest()[:16],
        "data_ingestao": str(date.today()),
        "tipo": "normativo_ou_conteudo"
    }
    
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    typer.secho(f"✓ Ingestão salva em {output}", fg=typer.colors.GREEN)

@app.command()
def process(
    input_file: Path = typer.Option(..., "--input", "-i"),
    output: Path = typer.Option("data/atomos.json", "--output", "-o"),
):
    """Processa texto bruto em átomos (versão determinística simples)."""
    data = json.loads(input_file.read_text())
    texto = data.get("texto_bruto", "")
    
    # Extração simples baseada em artigos (placeholder robusto)
    atomos = []
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    for i, linha in enumerate(linhas[:20]):  # limita para demo
        if any(x in linha.lower() for x in ["art.", "artigo", "§", "inciso"]):
            atomos.append({
                "id_atomo": f"NORM-{date.today().year}-{i+1:03d}",
                "texto_regra": linha[:400],
                "dispositivo_legal": linha[:80],
                "norma_origem": data.get("origem", "desconhecida"),
                "link_fonte": data.get("origem", ""),
                "status": "Vigente",
                "data_verificacao": str(date.today()),
                "versao_contrato": "1.0.0"
            })
    
    output.write_text(json.dumps(atomos, ensure_ascii=False, indent=2))
    typer.secho(f"✓ {len(atomos)} átomos gerados em {output}", fg=typer.colors.GREEN)

@app.command()
def validate(
    input_file: Path = typer.Option(..., "--input", "-i"),
):
    """Valida átomos contra o contrato."""
    from packages.schemas.atomo import AtomoNormativo
    data = json.loads(input_file.read_text())
    if isinstance(data, dict):
        data = [data]
    
    validos = 0
    for item in data:
        try:
            AtomoNormativo(**item)
            validos += 1
        except Exception as e:
            typer.secho(f"Erro: {e}", fg=typer.colors.RED)
    
    typer.secho(f"✓ {validos}/{len(data)} válidos", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()
