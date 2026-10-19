#!/usr/bin/env python3
"""CE PMO deterministic anti-rework gate, READ_ONLY and fail-closed.

This is a local documentary decision engine, not a persistent service,
GitHub required check or authoritative Kernel admission.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

APPROVED_MODES = {"READ_ONLY", "DOCUMENTARY"}
EXECUTED = {"EXECUTED_EVIDENCED", "EXECUTED_AWAITING_VALIDATION"}
BLOCKING = EXECUTED | {"IN_PROGRESS", "HOLD", "FAILED_UNRESOLVED"}
REQUIRED_FIELDS = {
    "task_id", "intent", "scope", "cutoff", "mode", "source_ids", "project",
    "domain", "operation_kind", "population_snapshot", "policy_version",
    "validator_version", "schema_version", "target_artifact", "intended_outputs",
    "jurisdiction", "language", "license_context", "parameters",
}
HASH = re.compile(r"^[0-9a-f]{64}$")


def canonical(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("missing identity dimension")
    return " ".join(value.strip().casefold().split())


def fingerprint(task: dict, *, include_cutoff: bool = True) -> str:
    keys = ("project", "domain", "operation_kind", "intent", "scope", "population_snapshot", "policy_version", "validator_version", "schema_version", "target_artifact", "jurisdiction", "language", "license_context")
    fields = [canonical(task[k]) for k in keys]
    fields += [sorted(canonical(v) for v in task["source_ids"]), task["parameters"], sorted(canonical(v) for v in task["intended_outputs"])]
    if include_cutoff:
        fields.append(canonical(task["cutoff"]))
    serialized = json.dumps(fields, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def verdict(allowed: bool, code: str, matches: list[str] | None = None, reason: str = "") -> dict:
    return {"decision": "ALLOW_PREFLIGHT_ONLY" if allowed else "BLOCK", "code": code, "matched_task_ids": sorted(set(matches or [])), "reason": reason, "not_kernel_admission": True}


def eligible_reuse_only(candidate: dict, known_sources: set[str]) -> bool:
    """Allow only documentary linkage to already registered evidence, never source reprocessing."""
    return (
        candidate.get("mode") == "READ_ONLY"
        and candidate.get("operation_kind") == "EVIDENCE_LINK_ONLY"
        and candidate.get("evidence_of_new_scope") == "REUSE_ONLY_EXISTING_EVIDENCE"
        and candidate.get("intended_outputs") == ["EVIDENCE_CROSSWALK_ONLY"]
        and candidate.get("parameters") == {"no_source_reprocessing": True, "no_remote_writes": True}
        and isinstance(candidate.get("prior_evidence_ids"), list)
        and bool(candidate["prior_evidence_ids"])
        and set(candidate["prior_evidence_ids"]).issubset(known_sources)
    )


def evaluate(candidate: dict, ledger: dict, master: dict, history_index: dict | None = None) -> dict:
    if master.get("pmo_trusted") is not False or master.get("project_execution_allowed") is not False:
        return verdict(False, "MASTER_RELEASE_STATE_UNSAFE")
    if not isinstance(candidate, dict) or not isinstance(ledger, dict):
        return verdict(False, "INVALID_INPUT")
    if any(k not in candidate for k in REQUIRED_FIELDS):
        return verdict(False, "TASK_IDENTITY_INCOMPLETE")
    if candidate.get("mode") not in APPROVED_MODES:
        return verdict(False, "RUNTIME_ADMISSION_NOT_PROVEN")
    if not isinstance(candidate.get("source_ids"), list) or not candidate["source_ids"] or not isinstance(candidate.get("parameters"), dict) or not isinstance(candidate.get("intended_outputs"), list) or not candidate["intended_outputs"]:
        return verdict(False, "TASK_SOURCE_IDS_MISSING")
    known_sources = {s["source_id"] for s in master.get("source_register", []) if isinstance(s, dict) and "source_id" in s}
    if not set(candidate["source_ids"]).issubset(known_sources):
        return verdict(False, "SOURCE_IDS_NOT_VERIFIED")
    try:
        target = fingerprint(candidate)
        family = fingerprint(candidate, include_cutoff=False)
        canonical(candidate["task_id"])
    except (KeyError, ValueError, TypeError, AttributeError):
        return verdict(False, "TASK_IDENTITY_INVALID")

    if ledger.get("schema_version") != "0.1.0" or ledger.get("state") != "CANDIDATE_EVIDENCE_LEDGER_NOT_CANONICAL":
        return verdict(False, "LEDGER_NOT_TRUSTED")
    rows = ledger.get("tasks")
    if not isinstance(rows, list) or not rows:
        return verdict(False, "LEDGER_EMPTY_OR_INVALID")
    matches, variants = [], []
    seen = set()
    for row in rows:
        if not isinstance(row, dict) or any(k not in row for k in REQUIRED_FIELDS):
            return verdict(False, "LEDGER_ROW_INVALID")
        try:
            key = fingerprint(row)
            family_key = fingerprint(row, include_cutoff=False)
            row_id = canonical(row["task_id"])
        except (KeyError, ValueError, TypeError, AttributeError):
            return verdict(False, "LEDGER_IDENTITY_INVALID")
        unique = (row_id, key)
        if unique in seen:
            return verdict(False, "LEDGER_DUPLICATE_IDENTITY")
        seen.add(unique)
        status = row.get("status")
        if status not in BLOCKING | {"PLANNED_NOT_EXECUTED"}:
            return verdict(False, "LEDGER_STATUS_UNRECOGNIZED")
        if status in EXECUTED:
            evidence = row.get("evidence", {})
            if not isinstance(evidence, dict) or not evidence.get("source_ids") or evidence.get("readback") != "EXACT_OR_INDEPENDENTLY_VERIFIED":
                return verdict(False, "EXECUTION_EVIDENCE_INCOMPLETE", [row["task_id"]])
            if not set(evidence["source_ids"]).issubset(known_sources):
                return verdict(False, "EXECUTION_SOURCE_UNRESOLVED", [row["task_id"]])
        if key == target:
            matches.append(row)
        elif family_key == family or row_id == canonical(candidate["task_id"]):
            variants.append(row)

    if matches:
        ids = [x["task_id"] for x in matches]
        statuses = {x["status"] for x in matches}
        if statuses & EXECUTED:
            return verdict(False, "BLOCK_ALREADY_EXECUTED_REUSE_EVIDENCE", ids)
        if "IN_PROGRESS" in statuses:
            return verdict(False, "BLOCK_CONCURRENT_EXECUTION", ids)
        if statuses & {"HOLD", "FAILED_UNRESOLVED"}:
            return verdict(False, "BLOCK_REVIEW_PRIOR_EXCEPTION", ids)
        return verdict(False, "BLOCK_EXISTING_PLANNED_TASK_REUSE_ID", ids)
    if variants:
        return verdict(False, "HOLD_VERSION_OR_CUTOFF_VARIANT", [x["task_id"] for x in variants])
    if eligible_reuse_only(candidate, known_sources):
        return {"decision": "ALLOW_REUSE_ANALYSIS_ONLY", "code": "EXISTING_EVIDENCE_LINKAGE_NO_REEXECUTION", "matched_task_ids": [], "reason": "read-only crosswalk of registered evidence, no source processing or productive mutation", "not_kernel_admission": True}
    if ledger.get("historical_evidence_index"):
        if not isinstance(history_index, dict) or history_index.get("kind") != "HISTORICAL_EVIDENCE_INDEX_NOT_EXECUTION_LEDGER":
            return verdict(False, "HOLD_HISTORICAL_INDEX_NOT_LOADED")
        target_name = candidate.get("target_artifact")
        prior = [row["record_id"] for row in history_index.get("local_reports", []) if row.get("locator") == target_name]
        if prior:
            return verdict(False, "HOLD_PRIOR_DOCUMENTARY_EVIDENCE_REVIEW", prior)
        domain_key = canonical(candidate.get("domain", "")).upper().replace("-", "")
        historical = [row for row in history_index.get("archive_evidence", []) if row.get("domain") == domain_key]
        if historical:
            return verdict(False, "HOLD_PRIOR_FRONT_EVIDENCE_REVIEW", [row["record_id"] for row in historical][:20])
    if ledger.get("historical_coverage") != "HISTORY_RECONCILED":
        return verdict(False, "HOLD_HISTORICAL_COVERAGE_INCOMPLETE")
    if candidate.get("evidence_of_new_scope") != "DOCUMENTED_RECONCILIATION":
        return verdict(False, "NEW_TASK_SCOPE_EVIDENCE_REQUIRED")
    return verdict(True, "NEW_DOCUMENTARY_TASK_PREFLIGHT_ONLY")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--historical-index", type=Path)
    args = parser.parse_args()
    try:
        sources = [json.loads(p.read_text(encoding="utf-8")) for p in (args.candidate, args.ledger, args.master)]
        index = json.loads(args.historical_index.read_text(encoding="utf-8")) if args.historical_index else None
        result = evaluate(*sources, index)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        result = verdict(False, "INPUT_UNAVAILABLE_OR_INVALID")
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0 if result["decision"] in {"ALLOW_PREFLIGHT_ONLY", "ALLOW_REUSE_ANALYSIS_ONLY"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
