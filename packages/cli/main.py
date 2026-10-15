import json
from datetime import date
from pathlib import Path

import typer

from packages.cli.auditor import auditar_omissao
from packages.cli.evidence import registrar_proveniencia
from packages.cli.sources import ALLOWED, INVALID, REFERENCE_ONLY, classificar_url
from packages.schemas.invariantes import LIMITE_TEXTO_REGRA, VERSAO_CONTRATO, AtomoBlindado

app = typer.Typer(help="CLI canônica e blindada - Calculadoras de Enfermagem")


@app.command()
def ingest(
    source: str = typer.Option(..., "--source", "-s"),
    output: Path = typer.Option("data/raw.json", "--output", "-o"),
    fonte: str = typer.Option("auto", "--fonte", help="auto | dou_federal | secundaria"),
):
    """Ingesta com allowlist de fontes, máscara auditável e hash duplo."""
    typer.echo(f"Ingerindo: {source} (fonte={fonte})")

    if source.startswith("http"):
        classificacao, fonte_tipo_allow = classificar_url(source)
        if classificacao == INVALID:
            typer.secho("FAIL: URL inválida", fg=typer.colors.RED)
            raise typer.Exit(2)
        if classificacao == REFERENCE_ONLY:
            typer.secho(
                "FAIL: domínio fora da allowlist de fontes oficiais. "
                "Classificação REFERENCE_ONLY: extração proibida (ver docs/SOURCES_HIERARCHY.md).",
                fg=typer.colors.RED,
            )
            raise typer.Exit(2)

        if fonte == "dou_federal" or (fonte == "auto" and fonte_tipo_allow == "DIARIO_OFICIAL_FEDERAL"):
            from packages.cli.adapters.dou import fetch_dou_federal
            payload = fetch_dou_federal(source)
        else:
            from packages.cli.adapters.secundaria import fetch_secundaria
            payload = fetch_secundaria(source)
    else:
        path = Path(source)
        if not path.exists():
            typer.secho("Arquivo não encontrado", fg=typer.colors.RED)
            raise typer.Exit(1)
        text = path.read_text(encoding="utf-8")
        evidencia = registrar_proveniencia(text, origem=source)
        payload = {
            "origem": source,
            "fonte_tipo": "ARQUIVO_LOCAL",
            "texto_sanitizado": evidencia["texto_sanitizado"],
            "hash": evidencia["sha256_transformado"],
            "sha256_original": evidencia["sha256_original"],
            "sha256_transformado": evidencia["sha256_transformado"],
            "mascara_diff": evidencia["mascara_diff"],
            "data_ingestao": str(date.today()),
        }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    typer.secho(
        f"✓ Ingestão salva (tipo: {payload.get('fonte_tipo')}, "
        f"sha_original: {payload.get('sha256_original', '')[:12]}…)",
        fg=typer.colors.GREEN,
    )


@app.command()
def process(
    input_file: Path = typer.Option(..., "--input", "-i"),
    output: Path = typer.Option("data/atomos.json", "--output", "-o"),
    block_on_omission: bool = typer.Option(
        True,
        "--block-on-omission/--no-block-on-omission",
        help="Omissão crítica bloqueia por padrão (GOV-006).",
    ),
):
    """Atomização heurística: processa TODAS as linhas elegíveis, sem vigência automática."""
    data = json.loads(input_file.read_text())
    texto = data.get("texto_sanitizado") or ""
    atomos = []
    linhas = [l.strip() for l in texto.split("\n") if len(l.strip()) > 40]
    has_critical = False
    # Sem corte: limitar a extração às primeiras N linhas gerava sucesso
    # parcial silencioso (GOV-005, confirmado no teste T4).
    for i, linha in enumerate(linhas):
        if any(k in linha.lower() for k in ["art.", "artigo", "§", "inciso", "parágrafo"]):
            texto_regra = linha
            if len(texto_regra) > LIMITE_TEXTO_REGRA:
                audit = {
                    "omissao_critica": True,
                    "motivo": "texto_acima_do_contrato",
                    "caracteres": len(texto_regra),
                    "numeros_omitidos": [],
                }
            else:
                audit = auditar_omissao(linha, texto_regra)
            atomo = {
                "id_atomo": f"NORM-{date.today().year}-{i+1:03d}",
                "texto_regra": texto_regra,
                "dispositivo_legal": linha,
                "norma_origem": data.get("origem", "desconhecida"),
                "link_fonte": data.get("origem", ""),
                # Vigência NUNCA é atribuída na extração (GOV-004). A promoção
                # a 'Vigente' exige verificação com evidência (schema v1.2.0).
                "status": "Não verificado",
                "data_verificacao": None,
                "versao_contrato": VERSAO_CONTRATO,
                "fonte_tipo": data.get("fonte_tipo", "GENERICA"),
            }
            atomo["_auditoria"] = audit
            if audit.get("omissao_critica"):
                has_critical = True
            atomos.append(atomo)

    if not atomos:
        typer.secho(
            "FAIL: nenhum átomo extraído. Corpus vazio não é sucesso (teste T1/T4).",
            fg=typer.colors.RED,
        )
        raise typer.Exit(2)

    # Auditoria de corpus: números presentes no documento que não aparecem em
    # nenhum átomo indicam dispositivos não capturados pela atomização.
    corpus_audit = auditar_omissao(texto, "\n".join(a["texto_regra"] for a in atomos))
    if corpus_audit.get("omissao_critica"):
        has_critical = True
        typer.secho(
            f"Omissão no corpus: números do documento ausentes dos átomos: "
            f"{sorted(corpus_audit.get('numeros_omitidos', []))[:10]}",
            fg=typer.colors.YELLOW,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(atomos, ensure_ascii=False, indent=2))
    typer.secho(f"✓ {len(atomos)} átomos de {len(linhas)} linhas elegíveis", fg=typer.colors.GREEN)
    if block_on_omission and has_critical:
        typer.secho("FAIL: omissão crítica detectada (gate obrigatório)", fg=typer.colors.RED)
        raise typer.Exit(2)


@app.command()
def validate(input_file: Path = typer.Option(..., "--input", "-i")):
    """Validação fail-closed: corpus vazio e omissão crítica reprovam."""
    data = json.loads(input_file.read_text())
    if isinstance(data, dict):
        data = [data]

    if len(data) == 0:
        typer.secho(
            "FAIL: corpus vazio. Zero átomos não é um resultado válido (teste T1).",
            fg=typer.colors.RED,
        )
        raise typer.Exit(2)

    validos = 0
    for item in data:
        # A auditoria embutida é verificada ANTES de ser removida: descartar
        # _auditoria sem ler permitia aprovar omissões críticas (teste T2).
        auditoria = item.get("_auditoria") or {}
        if auditoria.get("omissao_critica"):
            typer.secho(
                f"✗ {item.get('id_atomo', '?')}: omissão crítica registrada na auditoria "
                f"({auditoria.get('numeros_omitidos')})",
                fg=typer.colors.RED,
            )
            continue
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
