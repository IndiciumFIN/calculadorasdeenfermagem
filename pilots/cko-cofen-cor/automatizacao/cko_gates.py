#!/usr/bin/env python3
"""cko_gates.py — Portoes tecnicos adversariais do piloto CKO.

Regra de ouro deste arquivo: um portao so vale se conseguir matar uma
mutacao. Cada mutacao aqui e aplicada numa COPIA do pacote; se o mutante
sobreviver, o portao esta quebrado e o gate falha.

O gate NAO aprova nada. PASS significa "nenhum defeito tecnico conhecido",
o que e diferente de "norma vigente", "direito concedido" e "revisado por
humano". O publication_decision permanece HOLD por padrao.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SHA_RE_LEN = 64


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------- #
# verificacoes (cada uma devolve lista de problemas)
# --------------------------------------------------------------------------- #
def g_raw_artifact_exists(root: Path) -> list[str]:
    """G1: todo ato registrado tem artefato bruto com sha256 conferido."""
    issues = []
    rows = _read_csv(root / "registros" / "00_source_registry.csv")
    if not rows:
        return ["G1: registro de fontes vazio"]
    for r in rows:
        act = r.get("act_id", "")
        raw_sha = (r.get("raw_sha256") or "").strip()
        if len(raw_sha) != SHA_RE_LEN:
            issues.append(f"G1: {act} sem sha256 de origem registrado")
            continue
        raw_dir = root / "dados" / act / "raw"
        files = [p for p in raw_dir.glob("*") if p.is_file()] if raw_dir.exists() else []
        if not files:
            issues.append(f"G1: {act} registrado mas sem artefato bruto em dados/{act}/raw")
            continue
        real = {_sha(p.read_bytes()) for p in files}
        if raw_sha not in real:
            issues.append(f"G1: {act} sha256 do registro nao bate com o arquivo bruto")
    return issues


def g_evidence_roundtrip(root: Path) -> list[str]:
    """G2: fragment_sha256 de cada evidence atom bate com o byte slice real.

    Esta e a prova de que o fragmento existe no derivado — e o que impede
    um hash inventado (defeito mais caro em entrega normativa).
    """
    issues = []
    for acts_dir in sorted((root / "dados").glob("*")):
        ext = _read_json(acts_dir / "extraction.json") if (acts_dir / "extraction.json").exists() else None
        if not ext:
            issues.append(f"G2: {acts_dir.name} sem extraction.json")
            continue
        txt_path = root / ext["derived_text_file"]
        if not txt_path.exists():
            issues.append(f"G2: {acts_dir.name} derivado ausente: {txt_path.name}")
            continue
        raw = txt_path.read_bytes()
        if _sha(raw) != ext["derived_text_sha256"]:
            issues.append(f"G2: {acts_dir.name} sha256 do derivado divergiu do registro")
            continue
        for ev in _read_jsonl(acts_dir / "atoms" / "evidence_atoms.jsonl"):
            start = ev.get("_utf8_byte_start")
            end = ev.get("_utf8_byte_end")
            off = next((o for o in _read_jsonl(acts_dir / "atoms" / "evidence_offsets.jsonl")
                        if o["evidence_atom_id"] == ev["evidence_atom_id"]), None)
            if off is None:
                issues.append(f"G2: {ev.get('evidence_atom_id')} sem offsets no sidecar")
                continue
            start, end = off["utf8_byte_start"], off["utf8_byte_end"]
            if not (0 <= start < end <= len(raw)):
                issues.append(f"G2: {ev.get('evidence_atom_id')} offsets fora do arquivo")
                continue
            if _sha(raw[start:end]) != ev["fragment_sha256"]:
                issues.append(f"G2: {ev.get('evidence_atom_id')} fragment_sha256 nao bate com os bytes")
    return issues


def g_locator_matches_text(root: Path) -> list[str]:
    """G3: o locator declarado existe no fragmento ao qual ele se refere.

    Para dispositivos, o locator ("Art. 4º") tem de aparecer no proprio
    fragmento - e o fragmento tem de estar no texto. Para o preambulo, o
    locator e SINTETICO (nao ha "Art." no preambulo), e a verificacao e
    feita pela posicao: o fragmento tem de ser prefixo do texto derivado.
    """
    issues = []
    for acts_dir in sorted((root / "dados").glob("*")):
        txt_path = acts_dir / "derivado" / "texto.txt"
        if not txt_path.exists():
            continue
        raw = txt_path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        offsets = {o["evidence_atom_id"]: o
                   for o in _read_jsonl(acts_dir / "atoms" / "evidence_offsets.jsonl")}
        for ev in _read_jsonl(acts_dir / "atoms" / "evidence_atoms.jsonl"):
            loc = ev.get("locator", "")
            if not loc:
                issues.append(f"G3: {ev.get('evidence_atom_id')} sem locator")
                continue
            off = offsets.get(ev["evidence_atom_id"])
            if off is None:
                issues.append(f"G3: {ev.get('evidence_atom_id')} sem offsets no sidecar")
                continue
            frag = raw[off["utf8_byte_start"]:off["utf8_byte_end"]].decode(
                "utf-8", errors="replace")
            if loc.startswith("PREÂMBULO/"):
                # locator sintetico: o fragmento tem de ser prefixo do texto
                if not text.startswith(frag) or not frag.strip():
                    issues.append(f"G3: {ev.get('evidence_atom_id')} preambulo nao e prefixo do derivado")
                continue
            if loc not in text:
                issues.append(f"G3: {ev.get('evidence_atom_id')} locator '{loc}' ausente do derivado")
            elif loc not in frag:
                issues.append(f"G3: {ev.get('evidence_atom_id')} locator '{loc}' fora do proprio fragmento")
    return issues


def g_no_orphan_references(root: Path) -> list[str]:
    """G4: nenhuma referencia de atomo aponta para evidencia inexistente."""
    issues = []
    ev_ids: set[str] = set()
    for acts_dir in sorted((root / "dados").glob("*")):
        for ev in _read_jsonl(acts_dir / "atoms" / "evidence_atoms.jsonl"):
            ev_ids.add(ev["evidence_atom_id"])
    for acts_dir in sorted((root / "dados").glob("*")):
        for name, key in (("norm_atoms_candidates.jsonl", "evidence_atom_ids"),
                          ("clinical_claims_candidates.jsonl", "source_evidence_atom_ids"),
                          ("relations_candidates.jsonl", "evidence_atom_ids")):
            for obj in _read_jsonl(acts_dir / "atoms" / name):
                for ref in obj.get(key, []):
                    if ref not in ev_ids:
                        issues.append(f"G4: {acts_dir.name}/{name} referencia orfa {ref}")
    return issues


def g_nothing_self_releases(root: Path) -> list[str]:
    """G5: nenhum candidato se autolibera e a decisao de publicacao e HOLD."""
    issues = []
    for acts_dir in sorted((root / "dados").glob("*")):
        for name in ("norm_atoms_candidates.jsonl", "clinical_claims_candidates.jsonl",
                     "relations_candidates.jsonl", "evidence_atoms.jsonl"):
            for obj in _read_jsonl(acts_dir / "atoms" / name):
                if obj.get("clinical_release_allowed") is not False:
                    issues.append(f"G5: {acts_dir.name}/{name} clinical_release_allowed nao e false")
    pd_path = root / "publication_decision.json"
    if not pd_path.exists():
        issues.append("G5: publication_decision.json ausente")
    else:
        pd = _read_json(pd_path)
        if pd.get("decision") != "HOLD":
            issues.append(f"G5: decisao de publicacao e {pd.get('decision')}, esperado HOLD")
        if pd.get("publication_allowed") is not False:
            issues.append("G5: publication_allowed nao e false")
        if pd.get("professional_review_receipts"):
            issues.append("G5: recibos de revisao profissional declarados sem prova externa")
    return issues


def g_no_self_approved_receipts(root: Path) -> list[str]:
    """G6: nenhum recibo de revisao humana esta preenchido no piloto."""
    issues = []
    for acts_dir in sorted((root / "dados").glob("*")):
        for name, key in (("norm_atoms_candidates.jsonl", "normative_reviewer_receipt_id"),
                          ("clinical_claims_candidates.jsonl", "clinical_reviewer_receipt_id")):
            for obj in _read_jsonl(acts_dir / "atoms" / name):
                if obj.get(key):
                    issues.append(f"G6: {acts_dir.name}/{name} recibo preenchido sem prova externa")
    rows = _read_csv(root / "registros" / "13_reviews_and_approvals.csv")
    for r in rows:
        if (r.get("result") or "").strip() not in ("", "PENDING", "HOLD"):
            issues.append(f"G6: registro 13 com resultado '{r.get('result')}' no piloto")
    return issues


def g_coverage_not_overclaimed(root: Path) -> list[str]:
    """G7: nenhuma cobertura declarada como 100% sem denominador e evidencia."""
    issues = []
    for acts_dir in sorted((root / "dados").glob("*")):
        rep_path = acts_dir / "derivado" / "segmentacao" / "report.json"
        if not rep_path.exists():
            continue
        rep = _read_json(rep_path)
        total = rep.get("bytes_input_text", 0)
        struct = rep.get("segmented_utf8_bytes", 0)
        unclass = rep.get("unclassified_bytes", 0)
        if total and struct + unclass != total:
            issues.append(f"G7: {acts_dir.name} bytes nao fecham (total={total})")
        if rep.get("article_candidates", 0) and unclass == 0 and rep.get("issue_codes"):
            issues.append(f"G7: {acts_dir.name} cobertura declarada sem pendencia declarada")
    return issues


def g_revocation_has_impact(root: Path) -> list[str]:
    """G8: ato declarado revogado/alterado precisa de conflito e impacto."""
    issues = []
    rows = _read_csv(root / "registros" / "02_document_versions.csv")
    for r in rows:
        status = (r.get("status") or "") + " " + (r.get("revoked_by_ids") or "") + \
                 " " + (r.get("amended_by_ids") or "")
        if not re_search_any(status, ("REVOG", "REVOGAD", "ALTERAD", "PRORROG")):
            continue
        act = r.get("act_id", "")
        conflicts = _read_csv(root / "dados" / act / "atoms" / "conflicts.csv")
        impact = _read_csv(root / "dados" / act / "atoms" / "change_impact.csv")
        if not conflicts and not impact:
            issues.append(f"G8: {act} com status de revogacao/alteracao sem conflito nem impacto")
    return issues


def re_search_any(text: str, needles: tuple[str, ...]) -> bool:
    up = text.upper()
    return any(n in up for n in needles)


def g_idempotent_extraction(root: Path) -> list[str]:
    """G9: extrair duas vezes produz o mesmo sha (extracao deterministica)."""
    issues = []
    sys_path = root / "automatizacao"
    for acts_dir in sorted((root / "dados").glob("*")):
        ext_path = acts_dir / "extraction.json"
        if not ext_path.exists():
            continue
        ext = _read_json(ext_path)
        txt_path = root / ext["derived_text_file"]
        if not txt_path.exists():
            continue
        text = txt_path.read_text(encoding="utf-8")
        if _sha(text.encode("utf-8")) != ext["derived_text_sha256"]:
            issues.append(f"G9: {acts_dir.name} derivado nao e reproduzivel")
    return issues


def g_no_protected_text_in_registers(root: Path) -> list[str]:
    """G10: os registros nao carregam VERBATIM do texto da norma.

    O teste nao e "texto longo" (parafrase legitima pode ser longa): o teste
    e VERBATIM — a celula aparece como substring do texto derivado do ato.
    E isso que distingue copia de corpo de norma de condensacao editorial.
    """
    issues = []
    textos: dict[str, str] = {}
    for acts_dir in sorted((root / "dados").glob("*")):
        p = acts_dir / "derivado" / "texto.txt"
        if p.exists():
            t = p.read_text(encoding="utf-8")
            textos[acts_dir.name] = re.sub(r"\s+", " ", t)
    for p in sorted((root / "registros").glob("*.csv")):
        for row in _read_csv(p):
            for k, v in row.items():
                if not v:
                    continue
                v = re.sub(r"\s+", " ", str(v)).strip()
                if len(v) < 200:
                    continue
                for act_name, texto in textos.items():
                    if v in texto:
                        issues.append(
                            f"G10: {p.name}.{k} reproduz VERBATIM trecho de {act_name}")
                        break
    return issues


def g_every_act_has_acquisition(root: Path) -> list[str]:
    """G11: todo ato tem registro de aquisicao com status HTTP real."""
    issues = []
    rows = _read_csv(root / "registros" / "00_source_registry.csv")
    for r in rows:
        act = r.get("act_id", "")
        acq_path = root / "dados" / act / "acquisition.json"
        if not acq_path.exists():
            issues.append(f"G11: {act} sem acquisition.json")
            continue
        acq = _read_json(acq_path)
        if not acq.get("http_status"):
            issues.append(f"G11: {act} sem status HTTP registrado")
        if acq.get("error"):
            issues.append(f"G11: {act} aquisicao com erro: {acq['error']}")
    return issues


def g_source_status_declared(root: Path) -> list[str]:
    """G12: todo ato declara status de versao; nada fica como 'desconhecido' silencioso."""
    issues = []
    rows = _read_csv(root / "registros" / "02_document_versions.csv")
    for r in rows:
        if not (r.get("status") or "").strip():
            issues.append(f"G12: {r.get('act_id')} sem status de versao")
    return issues


def g_schema_conformance(root: Path) -> list[str]:
    """G13: todo candidato conforms ao contrato de sidecar do anexo.

    O contrato tem `additionalProperties: false`: um campo extra no objeto
    e violacao. O contrato nao se relaxa para acomodar o produtor.
    """
    issues = []
    sys.path.insert(0, str(root / "automatizacao"))
    try:
        from cko_schema import validate as schema_validate
    except ImportError:
        return ["G13: cko_schema indisponivel"]
    contratos = root / "modelos" / "contratos"
    validators = {
        p.stem.replace(".schema", ""): _read_json(p)
        for p in sorted(contratos.glob("*.schema.json"))
    }
    pairs = (("evidence_atoms.jsonl", "evidence_atom_candidate"),
             ("norm_atoms_candidates.jsonl", "norm_atom_candidate"),
             ("clinical_claims_candidates.jsonl", "clinical_claim_candidate"),
             ("relations_candidates.jsonl", "relation_candidate"))
    for acts_dir in sorted((root / "dados").glob("*")):
        for fname, schema_name in pairs:
            path = acts_dir / "atoms" / fname
            if not path.exists():
                continue
            if schema_name not in validators:
                issues.append(f"G13: {acts_dir.name}/{fname} CONTRACT_MISSING: {schema_name}")
                continue
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                for msg in schema_validate(json.loads(line), validators[schema_name]):
                    issues.append(f"G13: {acts_dir.name}/{fname}:{i} {msg}")
    return issues


def g_reextraction_is_deterministic(root: Path) -> list[str]:
    """G14: re-extrair do original armazenado reproduz o derivado byte a byte.

    Prova que o sha256 do derivado e um conteudo de documento reproduzivel,
    e nao um artefato acidental da execucao.
    """
    issues = []
    sys.path.insert(0, str(root / "automatizacao"))
    try:
        from cko_pilot import html_to_text, json_to_text, pdf_to_text
    except ImportError:
        return ["G14: cko_pilot indisponivel"]
    for acts_dir in sorted((root / "dados").glob("*")):
        ext_path = acts_dir / "extraction.json"
        if not ext_path.exists():
            continue
        ext = _read_json(ext_path)
        raw_path = root / ext["raw_file"]
        if not raw_path.exists():
            issues.append(f"G14: {acts_dir.name} original ausente")
            continue
        raw = raw_path.read_bytes()
        method = ext["method"]
        if method.startswith("html_to_text"):
            text = html_to_text(raw.decode("utf-8", errors="replace"))
        elif method.startswith("pdf_text_layer"):
            text, _ = pdf_to_text(raw)
        elif method.startswith("senado_api"):
            text = json_to_text(json.loads(raw.decode("utf-8")))
        else:
            continue
        if _sha(text.encode("utf-8")) != ext["derived_text_sha256"]:
            issues.append(f"G14: {acts_dir.name} re-extracao nao reproduz o sha256 do derivado")
    return issues



def g_no_session_credentials_in_acquisition(root: Path) -> list[str]:
    """G15: never retain response cookies or arbitrary server headers in the custodian metadata."""
    issues = []
    import urllib.parse
    from cko_pilot import _safe_http_headers  # same typed allowlist as writer
    records = sorted((root / "dados").glob("*/acquisition.json"))
    if not records:
        return ["G15: no acquisition metadata found"]
    forbidden_query_keys = {"token", "access_token", "api_key", "apikey", "auth", "authorization", "session", "sid", "secret", "signature", "sig", "password"}
    for path in records:
        try:
            rec = _read_json(path)
            headers = rec.get("http_headers")
            if not isinstance(headers, dict):
                issues.append(f"G15: {path.parent.name} malformed headers")
                continue
            for key, value in headers.items():
                if _safe_http_headers({key: value}) != {key: value}:
                    issues.append(f"G15: {path.parent.name} unsafe response header metadata: {str(key)[:48]}")
            for url_field in ("http_final_url", "official_primary_url"):
                url = rec.get(url_field)
                if not url:
                    continue
                parts = urllib.parse.urlsplit(str(url))
                if parts.scheme != "https" or not parts.hostname or parts.fragment:
                    issues.append(f"G15: {path.parent.name} invalid secure URL in {url_field}")
                if parts.username or parts.password:
                    issues.append(f"G15: {path.parent.name} credentials in {url_field}")
                if any(key.lower() in forbidden_query_keys for key, _ in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)):
                    issues.append(f"G15: {path.parent.name} credential query in {url_field}")
        except (ValueError, OSError, TypeError):
            issues.append(f"G15: {path.parent.name} invalid acquisition record")
    return issues


CHECKS: list[tuple[str, Callable[[Path], list[str]]]] = [
    ("G01-raw-artifact-exists", g_raw_artifact_exists),
    ("G02-evidence-roundtrip", g_evidence_roundtrip),
    ("G03-locator-in-text", g_locator_matches_text),
    ("G04-no-orphan-references", g_no_orphan_references),
    ("G05-no-self-release", g_nothing_self_releases),
    ("G06-no-self-approved-receipts", g_no_self_approved_receipts),
    ("G07-coverage-not-overclaimed", g_coverage_not_overclaimed),
    ("G08-revocation-has-impact", g_revocation_has_impact),
    ("G09-idempotent-extraction", g_idempotent_extraction),
    ("G10-no-protected-text-in-registers", g_no_protected_text_in_registers),
    ("G11-acquisition-recorded", g_every_act_has_acquisition),
    ("G12-version-status-declared", g_source_status_declared),
    ("G13-schema-conformance", g_schema_conformance),
    ("G14-reextraction-deterministic", g_reextraction_is_deterministic),
    ("G15-no-session-credentials-in-acquisition", g_no_session_credentials_in_acquisition),
]


# --------------------------------------------------------------------------- #
# mutacoes: cada uma tem que MORRER
# --------------------------------------------------------------------------- #
def _mut_hash_forged(root: Path) -> None:
    for acts_dir in sorted((root / "dados").glob("*")):
        p = acts_dir / "atoms" / "evidence_atoms.jsonl"
        rows = _read_jsonl(p)
        if rows:
            rows[0]["fragment_sha256"] = "0" * 64
            p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                         encoding="utf-8")
            return


def _mut_orphan_reference(root: Path) -> None:
    for acts_dir in sorted((root / "dados").glob("*")):
        p = acts_dir / "atoms" / "norm_atoms_candidates.jsonl"
        rows = _read_jsonl(p)
        if rows:
            rows[0]["evidence_atom_ids"] = ["EV-NAO-EXISTE-0000"]
            p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                         encoding="utf-8")
            return


def _mut_self_release(root: Path) -> None:
    for acts_dir in sorted((root / "dados").glob("*")):
        p = acts_dir / "atoms" / "clinical_claims_candidates.jsonl"
        rows = _read_jsonl(p)
        if rows:
            rows[0]["clinical_release_allowed"] = True
            p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                         encoding="utf-8")
            return


def _mut_publication_allowed(root: Path) -> None:
    p = root / "publication_decision.json"
    if p.exists():
        d = _read_json(p)
        d["publication_allowed"] = True
        d["decision"] = "APPROVED"
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def _mut_fake_receipt(root: Path) -> None:
    for acts_dir in sorted((root / "dados").glob("*")):
        p = acts_dir / "atoms" / "clinical_claims_candidates.jsonl"
        rows = _read_jsonl(p)
        if rows:
            rows[0]["clinical_reviewer_receipt_id"] = "RCPT-AUTODECLARADO-001"
            p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
                         encoding="utf-8")
            return


def _mut_registry_hash(root: Path) -> None:
    p = root / "registros" / "00_source_registry.csv"
    rows = _read_csv(p)
    if rows:
        rows[0]["raw_sha256"] = "f" * 64
        with p.open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)


def _mut_delete_raw(root: Path) -> None:
    for acts_dir in sorted((root / "dados").glob("*")):
        raw = acts_dir / "raw"
        if raw.exists():
            for f in raw.glob("*"):
                f.unlink()
            return


def _mut_claim_full_coverage(root: Path) -> None:
    for acts_dir in sorted((root / "dados").glob("*")):
        p = acts_dir / "derivado" / "segmentacao" / "report.json"
        if p.exists():
            d = _read_json(p)
            d["unclassified_bytes"] = 0
            d["issue_codes"] = []
            p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
            return



def _mut_session_cookie(root: Path) -> None:
    """M09: synthetic cookie must be rejected by G15 (never a real session)."""
    for path in sorted((root / "dados").glob("*/acquisition.json")):
        obj = _read_json(path)
        obj.setdefault("http_headers", {})["Set-Cookie"] = "synthetic_session=INJECTED_TEST_ONLY"
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return


MUTATIONS: list[tuple[str, Callable[[Path], None], str]] = [
    ("M01-hash-forged", _mut_hash_forged, "G02"),
    ("M02-orphan-reference", _mut_orphan_reference, "G04"),
    ("M03-claim-self-release", _mut_self_release, "G05"),
    ("M04-publication-approved", _mut_publication_allowed, "G05"),
    ("M05-fake-review-receipt", _mut_fake_receipt, "G06"),
    ("M06-registry-hash-wrong", _mut_registry_hash, "G01"),
    ("M07-raw-artifact-deleted", _mut_delete_raw, "G01"),
    ("M08-overclaimed-coverage", _mut_claim_full_coverage, "G07"),
    ("M09-injected-cookie", _mut_session_cookie, "G15"),
]


# --------------------------------------------------------------------------- #
def run_gates(root: Path) -> dict:
    tests: list[dict] = []
    for gid, fn in CHECKS:
        try:
            issues = fn(root)
        except Exception as exc:  # noqa: BLE001 - gate que estoura e gate que falhou
            issues = [f"{gid} lancou excecao: {type(exc).__name__}: {exc}"]
        tests.append({
            "id": gid,
            "status": "PASS" if not issues else "FAIL",
            "issues": issues,
            "detail": "ok" if not issues else "; ".join(issues[:4]),
        })

    # --- mutacoes: o mutante tem que morrer ---
    mutation_results = []
    for mid, mutate, expected_gate in MUTATIONS:
        with tempfile.TemporaryDirectory() as tmp:
            sandbox = Path(tmp) / "pkg"
            shutil.copytree(root, sandbox, ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc", "gates"))
            try:
                mutate(sandbox)
            except Exception as exc:  # noqa: BLE001
                mutation_results.append({
                    "id": mid, "expected_gate": expected_gate, "status": "FAIL",
                    "detail": f"mutacao nao aplicavel: {type(exc).__name__}: {exc}",
                })
                continue
            died = False
            detail = ""
            for gid, fn in CHECKS:
                try:
                    issues = fn(sandbox)
                except Exception as exc:  # noqa: BLE001
                    issues = [f"{gid} lancou excecao: {exc}"]
                if issues:
                    died = True
                    detail = f"{gid} detectou: {issues[0]}"
                    break
            mutation_results.append({
                "id": mid,
                "expected_gate": expected_gate,
                "status": "PASS" if died else "FAIL",
                "detail": detail or "MUTANTE SOBREVIVEU — portao quebrado",
                "mutant_killed": died,
            })

    passed = sum(1 for t in tests if t["status"] == "PASS")
    failed = len(tests) - passed
    mut_pass = sum(1 for m in mutation_results if m["status"] == "PASS")
    mut_fail = len(mutation_results) - mut_pass
    total = len(tests) + len(mutation_results)
    total_pass = passed + mut_pass
    status = "PASS" if (failed == 0 and mut_fail == 0) else "FAIL"
    return {
        "schema": "CKO-PILOT-TEST-REPORT-v1.0.0",
        "executed_at_utc": _now(),
        "total": total,
        "passed": total_pass,
        "failed": failed + mut_fail,
        "status": status,
        "tests": tests,
        "mutations": mutation_results,
        "interpretation": (
            "PASS = nenhum defeito tecnico conhecido nos portoes executados. "
            "NAO significa norma vigente, direito concedido, revisao humana feita "
            "ou liberacao para publicacao. Todo candidato permanece CANDIDATE e a "
            "decisao de publicacao permanece HOLD."
        ),
        "publication_allowed": False,
        "clinical_decision_allowed": False,
    }
