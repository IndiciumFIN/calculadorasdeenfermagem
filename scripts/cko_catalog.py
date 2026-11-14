#!/usr/bin/env python3
"""Compile a deterministic CKO metadata graph and living dictionary.

Canonical inputs: contracts/fontes/*.json and contracts/policies/*.json.
Optional candidate lineage: PMO_REGISTER_SNAPSHOT_M08_M09.json.
This is a read-only catalog/compiler, NEVER a clinical promotion engine.
No web, Drive, Supabase, secret, patient data or publication operations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

VERSION = "CE-CKO-METAMODEL-1.0.0"
REPO_ROOT = Path(__file__).resolve().parents[1]
_VALID_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,127}$")
_VALID_PATH = re.compile(r"^[A-Za-z0-9_./-]+$")
_POLICY_ID = re.compile(r"^KERNEL-POLICY-[0-9]{3}$")
_PMO_TABLES = {
    "SOURCE_REGISTER": "NORM_SOURCE",
    "DOCUMENT_REGISTER": "NORM_DOCUMENT",
    "EVIDENCE_ATOMS": "EVIDENCE_ATOM",
    "CLAIM_LEDGER": "CANDIDATE_CLAIM",
    "CONTENT_REGISTER": "EDITORIAL_CONTENT",
}


def _sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _types(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "unsupported"


def _schema(rows: list[dict]) -> list[dict]:
    if not rows:
        return []
    fields = sorted({key for row in rows for key in row})
    return [
        {
            "field": field,
            "observed_types": sorted({_types(row[field]) for row in rows if field in row}),
            "present_in": sum(field in row for row in rows),
            "required_in_all_records": all(field in row for row in rows),
            "definition_origin": "OBSERVED_CONTRACT_METADATA_NOT_NORMATIVE_CLAIM",
        }
        for field in fields
    ]


def _parts(value: Any) -> list[str]:
    if not isinstance(value, str):
        return []
    return [token.strip() for token in value.split(";") if token.strip()]


def build(root: Path, *, pmo_file: Path | None = None) -> dict:
    root = root.resolve()
    nodes: dict[str, dict] = {}
    edges: set[tuple[str, str, str]] = set()
    findings: list[dict] = []
    source_data: dict[str, dict] = {}
    policy_data: dict[str, dict] = {}
    source_files = sorted((root / "contracts/fontes").glob("*.json"))
    policy_files = sorted((root / "contracts/policies").glob("*.json"))
    if not source_files or not policy_files:
        raise ValueError("Missing canonical source or policy registry")
    if (root / "contracts/fonts").exists():
        findings.append(dict(severity="ERROR", code="LEGACY_SOURCE_DIR",
                             subject="contracts/fonts", detail="Use contracts/fontes only"))

    def flag(severity: str, code: str, subject: str, detail: str) -> None:
        findings.append(dict(severity=severity, code=code,
                             subject=subject, detail=detail))

    def node(kind: str, identity: str, **attrs: Any) -> str:
        if not identity or not isinstance(identity, str):
            raise ValueError("Empty graph node identity")
        nid = kind + ":" + identity
        if nid in nodes:
            flag("ERROR", "DUPLICATE_NODE", nid, "Node declared more than once")
        else:
            nodes[nid] = {"id": nid, "type": kind, **attrs}
        return nid

    def link(from_id: str, relation: str, to_id: str) -> None:
        edges.add((from_id, relation, to_id))

    def read_registry(file: Path, collection: dict) -> tuple[dict, str]:
        try:
            raw = file.read_bytes()
            data = json.loads(raw)
        except (OSError, ValueError) as exc:
            flag("ERROR", "INVALID_JSON", file.relative_to(root).as_posix(), type(exc).__name__)
            return {}, ""
        if not isinstance(data, dict):
            flag("ERROR", "INVALID_CONTRACT_OBJECT", file.name, "JSON root must be object")
            return {}, ""
        return data, _sha(raw)

    for file in source_files:
        rel = file.relative_to(root).as_posix()
        source, digest = read_registry(file, source_data)
        if not source:
            continue
        slug = file.stem
        if not _VALID_ID.fullmatch(slug):
            flag("ERROR", "INVALID_SOURCE_ID", rel, slug)
        if source.get("fonte_slug") != slug or source.get("source_contract") != rel:
            flag("ERROR", "SOURCE_REFERENCE_MISMATCH", rel, "Name, slug and self link differ")
        if slug in source_data:
            flag("ERROR", "DUPLICATE_SOURCE", rel, slug)
        source_data[slug] = source
        source_n = node(
            "SOURCE_CONTRACT", slug,
            contract_path=rel, contract_sha256=digest,
            authority_declared=str(source.get("fonte_oficial", "")),
            source_kind_declared=str(source.get("tipo", "")),
            normative_validity="NOT_VERIFIED",
            rights_approval="NOT_VERIFIED",
            release_allowed=False,
        )
        policy_id = source.get("kernel_policy_id")
        if not isinstance(policy_id, str) or not _POLICY_ID.fullmatch(policy_id):
            flag("ERROR", "INVALID_POLICY_POINTER", rel, repr(policy_id))
        else:
            link(source_n, "GOVERNED_BY", "KERNEL_POLICY:" + policy_id)
        parser = source.get("parser")
        if not isinstance(parser, str) or not _VALID_PATH.fullmatch(parser) or (
            not parser.startswith("packages/cli/") or ".." in Path(parser).parts
            or not parser.endswith(".py")
        ):
            flag("ERROR", "INVALID_PARSER_PATH", rel, repr(parser))
            continue
        absolute = (root / parser).resolve()
        if not absolute.is_relative_to(root):
            flag("ERROR", "PARSER_PATH_ESCAPE", rel, parser)
            continue
        parser_n = "SOURCE_PARSER:" + parser
        if parser_n not in nodes:
            node("SOURCE_PARSER", parser,
                 path=parser, candidate_file_present=absolute.is_file(),
                 admission="UNVERIFIED_IMPLEMENTATION" if absolute.is_file()
                 else "MISSING_IMPLEMENTATION", release_allowed=False)
        link(source_n, "PARSED_BY_CANDIDATE", parser_n)
        if not absolute.is_file():
            flag("PENDING", "MISSING_PARSER", rel, parser)

    for file in policy_files:
        rel = file.relative_to(root).as_posix()
        data, digest = read_registry(file, policy_data)
        if not data:
            continue
        pid = file.stem
        if not _POLICY_ID.fullmatch(pid) or data.get("id") != pid:
            flag("ERROR", "POLICY_ID_MISMATCH", rel, pid)
        if pid in policy_data:
            flag("ERROR", "DUPLICATE_POLICY", rel, pid)
        policy_data[pid] = data
        node("KERNEL_POLICY", pid, path=rel, contract_sha256=digest,
             version=str(data.get("version", "")),
             review_required=data.get("requires_human_review") is True,
             sha256_required=data.get("sha256_required") is True,
             wo_required=data.get("wo_required") is True,
             rights_approval="NOT_VERIFIED",
             release_allowed=False)
        source_path = data.get("source_contract")
        if not isinstance(source_path, str) or not source_path.startswith("contracts/fontes/") or not source_path.endswith(".json"):
            flag("ERROR", "INVALID_POLICY_SOURCE_PATH", rel, repr(source_path))
        else:
            sid = Path(source_path).stem
            link("KERNEL_POLICY:" + pid, "POLICY_SOURCE_CONTRACT", "SOURCE_CONTRACT:" + sid)
            source = source_data.get(sid)
            if not source or source.get("kernel_policy_id") != pid:
                flag("ERROR", "BROKEN_POLICY_SOURCE_INVERSE", rel, source_path)
        validators = data.get("validators")
        if not isinstance(validators, list) or not validators:
            flag("ERROR", "MISSING_POLICY_VALIDATORS", rel, "Require nonempty array")
            validators = []
        if len(validators) != len(set(str(x) for x in validators)):
            flag("ERROR", "DUPLICATE_VALIDATOR_LINK", rel, "Repeated policy validator")
        for validator in validators:
            if not isinstance(validator, str) or not _VALID_ID.fullmatch(validator):
                flag("ERROR", "INVALID_VALIDATOR_ID", rel, repr(validator))
                continue
            vid = "VALIDATOR:" + validator
            if vid not in nodes:
                node("VALIDATOR", validator, code_self_test="NOT_ATTESTED_BY_CATALOG",
                     clinical_reviewer="NOT_ATTESTED", release_allowed=False)
            link("KERNEL_POLICY:" + pid, "REQUIRES_VALIDATOR", vid)
        if (data.get("requires_human_review") is not True or
            data.get("wo_required") is not True or
            data.get("sha256_required") is not True):
            flag("PENDING", "POLICY_REVIEW_INCOMPLETE", rel,
                 "Review / WO / source SHA gates not all enabled; not an approval")
        if source_path and isinstance(source_path, str):
            slug = Path(source_path).stem
            source = source_data.get(slug, {})
            declared = source.get("validators")
            values = ([declared] if isinstance(declared, str) else declared)
            if isinstance(values, list) and not set(values).issubset(set(validators)):
                flag("PENDING", "SOURCE_VALIDATOR_DRIFT", rel,
                     "Source contract validator declaration differs from policy")
            elif isinstance(values, list) and set(values) != set(validators):
                flag("PENDING", "SOURCE_VALIDATOR_DRIFT", rel,
                     "Policy validators extend source contract declaration")

    for slug, source in source_data.items():
        pid = source.get("kernel_policy_id")
        if pid not in policy_data:
            flag("ERROR", "SOURCE_POLICY_ORPHAN", slug, str(pid))
    for pid, policy in policy_data.items():
        sid = Path(str(policy.get("source_contract", ""))).stem
        if sid not in source_data:
            flag("ERROR", "POLICY_SOURCE_ORPHAN", pid, sid)

    if pmo_file is not None:
        _add_pmo(root, pmo_file, node, link, flag)

    for src, relation, target in edges:
        if src not in nodes or target not in nodes:
            flag("ERROR", "GRAPH_ORPHAN", src + " -> " + target, relation)

    findings.sort(key=lambda row: (row["severity"], row["code"], row["subject"], row["detail"]))
    ordered = [
        {"source": src, "relation": relation, "target": target}
        for src, relation, target in sorted(edges)
    ]
    return {
        "schema_version": VERSION,
        "status": "METADATA_CANDIDATE_NO_CLINICAL_RELEASE",
        "publication_allowed": False,
        "generated_from": ["contracts/fontes/*.json", "contracts/policies/*.json"] +
                          ([pmo_file.name] if pmo_file is not None else []),
        "verified_input_digest": (
            {"pmo_snapshot_sha256": _sha(pmo_file.read_bytes())}
            if pmo_file is not None and pmo_file.is_file() else {}
        ),
        "statistics": {
            "sources": len(source_data), "policies": len(policy_data),
            "candidate_parsers": sum(x["type"] == "SOURCE_PARSER" for x in nodes.values()),
            "missing_parsers": sum(f["code"] == "MISSING_PARSER" for f in findings),
            "validators_declared": sum(x["type"] == "VALIDATOR" for x in nodes.values()),
            "nodes": len(nodes), "edges": len(edges),
            "errors": sum(f["severity"] == "ERROR" for f in findings),
            "pending": sum(f["severity"] == "PENDING" for f in findings),
            "finding_counts_by_code": dict(sorted(Counter(f["code"] for f in findings).items())),
        },
        "dictionary": {
            "SOURCE_CONTRACT": _schema(list(source_data.values())),
            "KERNEL_POLICY": _schema(list(policy_data.values())),
        },
        "entities": [nodes[k] for k in sorted(nodes)],
        "relationships": ordered,
        "findings": findings,
    }


def _add_pmo(root: Path, file: Path, node, link, flag) -> None:
    """Attach real, not inferred, SOURCE->DOCUMENT->EVIDENCE->CLAIM->CONTENT IDs."""
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        blocks = data["registers"]
        tables = {b["register"]: b["rows"] for b in blocks}
    except (OSError, ValueError, TypeError, KeyError) as exc:
        flag("ERROR", "PMO_INVALID", file.name, type(exc).__name__)
        return
    for table, kind in _PMO_TABLES.items():
        rows = tables.get(table)
        if not isinstance(rows, list):
            flag("ERROR", "PMO_TABLE_MISSING", table, "Missing PMO register")
            continue
        seen: set[str] = set()
        for row in rows:
            if not isinstance(row, list) or not row or not isinstance(row[0], str):
                flag("ERROR", "PMO_ROW_INVALID", table, "Expected [id, ...]")
                continue
            rid = row[0]
            if rid in seen:
                flag("ERROR", "PMO_ROW_DUPLICATE", table, rid)
                continue
            seen.add(rid)
            node(kind, rid, status="CANDIDATE_HOLD_REVIEW", release_allowed=False)
    norm_sources = {x[0] for x in tables.get("SOURCE_REGISTER", []) if isinstance(x, list) and x}
    docs = {x[0] for x in tables.get("DOCUMENT_REGISTER", []) if isinstance(x, list) and x}
    evidences = {x[0] for x in tables.get("EVIDENCE_ATOMS", []) if isinstance(x, list) and x}
    claims = {x[0] for x in tables.get("CLAIM_LEDGER", []) if isinstance(x, list) and x}

    def check_link(src_type: str, src_id: str, rel: str, dst_type: str,
                   dst_id: str, known: set[str]):
        if dst_id not in known:
            flag("ERROR", "PMO_ORPHAN", src_id, rel + " -> " + dst_id)
        else:
            link(src_type + ":" + src_id, rel, dst_type + ":" + dst_id)

    for row in tables.get("DOCUMENT_REGISTER", []):
        if len(row) < 2:
            flag("ERROR", "PMO_ROW_TRUNCATED", "DOCUMENT_REGISTER", str(row[:1]))
            continue
        check_link("NORM_SOURCE", row[1], "HAS_DOCUMENT", "NORM_DOCUMENT",
                   row[0], docs)
        if row[1] not in norm_sources:
            flag("ERROR", "PMO_ORPHAN", row[0], "unknown normative source " + row[1])
    for row in tables.get("EVIDENCE_ATOMS", []):
        if len(row) < 4:
            flag("ERROR", "PMO_ROW_TRUNCATED", "EVIDENCE_ATOMS", str(row[:1]))
            continue
        check_link("NORM_DOCUMENT", row[1], "SUPPORTS_EVIDENCE", "EVIDENCE_ATOM",
                   row[0], evidences)
        if row[1] not in docs:
            flag("ERROR", "PMO_ORPHAN", row[0], "unknown document " + row[1])
        for claim in _parts(row[3]):
            check_link("EVIDENCE_ATOM", row[0], "SUPPORTS_CLAIM",
                       "CANDIDATE_CLAIM", claim, claims)
    for row in tables.get("CLAIM_LEDGER", []):
        if len(row) < 11:
            flag("ERROR", "PMO_ROW_TRUNCATED", "CLAIM_LEDGER", str(row[:1]))
            continue
        if row[4] not in evidences:
            flag("ERROR", "PMO_ORPHAN", row[0], "unknown evidence " + row[4])
        else:
            link("EVIDENCE_ATOM:" + row[4], "SUPPORTS_CLAIM",
                 "CANDIDATE_CLAIM:" + row[0])
        if row[9] != "PENDING_CLINICAL_AND_EDITORIAL_REVIEW" or row[10] != "EVIDENCE_BOUND_HOLD":
            flag("ERROR", "PMO_CLAIM_RELEASE_BYPASS", row[0], "Candidate must stay HOLD")
    for row in tables.get("CONTENT_REGISTER", []):
        if len(row) < 11:
            flag("ERROR", "PMO_ROW_TRUNCATED", "CONTENT_REGISTER", str(row[:1]))
            continue
        for sid in _parts(row[6]):
            check_link("NORM_SOURCE", sid, "SUPPORTS_CONTENT_CANDIDATE",
                       "EDITORIAL_CONTENT", row[0], {x[0] for x in tables.get("CONTENT_REGISTER", []) if x})
            if sid not in norm_sources:
                flag("ERROR", "PMO_ORPHAN", row[0], "unknown content source " + sid)
        for cid in _parts(row[7]):
            check_link("CANDIDATE_CLAIM", cid, "USED_BY_CONTENT_CANDIDATE",
                       "EDITORIAL_CONTENT", row[0], {x[0] for x in tables.get("CONTENT_REGISTER", []) if x})
            if cid not in claims:
                flag("ERROR", "PMO_ORPHAN", row[0], "unknown content claim " + cid)
        if row[9] != "HOLD_HUMAN" or row[10] != "CANDIDATE_NO_PUBLICATION":
            flag("ERROR", "PMO_CONTENT_RELEASE_BYPASS", row[0], "Editorial content must stay HOLD")
    # Legal normative act IDs and generic source contracts have no verified
    # crosswalk in these inputs. Never infer that cofen_dou means any given act.
    for sid in sorted(norm_sources):
        flag("PENDING", "NORMATIVE_CROSSWALK_UNVERIFIED", sid,
             "No evidence-backed mapping from normative act to source contract")


def _cell(value: Any) -> str:
    return str(value).replace("|", "&#124;").replace("\n", " ").replace("\r", "")


def render(catalog: dict) -> dict[str, str]:
    nodes = catalog["entities"]
    edges = catalog["relationships"]
    stats = catalog["statistics"]
    headers = [
        "# Catálogo CKO / metamodelo canônico (geração determinística)",
        "", f"Versão: `{VERSION}`.",
        "",
        "**ATENÇÃO:** esta geração reconcilia contratos de origem e proveniência candidata. "
        "Não certifica vigência normativa, direitos, revisões clínicas ou permissão de publicação.",
        "",
        "## Indicadores",
        "",
        "| Fontes | Políticas | Parsers ausentes | Validadores declarados | Relações | Erros | Pendências |",
        "|---:|---:|---:|---:|---:|---:|---:|",
        f"| {stats['sources']} | {stats['policies']} | {stats['missing_parsers']} | "
        f"{stats['validators_declared']} | {stats['edges']} | "
        f"{stats['errors']} | {stats['pending']} |",
        "",
        "## Relações canônicas declaradas",
        "",
        "| Contrato de fonte | Política | Parser | Implementação física |",
        "|---|---|---|---|",
    ]
    by_id = {n["id"]: n for n in nodes}
    indexed = {}
    for e in edges:
        indexed.setdefault((e["source"], e["relation"]), []).append(e["target"])
    for n in nodes:
        if n["type"] != "SOURCE_CONTRACT":
            continue
        source = n["id"]
        policy = indexed.get((source, "GOVERNED_BY"), ["—"])[0]
        parser_id = indexed.get((source, "PARSED_BY_CANDIDATE"), ["—"])[0]
        parser_info = by_id.get(parser_id, {})
        status = "PRESENTE ≠ HOMOLOGADO" if parser_info.get("candidate_file_present") else "AUSENTE / HOLD"
        headers.append(f"| `{_cell(n['contract_path'])}` | `{_cell(policy)}` | "
                       f"`{_cell(parser_info.get('path', parser_id))}` | {status} |")
    headers += ["", "## Achados e controles", "",
                "| Gravidade | Código | Entidade | Diagnóstico |",
                "|---|---|---|---|"]
    for f in catalog["findings"]:
        headers.append("| " + " | ".join(_cell(f[x]) for x in ("severity", "code", "subject", "detail")) + " |")
    headers += ["", "O status de candidato não é liberação; a existência de um parser "
                "também não substitui testes, aprovação de direitos e revisão humana.", ""]
    dictionary = [
        "# Dicionário vivo de contratos de origem e políticas",
        "", "Gerado automaticamente dos campos JSON efetivamente encontrados. "
        "Os tipos e a obrigatoriedade abaixo são **observados**, não normas clínicas.", ""
    ]
    for kind, rows in catalog["dictionary"].items():
        dictionary += [f"## {kind}", "", "| Campo | Tipos observados | Presença | Em todos os registros? |",
                       "|---|---|---:|---|"]
        total = stats["sources"] if kind == "SOURCE_CONTRACT" else stats["policies"]
        for f in rows:
            dictionary.append(f"| `{_cell(f['field'])}` | "
                              f"{_cell(', '.join(f['observed_types']))} | "
                              f"{f['present_in']}/{total} | "
                              f"{'Sim' if f['required_in_all_records'] else 'Não'} |")
        dictionary.append("")
    diagram = ["flowchart TD"]
    mapping = {n["id"]: "N" + hashlib.sha256(n["id"].encode()).hexdigest()[:12] for n in nodes}
    for n in nodes:
        label = n["id"].replace('"', "'").replace("<", "").replace(">", "")
        diagram.append(f'  {mapping[n["id"]]}["{label}"]')
    for e in edges:
        diagram.append(f'  {mapping[e["source"]]} -->|{e["relation"]}| {mapping[e["target"]]}')
    return {
        "catalog.json": json.dumps(catalog, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        "SUMMARY.md": "\n".join(headers),
        "dictionary.md": "\n".join(dictionary),
        "relations.mmd": "\n".join(diagram) + "\n",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--pmo", type=Path,
                        help="Explicit PMO snapshot; never discover unverified lineage")
    parser.add_argument("--check", action="store_true",
                        help="Reject drift instead of modifying generated files")
    args = parser.parse_args()
    root = args.root.resolve()
    out_dir = args.out_dir or root / "governance/cko/generated"
    catalog = build(root, pmo_file=args.pmo)
    outputs = render(catalog)
    mismatch = []
    for name, content in outputs.items():
        path = out_dir / name
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != content:
                mismatch.append(str(path))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
    result = {"schema_version": VERSION, "generated_files": sorted(outputs),
              "errors": catalog["statistics"]["errors"],
              "pending": catalog["statistics"]["pending"],
              "publication_allowed": False, "drift": mismatch,
              "status": "FAIL" if mismatch or catalog["statistics"]["errors"] else
                        "HOLD" if catalog["statistics"]["pending"] else "METADATA_PASS"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if mismatch or catalog["statistics"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
