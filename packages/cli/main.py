import typer
import json
from pathlib import Path
from datetime import date
import requests
from bs4 import BeautifulSoup

from packages.cli.utils import aplicar_mascara, calcular_hash
from packages.cli.auditor import auditar_omissao
from packages.schemas.invariantes import AtomoBlindado

app = typer.Typer(help="CLI canônica e blindada - Calculadoras de Enfermagem")

@app.command()
def ingest(
    source: str = typer.Option(..., "--source", "-s"),
    output: Path = typer.Option("data/raw.json", "--output", "-o"),
):
    """Ingesta + máscara + hash."""
    typer.echo(f"Ingerindo: {source}")
    
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
        "texto_bruto_original": text[:30000],
        "texto_sanitizado": texto_limpo[:30000],
        "hash": calcular_hash(texto_limpo),
        "data_ingestao": str(date.today())
    }
    
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    typer.secho(f"✓ Ingestão + máscara salva em {output}", fg=typer.colors.GREEN)

@app.command()
def process(
    input_file: Path = typer.Option(..., "--input", "-i"),
    output: Path = typer.Option("data/atomos.json", "--output", "-o"),
    block_on_omission: bool = typer.Option(False, "--block-on-omission", help="Exit 2 se houver omissão crítica"),
):
    """Gera átomos + auditoria de omissão."""
    data = json.loads(input_file.read_text())
    texto = data.get("texto_sanitizado") or data.get("texto_bruto_original", "")
    
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
                "versao_contrato": "1.1.0"
            }
            audit = auditar_omissao(texto, atomo["texto_regra"])
            atomo["_auditoria"] = audit
            if audit["omissao_critica"]:
                has_critical = True
                typer.secho(f"⚠ Omissão detectada no átomo {atomo['id_atomo']}: {audit['numeros_omitidos']}", fg=typer.colors.YELLOW)
            atomos.append(atomo)

    output.write_text(json.dumps(atomos, ensure_ascii=False, indent=2))
    typer.secho(f"✓ {len(atomos)} átomos gerados (com auditoria)", fg=typer.colors.GREEN)
    
    if block_on_omission and has_critical:
        typer.secho("BLOCK: omissão crítica detectada. Use --block-on-omission=false para apenas avisar.", fg=typer.colors.RED)
        raise typer.Exit(2)

@app.command()
def validate(
    input_file: Path = typer.Option(..., "--input", "-i"),
):
    """Valida com invariantes blindados."""
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
            typer.secho(f"✗ Rejeitado: {e}", fg=typer.colors.RED)
    
    if validos == len(data):
        typer.secho(f"✓ Todos os {validos} átomos passaram nas invariantes", fg=typer.colors.GREEN)
    else:
        typer.secho(f"{validos}/{len(data)} válidos", fg=typer.colors.YELLOW)
        raise typer.Exit(2)

if __name__ == "__main__":
    app()
