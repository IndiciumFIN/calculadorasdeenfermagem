"""
Migração do acervo legado (planilhas NORMATIVE_ATOMS do Drive) para o
contrato AtomoBlindado v1.2.0.

Regras:
- Cada linha vira candidato com status 'Não verificado'. Vigência não é
  herdada da planilha (GOV-004): o status legado fica só na proveniência.
- Texto acima de 800 caracteres ou abaixo de 10 vai para quarentena com o
  texto integral. Não há truncamento (GOV-005).
- O mesmo NORM_ATOM_ID com textos diferentes vai inteiro para quarentena
  (nenhuma cópia vira candidato). Duplicata idêntica é deduplicada.
- id_atomo é determinístico: NORM-{ano}-{sha256(legacy_id)[:12] em decimal}.
- link_fonte aponta para a planilha de origem no Drive (de onde o texto foi
  retirado). Não é o diário oficial; por isso o átomo não pode nascer Vigente.
- Fail-closed (exit 2): arquivo ausente, coluna obrigatória ausente, colisão
  de id canônico, corpus candidato vazio ou rejeição inesperada do contrato.
"""
import csv
import hashlib
import json
import re
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

import typer

from packages.schemas.invariantes import VERSAO_CONTRATO, AtomoBlindado

app = typer.Typer(help="Migra átomos legados das planilhas do Drive para o contrato governado")

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
TAG_T = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"

COL_ID = "NORM_ATOM_ID"
COL_DOC = "DOCUMENT_ID"
COL_TIPO = "Tipo"
COL_TEXTO = "Texto atômico"
COL_DISP = "Artigo/Seção"
COLUNAS = [COL_ID, COL_DOC, COL_TIPO, COL_TEXTO, COL_DISP, "Status", "Evidence span", "Effective from", "Effective to"]

ANO = re.compile(r"(?:19|20)\d{2}")
TERMOS_OPINATIVOS = ["infelizmente", "importante destacar", "recomenda-se", "sugerimos"]


@app.callback()
def _callback():
    """Força o modo subcomando mesmo com um único comando registrado."""


def _fail(msg: str):
    typer.secho(f"FAIL: {msg}", fg=typer.colors.RED)
    raise typer.Exit(2)


