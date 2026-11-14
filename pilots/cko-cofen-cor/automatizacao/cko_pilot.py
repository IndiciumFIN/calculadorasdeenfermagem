#!/usr/bin/env python3
"""cko_pilot.py — Extrator local ponta a ponta para normativos CKO (COFEN/COREN/Senado).

Escopo declarado
-----------------
Ferramenta de INGESTÃO OFFLINE. Ela adquire, extrai, segmenta, liga e valida.
Ela NÃO decide vigência jurídica, NÃO aprova clinical, NÃO emite direitos e
NÃO libera publicação. Todo átomo sai como CANDIDATE; a decisão é humana.

Cadeia (POP-CKO-NORM-001, 18 etapas)
------------------------------------
  00 escopo      -> fontes/fontes.json
  01-02 fonte    -> registros/00_source_registry.csv, 01_rights_by_operation.csv
  03-04 versao   -> registros/02_document_versions.csv (vigencia declarada)
  06 aquisicao  -> dados/<ACT_ID>/raw/ + acquisition.json  (sha256 + headers HTTP)
  07 derivacao  -> dados/<ACT_ID>/derivado/texto.txt  (sha256 do original e do derivado)
  08 parse       -> dados/<ACT_ID>/derivado/structure_tree.json
  09 cobertura   -> dados/<ACT_ID>/derivado/coverage_ledger.csv
  10 evidencia   -> dados/<ACT_ID>/atoms/evidence_atoms.jsonl
  10-12 atomos   -> dados/<ACT_ID>/atoms/norm_atoms_candidates.jsonl
                     dados/<ACT_ID>/atoms/clinical_claims_candidates.jsonl
  11 relacoes    -> dados/<ACT_ID>/atoms/relations_candidates.jsonl
  13 conflitos   -> dados/<ACT_ID>/atoms/conflicts.csv
  15-16 conteudo -> conteudo/content_master.md
  14 QA          -> gates/test_report.json
  17-18 release  -> publication_decision.json (HOLD por padrao)

Princípio do binding
--------------------
A atomização é juízo humano e fica em um PLANO declarativo (planos/<ACT>.json).
A ferramenta NÃO inventa átomos: ela amarra cada átomo do plano a um fragmento
de evidência REAL (locator + fragment_sha256 conferidos contra o derivado
extraído). Átomo sem evidência real morre no gate. É o portão que impede a
afirmação sem fonte — o defeito mais caro em entrega normativa.

Isolamento de rede
------------------
--offline não toca a rede. Somente `fetch` faz rede. Todo download grava status
HTTP, cabeçalhos, redirects, retrieved_at e sha256 do corpo efetivo.

Uso
---
  python3 cko_pilot.py fetch     --fontes fontes/fontes.json --root .
  python3 cko_pilot.py extract   --root .
  python3 cko_pilot.py segment   --root .
  python3 cko_pilot.py plan      --root .
  python3 cko_pilot.py register  --root .
  python3 cko_pilot.py validate  --root .
  python3 cko_pilot.py gate      --root .
  python3 cko_pilot.py run       --root .            # tudo, em ordem
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html as html_mod
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA_FONTES = "CKO-PILOT-FONTES-v1.0.0"
SCHEMA_ACQ = "CKO-PILOT-ACQUISITION-v1.0.0"
SCHEMA_EXTR = "CKO-PILOT-EXTRACTION-v1.0.0"
SCHEMA_SEG = "CKO-PILOT-STRUCTURE-v1.0.0"
SCHEMA_ATOMS = "CKO-PILOT-ATOMS-v1.0.0"

UA_DEFAULT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
)

# Basis legal de direitos: atos normativos oficiais de Playing card? nao.
# Lei 9.610/1998, art. 8o, IV: exclui os textos de atos oficiais da
# protecao autoral. A classificacao de materiais agregados, traducoes,
# fotografias e conteudos editoriais exige revisao por FONTE e OPERACAO.
# Esta constante e informativa e NAO concede direito de publicacao.
BASE_DIREITOS = (
    "Lei 9.610/1998 art. 8o IV: textos de leis, decretos, regulamentos, "
    "decisoes judiciais e demais atos oficiais; outros materiais exigem "
    "avaliacao independente de direitos por operacao"
)


# --------------------------------------------------------------------------- #
# utilitarios
# --------------------------------------------------------------------------- #
def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_text(txt: str) -> str:
    return sha256_bytes(txt.encode("utf-8"))


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_csv(path: Path, header: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=header, extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in header})


def log(msg: str) -> None:
    print(f"[cko-pilot] {msg}", flush=True)


# --------------------------------------------------------------------------- #
# 1. aquisicao (etapa 06)
# --------------------------------------------------------------------------- #
def http_fetch(url: str, ua: str, timeout: int = 60, retries: int = 2,
               accept: str | None = None) -> dict:
    """Baixa uma URL e devolve corpo + cabecalhos + cadeia de redirects + status."""
    last_error: str | None = None
    accept = accept or (
        "text/html,application/xhtml+xml,application/pdf,*/*")
    for attempt in range(1, retries + 1):
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": ua,
                "Accept": accept,
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            },
        )
        started = time.time()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = resp.read()
                return {
                    "ok": True,
                    "status": resp.status,
                    "final_url": resp.geturl(),
                    "content_type": resp.headers.get("Content-Type", ""),
                    "content_length_header": resp.headers.get("Content-Length", ""),
                    "headers": {k: v for k, v in resp.headers.items()},
                    "body": body,
                    "elapsed_ms": int((time.time() - started) * 1000),
                    "attempt": attempt,
                    "error": None,
                }
        except urllib.error.HTTPError as exc:
            last_error = f"HTTPError {exc.code}"
            # 4xx nao e retentavel (a nao ser 429); 5xx e 429 sao.
            if exc.code not in (429, 500, 502, 503, 504):
                break
            if attempt < retries:
                time.sleep(3 * attempt)
        except Exception as exc:  # noqa: BLE001 - erro de rede precisa virar dado
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep(3 * attempt)
    return {
        "ok": False,
        "status": 0,
        "final_url": url,
        "content_type": "",
        "content_length_header": "",
        "headers": {},
        "body": b"",
        "elapsed_ms": 0,
        "attempt": retries,
        "error": last_error,
    }


def cmd_fetch(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    fontes = read_json(Path(args.fontes))
    if fontes.get("schema") != SCHEMA_FONTES:
        log(f"HOLD: schema de fontes inesperado: {fontes.get('schema')}")
        return 2
    acts = fontes.get("acts", [])
    log(f"fontes declaradas: {len(acts)}")
    failures = 0
    for act in acts:
        act_id = act["act_id"]
        raw_dir = root / "dados" / act_id / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        url = act["official_primary_url"]
        name = act.get("raw_name") or _default_raw_name(url, act)
        target = raw_dir / name
        if target.exists() and not args.force:
            digest = sha256_bytes(target.read_bytes())
            log(f"  [cache] {act_id} {name} sha256={digest[:16]}...")
            _write_acquisition(root, act, target, cached=True,
                               extra={"sha256": digest, "bytes": target.stat().st_size})
            continue
        if args.offline:
            log(f"  [offline] {act_id}: sem rede e sem cache -> HOLD")
            failures += 1
            continue
        res = http_fetch(url, act.get("user_agent", UA_DEFAULT),
                         timeout=args.timeout, retries=args.retries,
                         accept=act.get("accept"))
        if not res["ok"] or not res["body"]:
            log(f"  [FALHA] {act_id} {url} -> {res['error']} status={res['status']}")
            failures += 1
            _write_acquisition(root, act, None, cached=False, extra=res)
            continue
        target.write_bytes(res["body"])
        digest = sha256_bytes(res["body"])
        log(f"  [ok] {act_id} {name} status={res['status']} "
            f"bytes={len(res['body'])} sha256={digest[:16]}...")
        _write_acquisition(root, act, target, cached=False,
                           extra={**res, "sha256": digest})
    log(f"fetch concluido: {len(acts) - failures}/{len(acts)} baixados")
    return 1 if failures else 0


def _default_raw_name(url: str, act: dict) -> str:
    path = urllib.parse.urlparse(url).path  # type: ignore[attr-defined]
    base = (path.rsplit("/", 1)[-1] or "index").strip() or "index"
    base = re.sub(r"[^A-Za-z0-9._-]", "_", base)
    if not Path(base).suffix:
        base += ".html"
    return base



def _safe_http_headers(headers: dict | None) -> dict:
    """Keep only essential, non-secret response metadata in custody records."""
    if not isinstance(headers, dict):
        return {}
    # Explicit, typed metadata. Do not persist opaque response headers such as
    # ETag (which may encode identifiers) or arbitrary Content-Type parameters.
    mime_re = re.compile(r"^[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+(?:\s*;\s*charset=[A-Za-z0-9._-]+)?$")
    result = {}
    for key, value in headers.items():
        name = str(key).strip()
        val = str(value).strip()
        normalized = name.lower()
        if len(val) > 128 or "\n" in val or "\r" in val:
            continue
        if normalized == "content-type" and mime_re.fullmatch(val):
            result[name] = val
        elif normalized == "content-length" and re.fullmatch(r"[0-9]{1,18}", val):
            result[name] = val
        elif normalized == "last-modified":
            from email.utils import parsedate_to_datetime
            try:
                parsed = parsedate_to_datetime(val)
            except (ValueError, TypeError, IndexError):
                continue
            if parsed.tzinfo is not None:
                result[name] = val
    return result


def _write_acquisition(root: Path, act: dict, target: Path | None,
                       cached: bool, extra: dict) -> None:
    path = root / "dados" / act["act_id"] / "acquisition.json"
    prev = _maybe(path) or {}
    status = extra.get("status", 0)
    final_url = extra.get("final_url", "")
    headers = extra.get("headers", {})
    # Em cache, o registro anterior e a fonte do status HTTP: o arquivo ja
    # foi baixado antes e o status e fato da AQUISICAO, nao do arquivo.
    if cached and not status:
        status = prev.get("http_status", 0)
        final_url = prev.get("http_final_url", final_url)
        headers = prev.get("http_headers", headers)
    headers = _safe_http_headers(headers)
    rec = {
        "schema": SCHEMA_ACQ,
        "act_id": act["act_id"],
        "source_id": act["source_id"],
        "official_primary_url": act["official_primary_url"],
        "acquired_at_utc": prev.get("acquired_at_utc") if cached and prev else now_utc(),
        "first_acquired_at_utc": prev.get("first_acquired_at_utc") or prev.get("acquired_at_utc") or now_utc(),
        "from_cache": cached,
        "raw_file": str(target.relative_to(root)) if target else None,
        "raw_bytes": extra.get("bytes", len(extra.get("body", b""))),
        "raw_sha256": extra.get("sha256"),
        "http_status": status,
        "http_content_type": extra.get("content_type", "") or prev.get("http_content_type", ""),
        "http_final_url": final_url,
        "http_headers": headers,
        "http_elapsed_ms": extra.get("elapsed_ms", 0),
        "http_attempt": extra.get("attempt", 1),
        "error": extra.get("error"),
        "rights_note": "coleta restrita ao ambiente de trabalho; sem redistribuicao",
    }
    write_json(path, rec)


# --------------------------------------------------------------------------- #
# 2. derivacao texto (etapa 07)
# --------------------------------------------------------------------------- #
_SCRIPT_STYLE = re.compile(
    r"<(script|style|noscript|svg|head)\b.*?</\1>", re.IGNORECASE | re.DOTALL
)
_BLOCK = re.compile(
    r"</(p|div|section|article|h[1-6]|li|tr|br)\s*>|<br\s*/?>", re.IGNORECASE
)


def html_to_text(raw: str) -> str:
    """HTML -> texto UTF-8 deterministico, sem dependencia externa."""
    body = raw
    m = re.search(r"<article\b[^>]*>(.*?)</article\s*>", body, re.IGNORECASE | re.DOTALL)
    if m:
        body = m.group(1)
    else:
        m = re.search(r'<div[^>]+class="[^"]*(?:entry-content|post-content)[^"]*"[^>]*>(.*)',
                      body, re.IGNORECASE | re.DOTALL)
        if m:
            body = m.group(1)
    body = _SCRIPT_STYLE.sub(" ", body)
    body = re.sub(r"<br\s*/?>", "\n", body, flags=re.IGNORECASE)
    body = re.sub(r"</(p|div|section|article|h[1-6]|li|tr)\s*>", "\n\n", body,
                  flags=re.IGNORECASE)
    body = re.sub(r"<[^>]+>", " ", body)
    body = html_mod.unescape(body)
    body = body.replace("\xa0", " ").replace(" ", " ").replace(" ", " ")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in body.split("\n")]
    out: list[str] = []
    blank = 0
    for ln in lines:
        if not ln:
            blank += 1
            if blank > 1:
                continue
        else:
            blank = 0
        out.append(ln)
    text = "\n".join(out).strip()
    return re.sub(r"\n{3,}", "\n\n", text) + "\n"


def pdf_to_text(raw: bytes) -> tuple[str, list[dict]]:
    """PDF -> texto + mapa de paginas (fonte: pypdf)."""
    try:
        from pypdf import PdfReader  # type: ignore
        import io
    except ImportError:  # pragma: no cover
        return "", []
    reader = PdfReader(io.BytesIO(raw))
    pages: list[dict] = []
    chunks: list[str] = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            t = page.extract_text() or ""
        except Exception as exc:  # noqa: BLE001
            t = ""
            pages.append({"page": i, "chars": 0, "error": f"{type(exc).__name__}"})
            continue
        chunks.append(f"[[pagina {i}]]\n{t}")
        pages.append({"page": i, "chars": len(t)})
    return "\n\n".join(chunks) + "\n", pages


def json_to_text(obj: Any) -> str:
    """API do Senado: extrai o conteudo textual dos dispositivos."""
    lines: list[str] = []
    det = obj.get("DetalheDocumento", {})
    for doc in (det.get("documentos", {}) or {}).get("documento", []) or []:
        ident = doc.get("identificacao", {}) or {}
        lines.append(f"{ident.get('normaNome', '')}")
        if doc.get("ementa"):
            lines.append(f"Ementa: {doc['ementa']}")
        for pub in (doc.get("publicacoes", {}) or {}).get("publicacao", []) or []:
            lines.append(f"Publicacao: {pub.get('fonte', '')} p.{pub.get('pagina', '')}")
        lines.append("")
        lines.append("DISPOSITIVOS")
        for disp in (doc.get("disps", {}) or {}).get("disp", []) or []:
            lines.append(f"- {disp.get('nomeDispositivo', '')}")
            refs = (disp.get("refs", {}) or {}).get("ref", []) or []
            for ref in refs:
                lines.append(f"    * {ref.get('dispositivo', '')} "
                             f"({ref.get('comentario', '')})")
    return "\n".join(lines).strip() + "\n" if lines else ""


def cmd_extract(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    fontes = read_json(Path(args.fontes))
    acts = fontes.get("acts", [])
    ok = 0
    for act in acts:
        act_id = act["act_id"]
        raw_dir = root / "dados" / act_id / "raw"
        raw_files = sorted(p for p in raw_dir.glob("*") if p.is_file()) if raw_dir.exists() else []
        if not raw_files:
            log(f"  [HOLD] {act_id}: sem original baixado")
            continue
        raw_path = raw_files[0]
        raw = raw_path.read_bytes()
        ctype = act.get("content_type", "")
        pages: list[dict] = []
        if raw_path.suffix.lower() == ".pdf" or "pdf" in ctype.lower():
            text, pages = pdf_to_text(raw)
            method = "pdf_text_layer(pypdf)"
        elif raw_path.suffix.lower() == ".json":
            text = json_to_text(json.loads(raw.decode("utf-8")))
            method = "senado_api_json_devices"
        else:
            text = html_to_text(raw.decode("utf-8", errors="replace"))
            method = "html_to_text(deterministic)"
        if not text.strip():
            log(f"  [HOLD] {act_id}: derivado vazio (method={method})")
            continue
        der_dir = root / "dados" / act_id / "derivado"
        der_dir.mkdir(parents=True, exist_ok=True)
        txt_path = der_dir / "texto.txt"
        txt_path.write_text(text, encoding="utf-8")
        rec = {
            "schema": SCHEMA_EXTR,
            "act_id": act_id,
            "document_version_id": act.get("document_version_id", f"DOC-{act_id}"),
            "source_id": act["source_id"],
            "official_primary_url": act["official_primary_url"],
            "extraction_run_id": f"RUN-{act_id}-{now_utc().replace(':', '').replace('-', '')}",
            "method": method,
            "tool": "cko_pilot.py",
            "tool_version": "1.0.0",
            "extracted_at_utc": now_utc(),
            "raw_file": str(raw_path.relative_to(root)),
            "raw_bytes": len(raw),
            "raw_sha256": sha256_bytes(raw),
            "derived_text_file": str(txt_path.relative_to(root)),
            "derived_text_bytes": len(text.encode("utf-8")),
            "derived_text_sha256": sha256_text(text),
            "page_map": pages,
            "ocr_used": False,
            "text_layer_quality": ("FULL" if pages and sum(p["chars"] for p in pages) > 200
                                   else ("PARTIAL" if pages else "N/A")),
            "rights_by_operation": act.get("rights_by_operation", {}),
            "rights_independently_verified": False,
            "publication_allowed": False,
            "clinical_decision_allowed": False,
        }
        write_json(root / "dados" / act_id / "extraction.json", rec)
        ok += 1
        log(f"  [ok] {act_id} derivado={rec['derived_text_bytes']}B "
            f"sha256={rec['derived_text_sha256'][:16]}... method={method}")
    log(f"extract concluido: {ok}/{len(acts)} derivados")
    return 0 if ok else 2


# --------------------------------------------------------------------------- #
# 3. segmentacao estrutural (etapas 08 e 09)
# --------------------------------------------------------------------------- #
def cmd_segment(args: argparse.Namespace) -> int:
    """Delega a segmentacao ao indexador do ANEXO (nao reimplementa o gate)."""
    root = Path(args.root).resolve()
    intake = root / "automatizacao" / "normative_candidate_intake.py"
    if not intake.exists():
        log("HOLD: indexador do anexo ausente")
        return 2
    fontes = read_json(Path(args.fontes))
    acts = fontes.get("acts", [])
    total_segs = 0
    for act in acts:
        act_id = act["act_id"]
        der_dir = root / "dados" / act_id / "derivado"
        txt = der_dir / "texto.txt"
        if not txt.exists():
            log(f"  [HOLD] {act_id}: sem texto derivado")
            continue
        out_dir = der_dir / "segmentacao"
        if out_dir.exists() and not args.force:
            report = read_json(out_dir / "report.json")
            total_segs += report.get("article_candidates", 0)
            log(f"  [cache] {act_id} artigos={report.get('article_candidates')}")
            continue
        manifest = {
            "source_id": act["source_id"],
            "document_version_id": act.get("document_version_id", f"DOC-{act_id}"),
            "official_primary_url": act["official_primary_url"],
            "issuer": act.get("issuer", act.get("authority", "")),
            "jurisdiction": act.get("jurisdiction", "BR"),
            "text_file": str(txt.resolve()),
            "expected_text_sha256": sha256_text(txt.read_text(encoding="utf-8")),
            "rights_by_operation": act.get("rights_by_operation", {}),
        }
        mpath = der_dir / "manifest.json"
        write_json(mpath, manifest)
        res = subprocess.run(
            [sys.executable, str(intake), "--manifest", str(mpath), "--output", str(out_dir)],
            capture_output=True, text=True,
        )
        # o indexador do anexo devolve exit 2 mesmo em sucesso (HOLD por design)
        if not (out_dir / "report.json").exists():
            log(f"  [FALHA] {act_id}: {res.stderr.strip()[:200]}")
            continue
        report = read_json(out_dir / "report.json")
        segs = [json.loads(x) for x in
                (out_dir / "candidate_segments.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        _build_structure_tree(root, act, report, segs)
        _build_coverage_ledger(root, act, report, segs)
        _build_evidence_atoms(root, act, report, segs)
        total_segs += len(segs)
        log(f"  [ok] {act_id} artigos={len(segs)} "
            f"unclassified_bytes={report.get('unclassified_bytes')} "
            f"issues={report.get('issue_codes')}")
    log(f"segment concluido: {total_segs} segmentos")
    return 0


def _build_structure_tree(root: Path, act: dict, report: dict, segs: list[dict]) -> None:
    nodes = []
    for i, s in enumerate(segs, start=1):
        nodes.append({
            "node_id": f"{act['act_id']}#N{i:03d}",
            "level": "dispositivo",
            "locator": s["locator_candidate"],
            "order": i,
            "utf8_byte_start": s["utf8_byte_start"],
            "utf8_byte_end": s["utf8_byte_end"],
            "utf8_byte_count": s["utf8_byte_count"],
            "fragment_sha256": s["fragment_sha256"],
            "parse_status": s["parse_status"],
            "normative_review": "PENDING",
            "clinical_review": "PENDING",
        })
    tree = {
        "schema": SCHEMA_SEG,
        "act_id": act["act_id"],
        "document_version_id": act.get("document_version_id", f"DOC-{act['act_id']}"),
        "source_id": act["source_id"],
        "official_primary_url": act["official_primary_url"],
        "declared_status": act.get("declared_status"),
        "root": {
            "node_id": f"{act['act_id']}#ROOT",
            "level": "documento",
            "title": act.get("title"),
            "children": [n["node_id"] for n in nodes],
        },
        "nodes": nodes,
        "counts": {
            "dispositivos": len(nodes),
            "bytes_estruturados": sum(n["utf8_byte_count"] for n in nodes),
            "bytes_nao_classificados": report.get("unclassified_bytes", 0),
        },
        "coverage_claim": "coverage_structure apenas; cobertura de evidencia e de "
                          "revisao humana sao denominadores distintos",
        "normative_review_status": "PENDING",
        "publication_allowed": False,
    }
    write_json(root / "dados" / act["act_id"] / "derivado" / "structure_tree.json", tree)


def _build_coverage_ledger(root: Path, act: dict, report: dict, segs: list[dict]) -> None:
    """Cada bloco recebe classificacao; o prefixo (preambulo) e classificado como CONTEXT."""
    header = ["document_version_id", "locator", "fragment_type", "byte_start", "byte_end",
              "classified_as", "normalized_ref", "reason_if_excluded", "reviewer",
              "review_status"]
    rows = []
    dvid = act.get("document_version_id", f"DOC-{act['act_id']}")
    if report.get("unclassified_bytes", 0) > 0:
        rows.append({
            "document_version_id": dvid,
            "locator": "PREÂMBULO/FRONTMATTER",
            "fragment_type": "PREAMBLE",
            "byte_start": 0,
            "byte_end": report.get("unclassified_bytes", 0),
            "classified_as": "CONTEXT",
            "normalized_ref": "",
            "reason_if_excluded": "preambulo/considerandos: fundamentam interpretacao, "
                                  "nao sao disposicao autonoma; ainda nao revisados",
            "reviewer": "",
            "review_status": "PENDING",
        })
    for s in segs:
        rows.append({
            "document_version_id": dvid,
            "locator": s["locator_candidate"],
            "fragment_type": "DISPOSITIVO",
            "byte_start": s["utf8_byte_start"],
            "byte_end": s["utf8_byte_end"],
            "classified_as": "NORMATIVE_CANDIDATE",
            "normalized_ref": "",
            "reason_if_excluded": "",
            "reviewer": "",
            "review_status": "PENDING",
        })
    write_csv(root / "dados" / act["act_id"] / "derivado" / "coverage_ledger.csv", header, rows)


def _build_evidence_atoms(root: Path, act: dict, report: dict, segs: list[dict]) -> None:
    """Um evidence atom por dispositivo + UM para o preambulo/considerandos.

    O preambulo e classificado como CONTEXT no ledger (nao e disposicao
    autonoma), mas contem as REMISSOES a outras normas (CONSIDERANDO ...).
    Sem um evidence atom para ele, essas remissoes ficam sem lastro.

    Os OFFSETS vao em sidecar (`evidence_offsets.jsonl`), nunca dentro do
    evidence atom: o contrato `evidence_atom_candidate.schema.json` tem
    `additionalProperties: false` e nao admite campos extras. O contrato nao
    se relaxa para acomodar dado do produtor.
    """
    rows = []
    offsets = []
    dvid = act.get("document_version_id", f"DOC-{act['act_id']}")
    run_id = f"RUN-{act['act_id']}"
    access = act.get("text_access_class", "APPROVED_INTERNAL")
    prefix = report.get("unclassified_bytes", 0) or 0
    if prefix > 0:
        txt = (root / "dados" / act["act_id"] / "derivado" / "texto.txt").read_bytes()
        rows.append({
            "evidence_atom_id": f"EV-{dvid}-PREAMBULO",
            "document_version_id": dvid,
            "locator": "PREÂMBULO/CONSIDERANDOS",
            "fragment_sha256": sha256_bytes(txt[:prefix]),
            "extraction_run_id": run_id,
            "rights_id": f"RTS-{act['source_id']}",
            "text_access_class": access,
            "verified_against_primary": False,
            "clinical_release_allowed": False,
        })
        offsets.append({
            "evidence_atom_id": f"EV-{dvid}-PREAMBULO",
            "utf8_byte_start": 0,
            "utf8_byte_end": prefix,
        })
    for s in segs:
        ev_id = f"EV-{dvid}-{s['fragment_sha256'][:16]}"
        rows.append({
            "evidence_atom_id": ev_id,
            "document_version_id": dvid,
            "locator": s["locator_candidate"],
            "fragment_sha256": s["fragment_sha256"],
            "extraction_run_id": run_id,
            "rights_id": f"RTS-{act['source_id']}",
            "text_access_class": access,
            "verified_against_primary": False,
            "clinical_release_allowed": False,
        })
        offsets.append({
            "evidence_atom_id": ev_id,
            "utf8_byte_start": s["utf8_byte_start"],
            "utf8_byte_end": s["utf8_byte_end"],
        })
    write_jsonl(root / "dados" / act["act_id"] / "atoms" / "evidence_atoms.jsonl", rows)
    write_jsonl(root / "dados" / act["act_id"] / "atoms" / "evidence_offsets.jsonl", offsets)


# --------------------------------------------------------------------------- #
# 4. plano de atomos (etapas 10 a 13)
# --------------------------------------------------------------------------- #
def cmd_plan(args: argparse.Namespace) -> int:
    """Liga o plano declarativo aos fragmentos REAIS de evidencia.

    Cada atomo do plano precisa casar com um evidence_atom existente.
    Locator inexistente ou hash divergente => o atomo nao entra (HOLD_BINDING).
    """
    root = Path(args.root).resolve()
    plans_dir = root / "planos"
    total_norm = total_claim = total_rel = 0
    for plan_path in sorted(plans_dir.glob("*.json")):
        plan = read_json(plan_path)
        act_id = plan["act_id"]
        atoms_dir = root / "dados" / act_id / "atoms"
        ev_path = atoms_dir / "evidence_atoms.jsonl"
        if not ev_path.exists():
            log(f"  [HOLD] {act_id}: sem evidence_atoms para ligar")
            continue
        evs = [json.loads(x) for x in ev_path.read_text(encoding="utf-8").splitlines() if x.strip()]
        by_loc = {e["locator"]: e for e in evs}
        by_sha = {e["fragment_sha256"]: e for e in evs}

        norm_atoms: list[dict] = []
        claim_atoms: list[dict] = []
        binds: list[tuple[str, str, str]] = []  # (tipo, id, evidencia ligada)
        rejected: list[str] = []

        for na in plan.get("norm_atoms", []):
            ev = _resolve_evidence(na, by_loc, by_sha)
            if ev is None:
                rejected.append(f"norm_atom {na['norm_atom_id']}: evidencia nao localizada")
                continue
            norm_atoms.append({
                "norm_atom_id": na["norm_atom_id"],
                "evidence_atom_ids": [ev["evidence_atom_id"]],
                "subject": na["subject"],
                "action": na["action"],
                "object": na["object"],
                "modality": na.get("modality", "UNKNOWN_REVIEW_REQUIRED"),
                "condition": na.get("condition"),
                "exception": na.get("exception"),
                "deadline": na.get("deadline"),
                "validity_from": na.get("validity_from"),
                "validity_to": na.get("validity_to"),
                "status": "CANDIDATE",
                "normative_reviewer_receipt_id": None,
                "clinical_release_allowed": False,
            })
            binds.append(("norm_atom", na["norm_atom_id"], ev["evidence_atom_id"]))

        for ca in plan.get("clinical_claims", []):
            ev = _resolve_evidence(ca, by_loc, by_sha)
            if ev is None:
                rejected.append(f"claim {ca['claim_id']}: evidencia nao localizada")
                continue
            claim_atoms.append({
                "claim_id": ca["claim_id"],
                "source_evidence_atom_ids": [ev["evidence_atom_id"]],
                "assertion_paraphrase": ca["assertion_paraphrase"],
                "population": ca.get("population", ""),
                "setting": ca.get("setting", ""),
                "scope": ca.get("scope", ""),
                "exceptions": ca.get("exceptions", []),
                "negations": ca.get("negations", []),
                "status": "CANDIDATE",
                "clinical_reviewer_receipt_id": None,
                "rights_id": f"RTS-{plan.get('source_id', 'BR-COFEN')}",
                "clinical_release_allowed": False,
            })
            binds.append(("clinical_claim", ca["claim_id"], ev["evidence_atom_id"]))

        rels: list[dict] = []
        for rel in plan.get("relations", []):
            ev = _resolve_evidence(rel, by_loc, by_sha)
            rels.append({
                "relation_id": rel["relation_id"],
                "subject_id": rel["subject_id"],
                "predicate": rel["predicate"],
                "object_id": rel["object_id"],
                "evidence_atom_ids": [ev["evidence_atom_id"]] if ev else [],
                "scope": rel.get("scope"),
                "relation_status": "CANDIDATE",
                "target_verified": False,
                "clinical_release_allowed": False,
            })
            if ev is None:
                rejected.append(f"relation {rel['relation_id']}: evidencia nao localizada")

        write_jsonl(atoms_dir / "norm_atoms_candidates.jsonl", norm_atoms)
        write_jsonl(atoms_dir / "clinical_claims_candidates.jsonl", claim_atoms)
        write_jsonl(atoms_dir / "relations_candidates.jsonl", rels)
        write_jsonl(atoms_dir / "evidence_bindings.jsonl", [
            {"kind": k, "id": i, "evidence_atom_id": e} for k, i, e in binds
        ])

        _write_conflicts(root, act_id, plan)
        _write_change_impact(root, act_id, plan)
        _write_mentions(root, act_id, plan)

        total_norm += len(norm_atoms)
        total_claim += len(claim_atoms)
        total_rel += len(rels)
        log(f"  {act_id}: norm={len(norm_atoms)} claims={len(claim_atoms)} "
            f"rels={len(rels)} rejeitados={len(rejected)}")
        for r in rejected:
            log(f"     [HOLD_BINDING] {r}")
    log(f"planos: {total_norm} norm atoms, {total_claim} claims, {total_rel} relations")
    return 0


def _resolve_evidence(spec: dict, by_loc: dict, by_sha: dict) -> dict | None:
    if spec.get("evidence_atom_id"):
        for e in by_sha.values():
            if e["evidence_atom_id"] == spec["evidence_atom_id"]:
                return e
    if spec.get("locator"):
        ev = by_loc.get(spec["locator"])
        if ev is None:
            return None
        if spec.get("fragment_sha256") and ev["fragment_sha256"] != spec["fragment_sha256"]:
            return None
        return ev
    if spec.get("fragment_sha256"):
        return by_sha.get(spec["fragment_sha256"])
    return None


def _write_conflicts(root: Path, act_id: str, plan: dict) -> None:
    header = ["conflict_id", "type", "severity", "act_id", "description", "evidence_ref",
              "gate", "status", "owner", "due_date", "resolution_receipt_id"]
    rows = []
    for c in plan.get("conflicts", []):
        rows.append({
            "conflict_id": c.get("conflict_id", f"CFL-{act_id}-{len(rows)+1}"),
            "type": c.get("type", "SEMANTIC"),
            "severity": c.get("severity", "MEDIUM"),
            "act_id": act_id,
            "description": c.get("description", ""),
            "evidence_ref": c.get("evidence_ref", ""),
            "gate": c.get("gate", "CE-G05"),
            "status": "HOLD_CONFLICT",
            "owner": c.get("owner", "NormativeHistorian"),
            "due_date": "",
            "resolution_receipt_id": "",
        })
    write_csv(root / "dados" / act_id / "atoms" / "conflicts.csv", header, rows)


def _write_change_impact(root: Path, act_id: str, plan: dict) -> None:
    header = ["event_id", "event_type", "old_source_version_id", "new_source_version_id",
              "changed_locators", "affected_claim_ids", "affected_content_ids",
              "affected_tools", "review_required", "release_hold", "rollback_ref"]
    rows = []
    for ev in plan.get("change_events", []):
        rows.append({
            "event_id": ev.get("event_id", f"IMP-{act_id}-{len(rows)+1}"),
            "event_type": ev.get("event_type", "AMENDS"),
            "old_source_version_id": ev.get("old_source_version_id", ""),
            "new_source_version_id": ev.get("new_source_version_id", ""),
            "changed_locators": ev.get("changed_locators", ""),
            "affected_claim_ids": ev.get("affected_claim_ids", ""),
            "affected_content_ids": ev.get("affected_content_ids", ""),
            "affected_tools": ev.get("affected_tools", ""),
            "review_required": "true",
            "release_hold": "true",
            "rollback_ref": "",
        })
    write_csv(root / "dados" / act_id / "atoms" / "change_impact.csv", header, rows)


# --------------------------------------------------------------------------- #
# 5. registros (etapas 01-02, 04)
# --------------------------------------------------------------------------- #
def cmd_register(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    fontes = read_json(Path(args.fontes))
    acts = fontes.get("acts", [])

    src_rows, rights_rows, doc_rows, run_rows = [], [], [], []
    for act in acts:
        act_id = act["act_id"]
        acq = _maybe(root / "dados" / act_id / "acquisition.json")
        ext = _maybe(root / "dados" / act_id / "extraction.json")
        src_rows.append({
            "source_id": act["source_id"],
            "authority": act.get("authority", ""),
            "jurisdiction": act.get("jurisdiction", "BR"),
            "source_kind": act.get("source_kind", ""),
            "act_id": act_id,
            "title": act.get("title", ""),
            "official_primary_url": act["official_primary_url"],
            "secondary_url": act.get("secondary_url", ""),
            "source_status": act.get("source_status", "LOCATED_PRIMARY"),
            "version_status": act.get("version_status", "UNDECLARED_PENDING_REVIEW"),
            "raw_sha256": (acq or {}).get("raw_sha256", ""),
            "retrieved_at_utc": (acq or {}).get("acquired_at_utc", ""),
            "rights_ref": f"RTS-{act['source_id']}",
            "owner": act.get("owner", "SourceVerifier"),
            "status": act.get("status", "REGISTERED"),
            "finding_ids": act.get("finding_ids", ""),
        })
        for op, st in (act.get("rights_by_operation") or {}).items():
            rights_rows.append({
                "rights_id": f"RTS-{act['source_id']}-{op.upper()}",
                "source_id": act["source_id"],
                "document_version_id": act.get("document_version_id", f"DOC-{act_id}"),
                "operation": op,
                "status": st,
                "rightsholder": act.get("rightsholder", "Uniao (Cofen/Senado) - ato normativo oficial"),
                "license_name": act.get("license_name", BASE_DIREITOS),
                "license_url": act.get("license_url", "https://www.planalto.gov.br/ccivil_03/leis/l9610.htm"),
                "proof_id": act.get("rights_proof_id", ""),
                "proof_sha256": "",
                "valid_from": act.get("act_date", ""),
                "valid_until": "",
                "reviewer_receipt_id": "",
                "notes": act.get("rights_notes", "revisao juridica humana pendente"),
            })
        doc_rows.append({
            "document_version_id": act.get("document_version_id", f"DOC-{act_id}"),
            "source_id": act["source_id"],
            "act_id": act_id,
            "publication_date": act.get("publication_date", act.get("published", "")),
            "effective_date": act.get("effective_date", ""),
            "valid_from": act.get("valid_from", ""),
            "valid_to": act.get("valid_to", ""),
            "version_label": act.get("version_label", "consolidada_na_publicacao"),
            "amended_by_ids": act.get("amended_by_ids", ""),
            "revoked_by_ids": act.get("revoked_by_ids", ""),
            "original_uri": act["official_primary_url"],
            "raw_sha256": (acq or {}).get("raw_sha256", ""),
            "derived_text_sha256": (ext or {}).get("derived_text_sha256", ""),
            "storage_access_class": act.get("storage_access_class", "PRIVATE_RESEARCH"),
            "extraction_run_id": (ext or {}).get("extraction_run_id", ""),
            "status": act.get("version_status", "PENDING_NORMATIVE_REVIEW"),
        })
        if ext:
            run_rows.append({
                "run_id": ext["extraction_run_id"],
                "wo_id": act.get("wo_id", "WO-PILOT-001"),
                "source_id": act["source_id"],
                "document_version_id": act.get("document_version_id", f"DOC-{act_id}"),
                "actor": "cko_pilot.py (agent local)",
                "tool": ext["method"],
                "tool_version": ext["tool_version"],
                "started_at_utc": ext["extracted_at_utc"],
                "finished_at_utc": ext["extracted_at_utc"],
                "raw_sha256": ext["raw_sha256"],
                "parsed_sha256": ext["derived_text_sha256"],
                "parser_config_sha256": "",
                "attempt_number": 1,
                "status": "COMPLETED_CANDIDATE",
                "error_code": "",
                "evidence_ref": str(root / "dados" / act_id / "extraction.json"),
            })

    reg = root / "registros"
    base = reg / "_cabecalhos.csv"
    if base.exists():
        for row in base.read_text(encoding="utf-8").splitlines():
            pass
    write_csv(reg / "00_source_registry.csv",
              ["source_id", "authority", "jurisdiction", "source_kind", "act_id", "title",
               "official_primary_url", "secondary_url", "source_status", "version_status",
               "raw_sha256", "retrieved_at_utc", "rights_ref", "owner", "status", "finding_ids"],
              src_rows)
    write_csv(reg / "01_rights_by_operation.csv",
              ["rights_id", "source_id", "document_version_id", "operation", "status",
               "rightsholder", "license_name", "license_url", "proof_id", "proof_sha256",
               "valid_from", "valid_until", "reviewer_receipt_id", "notes"],
              rights_rows)
    write_csv(reg / "02_document_versions.csv",
              ["document_version_id", "source_id", "act_id", "publication_date", "effective_date",
               "valid_from", "valid_to", "version_label", "amended_by_ids", "revoked_by_ids",
               "original_uri", "raw_sha256", "derived_text_sha256", "storage_access_class",
               "extraction_run_id", "status"],
              doc_rows)
    write_csv(reg / "03_extraction_runs.csv",
              ["run_id", "wo_id", "source_id", "document_version_id", "actor", "tool",
               "tool_version", "started_at_utc", "finished_at_utc", "raw_sha256",
               "parsed_sha256", "parser_config_sha256", "attempt_number", "status",
               "error_code", "evidence_ref"],
              run_rows)
    log(f"registros: {len(src_rows)} fontes, {len(rights_rows)} operacoes de direito, "
        f"{len(doc_rows)} versoes, {len(run_rows)} execucoes de extracao")
    _register_rest(root, acts)
    return 0


def _register_rest(root: Path, acts: list[dict]) -> None:
    """Registros 04 a 17, derivados dos artefatos ja produzidos (nada digitado a mao)."""
    reg = root / "registros"
    act_ids = [a["act_id"] for a in acts]

    # 04 cobertura
    cov: list[dict] = []
    # 05 evidencias
    ev_rows: list[dict] = []
    # 06 norm atoms
    na_rows: list[dict] = []
    # 07 claims
    cl_rows: list[dict] = []
    # 08 knowledge and reuse
    ka_rows: list[dict] = []
    # 09 content assets
    ca_rows: list[dict] = []
    # 10 relacoes
    rel_rows: list[dict] = []
    # 11 findings e conflitos
    fd_rows: list[dict] = []
    # 15 change impact
    imp_rows: list[dict] = []

    for act_id in act_ids:
        d = root / "dados" / act_id
        cov += _read_csv_rows(d / "derivado" / "coverage_ledger.csv")
        for ev in _read_jsonl(d / "atoms" / "evidence_atoms.jsonl"):
            ev_rows.append({
                "evidence_atom_id": ev["evidence_atom_id"],
                "document_version_id": ev["document_version_id"],
                "locator": ev["locator"],
                "fragment_sha256": ev["fragment_sha256"],
                "text_access_policy": ev["text_access_class"],
                "language": "pt-BR",
                "extraction_run_id": ev["extraction_run_id"],
                "context": act_id,
                "source_status": "LOCATED_PRIMARY",
                "verification_status": "DECLARED_NOT_VERIFIED",
            })
        for na in _read_jsonl(d / "atoms" / "norm_atoms_candidates.jsonl"):
            na_rows.append({
                "norm_atom_id": na["norm_atom_id"],
                "evidence_atom_id": ";".join(na["evidence_atom_ids"]),
                "document_version_id": f"DOC-{act_id}",
                "subject": na["subject"],
                "action": na["action"],
                "object": na["object"],
                "modality": na["modality"],
                "condition": na["condition"] or "",
                "exception": na["exception"] or "",
                "deadline": na["deadline"] or "",
                "jurisdiction": "BR",
                "valid_from": na["validity_from"] or "",
                "valid_to": na["validity_to"] or "",
                "source_language": "pt-BR",
                "status": "CANDIDATE",
                "review_receipt_id": "",
            })
        for cl in _read_jsonl(d / "atoms" / "clinical_claims_candidates.jsonl"):
            cl_rows.append({
                "claim_id": cl["claim_id"],
                "statement_summary": cl["assertion_paraphrase"],
                "evidence_atom_ids": ";".join(cl["source_evidence_atom_ids"]),
                "source_document_version_ids": f"DOC-{act_id}",
                "population": cl["population"],
                "setting": cl["setting"],
                "professional_scope": cl["scope"],
                "negation": ";".join(cl.get("negations", [])),
                "exceptions": ";".join(cl.get("exceptions", [])),
                "applicability": "BR - sistema Cofen/Conselhos Regionais",
                "uncertainty": "modalidade e escopo pendientes de revisao normativa humana",
                "claim_version": "0.1.0-candidate",
                "review_status": "CANDIDATE",
                "clinical_reviewer_receipt_id": "",
                "rights_id": cl["rights_id"],
            })
        for rel in _read_jsonl(d / "atoms" / "relations_candidates.jsonl"):
            rel_rows.append({
                "relation_id": rel["relation_id"],
                "subject_id": rel["subject_id"],
                "predicate": rel["predicate"],
                "object_id": rel["object_id"],
                "subject_version": f"DOC-{rel['subject_id']}",
                "object_version": f"DOC-{rel['object_id']}",
                "evidence_atom_ids": ";".join(rel["evidence_atom_ids"]),
                "confidence": "CANDIDATE",
                "justification": rel.get("scope") or "",
                "status": "CANDIDATE",
                "target_exists": "true" if _act_registered(root, rel["object_id"]) else "false",
                "review_receipt_id": "",
            })
        for c in _read_csv_rows(d / "atoms" / "conflicts.csv"):
            fd_rows.append({
                "finding_id": c["conflict_id"],
                "type": c["type"],
                "severity": c["severity"],
                "source_id": f"SRC-BR-COFEN",
                "document_version_id": f"DOC-{act_id}",
                "affected_ids": act_id,
                "description": c["description"],
                "evidence_ref": c["evidence_ref"],
                "gate": c["gate"],
                "status": c["status"],
                "owner": c["owner"],
                "due_date": "",
                "resolution_receipt_id": "",
            })
        imp_rows += _read_csv_rows(d / "atoms" / "change_impact.csv")

    # 08 knowledge and reuse: 1 knowledge atom por claim com vinculo ao conteudo
    for cl in cl_rows:
        ka_rows.append({
            "knowledge_atom_id": f"KA-{cl['claim_id'].replace('CLM-', '')}",
            "claim_ids": cl["claim_id"],
            "norm_atom_ids": "",
            "content_id": "CM-PILOT-001",
            "topic_id": "TPC-PROCESSO-DE-ENFERMAGEM",
            "specialty_ids": "enfermagem-geral",
            "audience": "profissionais de enfermagem",
            "context_constraints": "BR; vigente na data da revisao humana; sem posologia",
            "relation_type": "DERIVES_FROM",
            "source_sha256": "",
            "review_status": "CANDIDATE",
            "valid_from": "",
            "valid_to": "",
        })
    # 09 content assets
    content_path = root / "conteudo" / "content_master.json"
    if content_path.exists():
        cm = read_json(content_path)
        for res in cm.get("resources", []):
            ca_rows.append({
                "content_id": cm["content_id"],
                "resource_id": res["resource_id"],
                "resource_type": res["resource_type"],
                "topic_id": cm["topic_id"],
                "specialty_ids": ";".join(cm.get("specialty_ids", [])),
                "language": "pt-BR",
                "content_version": cm["version"],
                "content_sha256": res.get("content_sha256", ""),
                "claim_ids": ";".join(cm.get("claim_ids", [])),
                "editorial_status": cm["status"],
                "clinical_status": "PENDING_HUMAN_REVIEW",
                "rights_status": "PENDING",
                "accessibility_status": "PENDING",
                "i18n_status": "NOT_STARTED",
                "publication_status": "HOLD",
                "publication_url": "",
            })

    # 12 work orders
    wo_rows = [{
        "wo_id": "WO-PILOT-001",
        "find_ids": ";".join(sorted({r["finding_id"] for r in fd_rows})),
        "policy_ids": "CKO-POL-UT-001",
        "validator_ids": "cko_gates.G01..G12",
        "scope": "piloto de 16 atos: 10 COFEN, 2 COREN-SP, 4 atos federais via API do Senado",
        "source_ids": "SRC-BR-COFEN;SRC-BR-CORENSP;SRC-BR-SENADO",
        "document_version_ids": ";".join(f"DOC-{a}" for a in act_ids),
        "repo": "local://cko-pilot-cofen-cor",
        "branch": "N/A (execucao offline em workspace)",
        "head_sha": "",
        "wo_blob_sha": "",
        "allowed_operations": "fetch;extract;segment;plan;register;validate;gate;content_draft",
        "executor": "cko_pilot.py (agente local) + redacao humana dos planos",
        "independent_reviewer": "PENDENTE - profissional humano habilitado e juridico",
        "admission_receipt_id": "",
        "state": "EXECUTED_CANDIDATE_ONLY",
        "rollback_ref": "",
    }]
    # 13 revisoes
    rc_rows = [{
        "receipt_id": "",
        "review_domain": "normativa",
        "issuer_authority_id": "",
        "reviewer_credential_ref": "",
        "object_ids": ";".join(act_ids),
        "source_shas": "",
        "commit_sha": "",
        "wo_blob_sha": "",
        "rights_operations": "",
        "issued_at": "",
        "expires_at": "",
        "revocation_id": "",
        "signature_verifier": "",
        "result": "PENDING",
    }]
    # 14 execucoes de gate (preenchido depois pelo passo gate)
    gate_path = root / "gates" / "test_report.json"
    gate_rows = []
    if gate_path.exists():
        g = read_json(gate_path)
        for t in g.get("tests", []):
            gate_rows.append({
                "run_id": f"GATE-{g['executed_at_utc']}",
                "gate_id": t["id"],
                "gate_version": "1.0.0",
                "object_scope": "dados/*",
                "source_hash": "",
                "schema_hash": "",
                "validator_hash": "",
                "executed_at": g["executed_at_utc"],
                "exit_code": 0 if t["status"] == "PASS" else 1,
                "status": t["status"],
                "evidence_sha": "",
                "issues": t["detail"],
                "release_allowed": "false",
            })
    # 16 publicacao (vazia: nada publicado)
    pub_rows = [{
        "publication_id": "",
        "resource_id": "",
        "content_version": "",
        "channel": "",
        "site_url": "",
        "commit_sha": "",
        "release_receipt_id": "",
        "security_approval": "",
        "clinical_approval": "",
        "rights_approval": "",
        "rollback_ref": "",
        "published_at": "",
        "status": "NOT_PUBLISHED",
    }]
    # 17 inventario de pacotes
    inv_rows = [{
        "package_key": "cko_pilot_cofen_cor",
        "filename": "cko-pilot-cofen-cor",
        "zip_sha256": "",
        "zip_bytes": "",
        "file_count": "",
        "status": "WORKING_SET - hash do zip preenchido no empacotamento final",
        "reviewed_at": now_utc(),
    }]

    write_csv(reg / "04_coverage_ledger.csv",
              ["document_version_id", "locator", "fragment_type", "byte_start", "byte_end",
               "classified_as", "normalized_ref", "reason_if_excluded", "reviewer", "review_status"],
              cov)
    write_csv(reg / "05_evidence_atoms.csv",
              ["evidence_atom_id", "document_version_id", "locator", "fragment_sha256",
               "text_access_policy", "language", "extraction_run_id", "context",
               "source_status", "verification_status"], ev_rows)
    write_csv(reg / "06_norm_atoms.csv",
              ["norm_atom_id", "evidence_atom_id", "document_version_id", "subject", "action",
               "object", "modality", "condition", "exception", "deadline", "jurisdiction",
               "valid_from", "valid_to", "source_language", "status", "review_receipt_id"],
              na_rows)
    write_csv(reg / "07_clinical_claims.csv",
              ["claim_id", "statement_summary", "evidence_atom_ids", "source_document_version_ids",
               "population", "setting", "professional_scope", "negation", "exceptions",
               "applicability", "uncertainty", "claim_version", "review_status",
               "clinical_reviewer_receipt_id", "rights_id"], cl_rows)
    write_csv(reg / "08_knowledge_and_reuse.csv",
              ["knowledge_atom_id", "claim_ids", "norm_atom_ids", "content_id", "topic_id",
               "specialty_ids", "audience", "context_constraints", "relation_type",
               "source_sha256", "review_status", "valid_from", "valid_to"], ka_rows)
    write_csv(reg / "09_content_assets.csv",
              ["content_id", "resource_id", "resource_type", "topic_id", "specialty_ids",
               "language", "content_version", "content_sha256", "claim_ids", "editorial_status",
               "clinical_status", "rights_status", "accessibility_status", "i18n_status",
               "publication_status", "publication_url"], ca_rows)
    write_csv(reg / "10_relation_candidates.csv",
              ["relation_id", "subject_id", "predicate", "object_id", "subject_version",
               "object_version", "evidence_atom_ids", "confidence", "justification", "status",
               "target_exists", "review_receipt_id"], rel_rows)
    write_csv(reg / "11_findings_and_conflicts.csv",
              ["finding_id", "type", "severity", "source_id", "document_version_id",
               "affected_ids", "description", "evidence_ref", "gate", "status", "owner",
               "due_date", "resolution_receipt_id"], fd_rows)
    write_csv(reg / "12_work_orders.csv",
              ["wo_id", "find_ids", "policy_ids", "validator_ids", "scope", "source_ids",
               "document_version_ids", "repo", "branch", "head_sha", "wo_blob_sha",
               "allowed_operations", "executor", "independent_reviewer", "admission_receipt_id",
               "state", "rollback_ref"], wo_rows)
    write_csv(reg / "13_reviews_and_approvals.csv",
              ["receipt_id", "review_domain", "issuer_authority_id", "reviewer_credential_ref",
               "object_ids", "source_shas", "commit_sha", "wo_blob_sha", "rights_operations",
               "issued_at", "expires_at", "revocation_id", "signature_verifier", "result"], rc_rows)
    write_csv(reg / "14_gate_executions.csv",
              ["run_id", "gate_id", "gate_version", "object_scope", "source_hash",
               "schema_hash", "validator_hash", "executed_at", "exit_code", "status",
               "evidence_sha", "issues", "release_allowed"], gate_rows)
    write_csv(reg / "15_change_impact.csv",
              ["event_id", "event_type", "old_source_version_id", "new_source_version_id",
               "changed_locators", "affected_claim_ids", "affected_content_ids",
               "affected_tools", "review_required", "release_hold", "rollback_ref"], imp_rows)
    write_csv(reg / "16_publication_registry.csv",
              ["publication_id", "resource_id", "content_version", "channel", "site_url",
               "commit_sha", "release_receipt_id", "security_approval", "clinical_approval",
               "rights_approval", "rollback_ref", "published_at", "status"], pub_rows)
    write_csv(reg / "17_inventario_pacotes.csv",
              ["package_key", "filename", "zip_sha256", "zip_bytes", "file_count", "status",
               "reviewed_at"], inv_rows)


def _act_registered(root: Path, act_id: str) -> bool:
    return (root / "dados" / act_id).exists()


def _read_csv_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _maybe(path: Path) -> dict | None:
    if path.exists():
        try:
            return read_json(path)
        except Exception:  # noqa: BLE001
            return None
    return None


# --------------------------------------------------------------------------- #
# 6. validacao (schema + integridade referencial)
# --------------------------------------------------------------------------- #
def cmd_validate(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    validator_factory = None
    try:
        from jsonschema import Draft202012Validator
        validator_factory = Draft202012Validator
        backend = "jsonschema (Draft202012Validator)"
    except ImportError:
        sys.path.insert(0, str(root / "automatizacao"))
        from cko_schema import validate as _v, unsupported_keywords
        backend = "cko_schema (subconjunto Draft 2020-12, offline)"

        def validator_factory(schema: dict):  # type: ignore[misc]
            unsupported = unsupported_keywords(schema)
            if unsupported:
                raise ValueError(
                    f"schema usa palavras-chave nao suportadas: {unsupported}")

            class _Local:
                def __init__(self, sch: dict) -> None:
                    self.schema = sch

                def iter_errors(self, instance: Any):
                    for msg in _v(instance, self.schema):
                        yield type("E", (), {"message": msg})()

            return _Local(schema)

    contratos = root / "modelos" / "contratos"
    validators = {
        p.stem.replace(".schema", ""): validator_factory(read_json(p))
        for p in sorted(contratos.glob("*.schema.json"))
    }
    issues: list[str] = []
    required = ("evidence_atom_candidate", "norm_atom_candidate",
                "clinical_claim_candidate", "relation_candidate")
    for name in required:
        if name not in validators:
            issues.append(f"CONTRACT_MISSING: {name}")
    checked = 0
    expected = 0
    for acts_dir in sorted((root / "dados").glob("*")):
        atoms = acts_dir / "atoms"
        if not atoms.exists():
            continue
        for kind, schema_name in (("evidence_atoms.jsonl", "evidence_atom_candidate"),
                                  ("norm_atoms_candidates.jsonl", "norm_atom_candidate"),
                                  ("clinical_claims_candidates.jsonl", "clinical_claim_candidate"),
                                  ("relations_candidates.jsonl", "relation_candidate")):
            path = atoms / kind
            if not path.exists():
                continue
            val = validators.get(schema_name)
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                expected += 1
                if val is None:
                    issues.append(f"{acts_dir.name}/{kind}:{i} CONTRACT_MISSING: {schema_name}")
                    continue
                obj = json.loads(line)
                checked += 1
                for err in val.iter_errors(obj):
                    issues.append(f"{acts_dir.name}/{kind}:{i} [{err.message}]")
    # integridade referencial: toda referencia tem alvo real
    ev_ids: set[str] = set()
    for acts_dir in sorted((root / "dados").glob("*")):
        p = acts_dir / "atoms" / "evidence_atoms.jsonl"
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    ev_ids.add(json.loads(line)["evidence_atom_id"])
    for acts_dir in sorted((root / "dados").glob("*")):
        atoms = acts_dir / "atoms"
        for name, key in (("norm_atoms_candidates.jsonl", "evidence_atom_ids"),
                          ("clinical_claims_candidates.jsonl", "source_evidence_atom_ids"),
                          ("relations_candidates.jsonl", "evidence_atom_ids")):
            p = atoms / name
            if not p.exists():
                continue
            for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                obj = json.loads(line)
                for ref in obj.get(key, []):
                    if ref not in ev_ids:
                        issues.append(f"{acts_dir.name}/{name}:{i} referencia orfa -> {ref}")
    if checked != expected:
        issues.append(f"CONTRACT_COVERAGE: expected={expected} validated={checked}")
    report = {
        "schema": "CKO-PILOT-VALIDATION-v1.0.0",
        "objects_expected": expected,
        "checked_at_utc": now_utc(),
        "validator_backend": backend,
        "objects_validated": checked,
        "schema_contracts": sorted(validators),
        "issue_count": len(issues),
        "issues": issues[:200],
        "status": "PASS" if not issues else "FAIL",
        "note": "PASS de schema NAO equivale a aprovacao normativa ou clinica",
        "publication_allowed": False,
    }
    write_json(root / "gates" / "validation_report.json", report)
    log(f"validate: {checked} objetos, {len(issues)} problemas -> {report['status']}")
    for i in issues[:20]:
        log(f"    - {i}")
    return 0 if not issues else 1


# --------------------------------------------------------------------------- #
# 7. gate adversarial
# --------------------------------------------------------------------------- #
def cmd_gate(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    sys.path.insert(0, str(root / "automatizacao"))
    from cko_gates import run_gates  # noqa: PLC0415
    report = run_gates(root)
    write_json(root / "gates" / "test_report.json", report)
    log(f"gate: {report['passed']}/{report['total']} "
        f"({report['failed']} falha(s)) -> {report['status']}")
    for t in report["tests"]:
        if t["status"] != "PASS":
            log(f"    [FALHA] {t['id']}: {t['detail']}")
    return 0 if report["status"] == "PASS" else 1


def _write_mentions(root: Path, act_id: str, plan: dict) -> None:
    """Mencoes a atos que NAO estao no SourceRegistry deste piloto.

    Nao sao arestas: sao mencoes. Registrar o nome sem criar relacao evita
    o defeito F-ATOMIC-004 (rotulo de relacionamento tratado como aresta).
    """
    header = ["mentioned_act", "mentioned_label", "cited_in", "target_registered",
               "note"]
    rows = []
    for m in plan.get("mentions", []):
        rows.append({
            "mentioned_act": m.get("mentioned_act", ""),
            "mentioned_label": m.get("mentioned_label", ""),
            "cited_in": m.get("cited_in", ""),
            "target_registered": "false",
            "note": m.get("note", "mencao textual; ato fora do escopo deste piloto"),
        })
    write_csv(root / "dados" / act_id / "atoms" / "references_mentioned.csv", header, rows)


def cmd_run(args: argparse.Namespace) -> int:
    steps = [
        ("fetch", cmd_fetch), ("extract", cmd_extract), ("segment", cmd_segment),
        ("plan", cmd_plan), ("register", cmd_register),
        ("validate", cmd_validate), ("gate", cmd_gate),
    ]
    for name, fn in steps:
        log(f"=== passo: {name} ===")
        rc = fn(args)
        if rc != 0:
            log(f"passo {name} devolveu rc={rc}; pipeline interrompido em HOLD")
            return rc
    return 0


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Extrator local ponta a ponta para normativos CKO.")
    ap.add_argument("comando",
                    choices=["fetch", "extract", "segment", "plan", "register",
                             "validate", "gate", "run"])
    ap.add_argument("--fontes", default="fontes/fontes.json")
    ap.add_argument("--root", default=".")
    ap.add_argument("--offline", action="store_true",
                    help="nao acessa a rede (fetch falha sem cache)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--retries", type=int, default=2)
    args = ap.parse_args(argv)
    fn = {
        "fetch": cmd_fetch, "extract": cmd_extract, "segment": cmd_segment,
        "plan": cmd_plan, "register": cmd_register, "validate": cmd_validate,
        "gate": cmd_gate, "run": cmd_run,
    }[args.comando]
    return fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
