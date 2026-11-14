#!/usr/bin/env python3
"""Read-only G6 preflight for CKO claim evidence, not clinical attestation.

Technical graph consistency is NOT official normative vigency, clinical review,
copyright license, GitHub identity attestation, or publication authorization.
This code can report a consistent candidate; it CANNOT authorize release.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REQUIRED = frozenset({
    "SOURCE_REGISTER", "CLAIM_LEDGER", "EVIDENCE_ATOMS",
    "CONTENT_REGISTER", "HOLD_HUMAN", "CONFLICT_REGISTER",
})
ALLOWED_SOURCE_PREFIXES = ("https://www.cofen.gov.br/", "https://bvsms.saude.gov.br/")


def _linked(value: Any) -> list[str]:
    if not isinstance(value, str):
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def inspect_pmo(payload: dict, source_sha256: str) -> dict[str, Any]:
    issues: set[str] = set()
    registers = payload.get("registers", [])
    if not isinstance(registers, list):
        registers = []
        issues.add("REGISTER_LIST_INVALID")
    rows_by_register = {}
    for register in registers:
        if not isinstance(register, dict) or not isinstance(register.get("register"), str):
            issues.add("REGISTER_METADATA_INVALID")
            continue
        name = register["register"]
        if name in rows_by_register:
            issues.add("DUPLICATED_REGISTER")
            continue
        rows = register.get("rows")
        if not isinstance(rows, list):
            issues.add("REGISTER_ROWS_INVALID")
            continue
        rows_by_register[name] = rows
    if not REQUIRED.issubset(rows_by_register):
        issues.add("REQUIRED_REGISTER_MISSING")
    by_name = {name: rows_by_register.get(name, []) for name in REQUIRED}

    indexed = {}
    for name, records in by_name.items():
        index = {}
        for record in records:
            if not isinstance(record, list) or not record or not isinstance(record[0], str):
                issues.add(name + "_MALFORMED_ROW")
                continue
            if record[0] in index:
                issues.add(name + "_DUPLICATE_ID")
            index[record[0]] = record
        indexed[name] = index

    source_ids = indexed["SOURCE_REGISTER"]
    claim_ids = indexed["CLAIM_LEDGER"]
    atom_ids = indexed["EVIDENCE_ATOMS"]
    content = indexed["CONTENT_REGISTER"]
    if not source_ids or not claim_ids or not atom_ids or not content:
        issues.add("EMPTY_ESSENTIAL_REGISTER")

    for claim_id, row in claim_ids.items():
        if len(row) < 10 or not isinstance(row[1], str) or not row[1].strip():
            issues.add("CLAIM_MISSING_TEXT_OR_STATUS")
            continue
        if row[4] not in atom_ids:
            issues.add("CLAIM_ORPHAN_ATOM")
        if not row[3]:
            issues.add("CLAIM_MISSING_NORMATIVE_CLAUSE")
        if "PENDING" not in str(row[8]) and "HOLD" not in str(row[9]):
            issues.add("CLAIM_UNREVIEWED_STATUS_NOT_VERIFIED")
    for atom_id, row in atom_ids.items():
        if len(row) < 4:
            issues.add("ATOM_ROW_INCOMPLETE")
            continue
        if not _linked(row[3]) or any(c not in claim_ids for c in _linked(row[3])):
            issues.add("ATOM_CLAIM_REFERENCE_MISSING")
    for content_id, row in content.items():
        if len(row) < 11:
            issues.add("CONTENT_ROW_INCOMPLETE")
            continue
        if row[6] not in source_ids:
            issues.add("CONTENT_UNKNOWN_SOURCE")
        refs = _linked(row[7])
        if not refs or any(c not in claim_ids for c in refs):
            issues.add("CONTENT_CLAIM_REFERENCE_MISSING")
        if row[9] != "HOLD_HUMAN" or row[10] != "CANDIDATE_NO_PUBLICATION":
            issues.add("CONTENT_NOT_HELD")
    for source_id, row in source_ids.items():
        if len(row) < 10 or not isinstance(row[7], str) or not row[7].startswith(ALLOWED_SOURCE_PREFIXES):
            issues.add("SOURCE_URL_NOT_VERIFIED")
        if len(row) >= 10 and "M03_RECOVERED_SOURCE_TEXT" not in str(row[9]):
            issues.add("SOURCE_ORIGIN_NOT_RECONCILED")
    holds = indexed["HOLD_HUMAN"]
    if not holds or not any("OPEN" in str(row) for row in holds.values()):
        issues.add("REVIEW_HOLD_NOT_DOCUMENTED")
    conflicts = indexed["CONFLICT_REGISTER"]
    if not conflicts or not any("OPEN_HOLD" in str(row) for row in conflicts.values()):
        issues.add("CONFLICT_HOLD_NOT_DOCUMENTED")

    if payload.get("release_allowed") is not False:
        issues.add("SELF_ASSERTED_RELEASE_UNTRUSTED")

    # A manifest cannot prove a reviewer is licensed, independent, has read the
    # exact official source, or verified legal vigency. None is inferred here.
    return {
        "schema": "CE-CKO-G6-READONLY-PREFLIGHT-1.0.0",
        "status": "HOLD_HUMAN_NORMATIVE_RIGHTS",
        "input_sha256": source_sha256,
        "counts": {
            "sources": len(source_ids),
            "claims": len(claim_ids),
            "evidence_atoms": len(atom_ids),
            "editorial_masters": len(content),
            "open_holds": len(holds),
            "open_conflicts": len(conflicts),
        },
        "technically_consistent": not issues,
        "structural_issues": sorted(issues),
        "independent_reviewer_verified": False,
        "professional_credential_verified": False,
        "official_publication_chain_verified": False,
        "rights_by_operation_verified": False,
        "can_publish": False,
        "can_promote_to_canonical": False,
        "clinical_release_gate_exit_code": 2,
    }


def inspect_file(path: Path) -> dict:
    raw = Path(path).read_bytes()
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("PMO manifest must be a JSON object")
    return inspect_pmo(payload, hashlib.sha256(raw).hexdigest())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="G6: technical preflight only, never clinical approval")
    parser.add_argument("--pmo", type=Path, required=True)
    parser.add_argument("--diagnostic-only", action="store_true",
                        help="Exit 0 only for internally consistent HOLD candidate")
    args = parser.parse_args(argv)
    try:
        report = inspect_file(args.pmo)
    except (OSError, ValueError, TypeError) as exc:
        print("HOLD_SOURCE:" + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    if args.diagnostic_only and report["technically_consistent"]:
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