def _sha256_arquivo(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for bloco in iter(lambda: fh.read(1 << 20), b""):
            digest.update(bloco)
    return digest.hexdigest()


def _id_canonico(legacy_id: str, ano: str) -> str:
    numero = int(hashlib.sha256(legacy_id.encode("utf-8")).hexdigest()[:12], 16)
    return f"NORM-{ano}-{numero}"


def _coluna(ref: str) -> int:
    letras = re.match(r"[A-Z]+", ref)
    if not letras:
        return 0
    idx = 0
    for ch in letras.group(0):
        idx = idx * 26 + (ord(ch) - 64)
    return idx - 1


def _ler_xlsx(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as pacote:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in pacote.namelist():
            raiz = ET.fromstring(pacote.read("xl/sharedStrings.xml"))
            for si in raiz.findall("m:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(TAG_T)))
        folha = "xl/worksheets/sheet1.xml"
        if folha not in pacote.namelist():
            _fail(f"{path.name}: planilha sem sheet1.xml")
        raiz = ET.fromstring(pacote.read(folha))

    linhas: list[list[str]] = []
    for row in raiz.findall("m:sheetData/m:row", NS):
        valores: list[str] = []
        for celula in row.findall("m:c", NS):
            idx = _coluna(celula.attrib.get("r", ""))
            while len(valores) <= idx:
                valores.append("")
            tipo = celula.attrib.get("t")
            v = celula.find("m:v", NS)
            inline = celula.find("m:is", NS)
            if tipo == "s" and v is not None and v.text:
                valores[idx] = shared[int(v.text)]
            elif tipo == "inlineStr" and inline is not None:
                valores[idx] = "".join(t.text or "" for t in inline.iter(TAG_T))
            elif v is not None and v.text:
                valores[idx] = v.text
        if any(valores):
            linhas.append(valores)
    if not linhas:
        _fail(f"{path.name}: planilha vazia")
    cabecalho = linhas[0]
    tabela = []
    for valores in linhas[1:]:
        if len(valores) < len(cabecalho):
            valores = valores + [""] * (len(cabecalho) - len(valores))
        tabela.append(dict(zip(cabecalho, valores)))
    return tabela


def _ler_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def ler_tabela(path: Path) -> list[dict]:
    if path.suffix.lower() == ".csv":
        return _ler_csv(path)
    if path.suffix.lower() == ".xlsx":
        return _ler_xlsx(path)
    _fail(f"formato não suportado: {path.name}")
    raise AssertionError


def _motivo_estrutural(row: dict) -> str | None:
    legacy = (row.get(COL_ID) or "").strip()
    documento = (row.get(COL_DOC) or "").strip()
    texto = (row.get(COL_TEXTO) or "").strip()
    if not legacy:
        return "id_legado_ausente"
    if not documento:
        return "sem_norma"
    if not ANO.search(documento) and not ANO.search(legacy):
        return "sem_ano"
    if len(texto) < 10:
        return "texto_curto"
    if len(texto) > 800:
        return "texto_acima_do_contrato"
    if any(termo in texto.lower() for termo in TERMOS_OPINATIVOS):
        return "termo_opinativo"
    dispositivo = (row.get(COL_DISP) or "").strip() or (row.get(COL_TIPO) or "").strip()
    if len(dispositivo) < 3:
        return "sem_dispositivo"
    return None


def _montar_atomo(row: dict, link_fonte: str) -> dict:
    legacy = row[COL_ID].strip()
    documento = row[COL_DOC].strip()
    ano = (ANO.search(documento) or ANO.search(legacy)).group(0)
    dispositivo = (row.get(COL_DISP) or "").strip() or (row.get(COL_TIPO) or "").strip()
    return {
        "id_atomo": _id_canonico(legacy, ano),
        "texto_regra": row[COL_TEXTO].strip(),
        "dispositivo_legal": dispositivo,
        "norma_origem": documento,
        "link_fonte": link_fonte,
        "status": "Não verificado",
        "data_verificacao": None,
        "versao_contrato": VERSAO_CONTRATO,
        "fonte_tipo": "LEGADO_DRIVE",
    }


def _registro_base(row: dict, arquivo: str, linha: int) -> dict:
    return {
        "arquivo": arquivo,
        "linha": linha,
        "legacy_id": (row.get(COL_ID) or "").strip(),
        "document_id": (row.get(COL_DOC) or "").strip(),
        "tipo": (row.get(COL_TIPO) or "").strip(),
        "status_legado": (row.get("Status") or "").strip(),
        "evidence_span": (row.get("Evidence span") or "").strip(),
        "effective_from": (row.get("Effective from") or "").strip(),
        "effective_to": (row.get("Effective to") or "").strip(),
        "texto_regra": (row.get(COL_TEXTO) or "").strip(),
    }


def migrar(fontes_dir: Path, saida_dir: Path) -> dict:
    manifesto_path = fontes_dir / "manifest.json"
    if not manifesto_path.exists():
        _fail(f"manifesto de fontes ausente: {manifesto_path}")
    manifesto = json.loads(manifesto_path.read_text(encoding="utf-8"))
    entradas = manifesto.get("arquivos") or []
    if not entradas:
        _fail("manifesto de fontes sem arquivos")

    grupos: dict[str, list[dict]] = defaultdict(list)
    por_arquivo: dict[str, dict] = {}
    for entrada in entradas:
        nome = entrada["arquivo"]
        drive_id = entrada.get("drive_file_id", "").strip()
        if not drive_id:
            _fail(f"{nome}: drive_file_id ausente no manifesto")
        path = fontes_dir / nome
        if not path.exists():
            _fail(f"arquivo de fonte ausente: {path}")
        tabela = ler_tabela(path)
        if not tabela:
            _fail(f"{nome}: tabela sem linhas")
        faltando = [c for c in (COL_ID, COL_DOC, COL_TEXTO) if c not in tabela[0]]
        if faltando:
            _fail(f"{nome}: colunas obrigatórias ausentes: {faltando}")
        por_arquivo[nome] = {
            "drive_file_id": drive_id,
            "sha256": _sha256_arquivo(path),
            "linhas": len(tabela),
            "link_fonte": f"https://docs.google.com/spreadsheets/d/{drive_id}",
        }
        for i, row in enumerate(tabela, start=2):
            item = _registro_base(row, nome, i)
            item["link_fonte"] = por_arquivo[nome]["link_fonte"]
            item["sha256_arquivo"] = por_arquivo[nome]["sha256"]
            item["row"] = row
            grupos[item["legacy_id"] or f"__sem_id_{nome}_{i}"].append(item)

    candidatos: list[dict] = []
    proveniencia: list[dict] = []
    quarentena: list[dict] = []
    motivos: dict[str, int] = defaultdict(int)
    ids_canonicos: dict[str, str] = {}

    for legacy_id, itens in grupos.items():
        textos = {it["texto_regra"] for it in itens}
        if legacy_id and len(itens) > 1 and len(textos) > 1:
            for it in itens:
                motivos["conflito_duplicata"] += 1
                reg = {k: v for k, v in it.items() if k != "row"}
                reg["motivo"] = "conflito_duplicata"
                quarentena.append(reg)
            continue
        principal = itens[0]
        for extra in itens[1:]:
            motivos["duplicata_identica"] += 1
        motivo = _motivo_estrutural(principal["row"])
        if motivo:
            motivos[motivo] += 1
            reg = {k: v for k, v in principal.items() if k != "row"}
            reg["motivo"] = motivo
            quarentena.append(reg)
            continue
        atomo = _montar_atomo(principal["row"], principal["link_fonte"])
        try:
            AtomoBlindado(**atomo)
        except Exception as exc:
            motivos["contrato_inesperado"] += 1
            reg = {k: v for k, v in principal.items() if k != "row"}
            reg["motivo"] = "contrato_inesperado"
            reg["detalhe"] = str(exc)
            quarentena.append(reg)
            continue
        anterior = ids_canonicos.get(atomo["id_atomo"])
        if anterior is not None and anterior != legacy_id:
            _fail(
                f"colisão de id canônico {atomo['id_atomo']} entre "
                f"'{anterior}' e '{legacy_id}'"
            )
        ids_canonicos[atomo["id_atomo"]] = legacy_id
        candidatos.append(atomo)
        prov = {k: v for k, v in principal.items() if k not in ("row", "texto_regra")}
        prov["id_atomo"] = atomo["id_atomo"]
        prov["copias_identicas"] = len(itens)
        proveniencia.append(prov)

    if not candidatos:
        _fail("nenhum candidato produzido")
    if motivos.get("contrato_inesperado"):
        _escrever(saida_dir, candidatos, proveniencia, quarentena, por_arquivo, motivos, manifesto)
        _fail(f"{motivos['contrato_inesperado']} linhas rejeitadas pelo contrato de forma inesperada")

    resumo = _escrever(saida_dir, candidatos, proveniencia, quarentena, por_arquivo, motivos, manifesto)
    return resumo


def _escrever(saida_dir, candidatos, proveniencia, quarentena, por_arquivo, motivos, manifesto) -> dict:
    saida_dir.mkdir(parents=True, exist_ok=True)
    (saida_dir / "atomos_candidatos.json").write_text(
        json.dumps(candidatos, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (saida_dir / "proveniencia.jsonl").write_text(
        "".join(json.dumps(p, ensure_ascii=False) + "\n" for p in proveniencia), encoding="utf-8"
    )
    (saida_dir / "quarentena.jsonl").write_text(
        "".join(json.dumps(q, ensure_ascii=False) + "\n" for q in quarentena), encoding="utf-8"
    )
    resumo = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "versao_contrato": VERSAO_CONTRATO,
        "regra": (
            "Candidatos do acervo legado. status sempre Não verificado. "
            "link_fonte é a planilha de origem no Drive, não o diário oficial. "
            "Nada aqui é Vigente."
        ),
        "origem_manifesto": manifesto.get("origem"),
        "fontes": por_arquivo,
        "candidatos": len(candidatos),
        "quarentena": len(quarentena),
        "proveniencia": len(proveniencia),
        "motivos": dict(sorted(motivos.items())),
        "status_distintos": sorted({a["status"] for a in candidatos}),
        "notas": [
            "Nenhum candidato nasce Vigente. link_fonte é a planilha de origem no Drive, não o diário oficial.",
            "termo_opinativo: o contrato v1.2.0 rejeita o vocábulo 'recomenda-se' mesmo quando ele é o verbo da própria norma. O texto integral fica na quarentena até decisão de contrato.",
            "conflito_duplicata: o mesmo NORM_ATOM_ID com textos diferentes não escolhe lado; as duas cópias ficam na quarentena.",
            "texto_acima_do_contrato e texto_curto preservam o texto integral, sem truncar.",
            "O Supabase (schema public) não contém tabela de normativos; nada foi lido nem apagado lá. As planilhas de origem permanecem no Drive.",
        ],
    }
    (saida_dir / "resumo.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return resumo


@app.command()
def run(
    fontes: Path = typer.Option(Path("data/legado/fontes"), "--fontes"),
    saida: Path = typer.Option(Path("data/legado"), "--saida"),
):
    """Converte as planilhas legadas em candidatos AtomoBlindado + quarentena."""
    resumo = migrar(fontes, saida)
    typer.secho(
        f"✓ {resumo['candidatos']} candidatos, {resumo['quarentena']} em quarentena "
        f"({resumo['motivos']})",
        fg=typer.colors.GREEN,
    )


if __name__ == "__main__":
    app()
