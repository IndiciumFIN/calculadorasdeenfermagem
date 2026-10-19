#!/usr/bin/env python3
"""Fail-closed preflight for CE documentary inventory operations.

No mutations, network calls or publication. This gate is not Kernel admission.
Return 0 only when supplied inputs satisfy the documentary constraints.
"""
from __future__ import annotations

import argparse
import json
import re
import stat
import sys
import zipfile
from pathlib import Path, PurePosixPath

from ce_pmo_no_rework_agent_v01 import evaluate as anti_rework_evaluate

APPROVED_BRANCH = "pmo/recovery-controlled-20261019"
DOC_ROOT = "docs/pmo/recovery/20261019/"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GITSHA = re.compile(r"^[0-9a-f]{40}$")
FORBIDDEN_OPERATIONS = {"delete", "remove", "unlink", "truncate", "reset", "force_push", "merge", "deduplicate_delete", "overwrite_source", "extract_zip", "promote", "main_write"}
PROMOTION_KEYS = {"pmo_trusted", "project_execution_allowed", "canonical_approved", "release_approved", "m24_released"}


def guard(condition: bool, code: str, findings: list[str]) -> None:
    if not condition:
        findings.append(code)


def check_manifest(data: dict, findings: list[str]) -> None:
    guard(data.get("root_scope") == "recursive_workspace_only", "MANIFEST_SCOPE_MISMATCH", findings)
    rows = data.get("files")
    if not isinstance(rows, list):
        findings.append("MANIFEST_FILES_MISSING")
        return
    seen: set[str] = set()
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            findings.append(f"MANIFEST_ROW_INVALID:{i}")
            continue
        name = row.get("relative_path", "")
        path = PurePosixPath(name) if isinstance(name, str) else PurePosixPath("")
        guard(isinstance(name, str) and name and not path.is_absolute() and ".." not in path.parts and "\\" not in name, f"UNSAFE_MANIFEST_PATH:{i}", findings)
        guard(name not in seen, f"DUPLICATE_MANIFEST_PATH:{i}", findings)
        seen.add(name)
        guard(isinstance(row.get("sha256"), str) and bool(SHA256.fullmatch(row["sha256"])), f"HASH_MISSING_OR_INVALID:{i}", findings)
        guard(isinstance(row.get("bytes"), int) and row["bytes"] >= 0, f"SIZE_MISSING_OR_INVALID:{i}", findings)
        guard(row.get("external_persistence") == "NOT_PROVEN_BY_LOCAL_SCAN", f"FALSE_CUSTODY_CLAIM:{i}", findings)


def check_summary(data: dict, findings: list[str]) -> None:
    guard(data.get("privacy") == "AGGREGATE_ONLY_NO_FILENAMES_OR_HASHES", "SUMMARY_PRIVACY_UNDECLARED", findings)
    guard(data.get("pmo_gate") == "HOLD", "FALSE_GATE_PASS", findings)
    forbidden = {"relative_path", "path", "filename", "sha256", "hash", "url", "email", "zip_containers", "exact_duplicate_paths"}

    def walk(value: object, parent: str = "summary") -> None:
        if isinstance(value, dict):
            for k, v in value.items():
                if k.lower() in forbidden or (k.lower() == "files" and not (parent.startswith("summary.groups.") and isinstance(v, int))):
                    findings.append(f"PRIVATE_FIELD_IN_PUBLIC_SUMMARY:{parent}.{k}")
                walk(v, f"{parent}.{k}")
        elif isinstance(value, list):
            for n, v in enumerate(value):
                walk(v, f"{parent}[{n}]")

    walk(data)


def check_pmo(data: dict, findings: list[str]) -> None:
    guard(data.get("pmo_trusted") is False, "PMO_FALSE_PASS", findings)
    guard(data.get("project_execution_allowed") is False, "PROJECT_EXECUTION_FALSE_PASS", findings)
    guard(data.get("state") == "CANDIDATE_NOT_CANONICAL", "PMO_PREMATURE_CANONICAL", findings)
    restrictions = data.get("scope_restrictions", [])
    guard("M24_HOLD" in restrictions, "M24_HOLD_REMOVED", findings)
    guard("NO_MERGE" in restrictions, "MERGE_RESTRICTION_REMOVED", findings)
    exception = data.get("pmo_preservation_exception", {})
    guard(exception.get("allowed_target_branch") == APPROVED_BRANCH, "PMO_BRANCH_NOT_AUTHORIZED", findings)
    gates = data.get("gates")
    guard(isinstance(gates, list) and len(gates) == 8 and len({x.get("id") for x in gates if isinstance(x, dict)}) == 8,
          "PMO_GATE_POPULATION_INVALID", findings)
    for gate in gates if isinstance(gates, list) else []:
        if not isinstance(gate, dict):
            findings.append("PMO_GATE_ROW_INVALID")
            continue
        guard(gate.get("status") == "HOLD", f"GATE_FALSE_PASS:{gate.get('id','UNKNOWN')}", findings)
    m24 = [r for r in data.get("populations", []) if r.get("population_id") == "POP-M24-HOLD"]
    guard(len(m24) == 1 and m24[0].get("approved") == 0 and m24[0].get("status") == "EXPLICIT_HOLD_NOT_COUNTED", "M24_POPULATION_RELEASED", findings)
    metrics = data.get("progress_metrics", {})
    p1 = metrics.get("p1_technical_checkpoints", {})
    guard(isinstance(p1.get("completed"), int) and isinstance(p1.get("total"), int) and 0 <= p1.get("completed", -1) <= p1.get("total", 0), "P1_PROGRESS_INVALID", findings)
    guard(metrics.get("full_project_completion", {}).get("percent") is None, "UNSUPPORTED_PROJECT_PERCENT", findings)
    guard(data.get("pmo_preservation_exception", {}).get("does_not_enable_project_execution") is True,
          "PMO_EXCEPTION_EXPANDED", findings)


def check_control_chain(pmo: dict, queue: dict, findings: list[str]) -> None:
    """Cross-artifact documentary control; does not assert remote Git/Kernel authority."""
    check_pmo(pmo, findings)
    guard(queue.get("state") == "CANDIDATE_DOCUMENTARY_QUEUE_NOT_KERNEL_ADMISSION", "QUEUE_PREMATURE_RELEASE", findings)
    guard(queue.get("baseline", {}).get("project_completion_percent") is None, "QUEUE_PROJECT_PERCENT", findings)
    guard(queue.get("baseline", {}).get("pmo_gates") == {"passed": 0, "total": 8}, "QUEUE_GATE_MISMATCH", findings)
    guard(queue.get("baseline", {}).get("m24_hold_files") == 5, "QUEUE_M24_MISMATCH", findings)
    guard(queue.get("baseline", {}).get("p1_checkpoints", {}).get("completed") == pmo.get("progress_metrics", {}).get("p1_technical_checkpoints", {}).get("completed"), "QUEUE_P1_MISMATCH", findings)
    guard(pmo.get("execution_queue_control", {}).get("task_register_source") == "CE_PMO_FILA_EXECUCAO_P1_P5_20261019_CANDIDATE.json", "QUEUE_NOT_REGISTERED", findings)
    source_ids = [x.get("source_id") for x in pmo.get("source_register", []) if isinstance(x, dict)]
    guard(len(source_ids) == len(set(source_ids)) and "S-24" in source_ids, "PMO_SOURCE_REGISTER_INVALID", findings)
    guard(set(queue.get("source_ids", [])).issubset(source_ids), "QUEUE_SOURCE_UNRESOLVED", findings)
    tasks = queue.get("tasks", [])
    guard(isinstance(tasks, list) and bool(tasks), "QUEUE_TASKS_MISSING", findings)
    if not isinstance(tasks, list):
        return
    ids = [t.get("id") for t in tasks if isinstance(t, dict)]
    guard(len(ids) == len(tasks) and len(ids) == len(set(ids)), "QUEUE_TASK_IDENTITIES_INVALID", findings)
    allowed_statuses = {"READY_NOT_STARTED", "BLOCKED_DEPENDENCY"}
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            findings.append(f"QUEUE_TASK_INVALID:{index}")
            continue
        guard(task.get("status") in allowed_statuses, f"QUEUE_FALSE_EXECUTION:{index}", findings)
        guard(task.get("mode") in {"READ_ONLY", "DOCUMENTARY"}, f"QUEUE_RUNTIME_NOT_ADMITTED:{index}", findings)
        guard(bool(task.get("evidence_required")) and bool(task.get("acceptance")) and bool(task.get("release_gate")), f"QUEUE_EVIDENCE_OR_GATE_MISSING:{index}", findings)
        guard(all(dep in ids or dep == "P1-C-C" for dep in task.get("depends_on", [])), f"QUEUE_DEPENDENCY_UNRESOLVED:{index}", findings)
    guard(queue.get("rules", {}).get("runtime_scope", "").startswith("No productive run until"), "QUEUE_RUNTIME_POLICY_MISSING", findings)


def check_publication(plan: dict, findings: list[str]) -> None:
    guard(plan.get("branch") == APPROVED_BRANCH, "UNAUTHORIZED_TARGET_BRANCH", findings)
    ops = plan.get("operations", [])
    guard(isinstance(ops, list) and bool(ops), "NO_DECLARED_OPERATIONS", findings)
    for i, op in enumerate(ops if isinstance(ops, list) else []):
        if not isinstance(op, dict):
            findings.append(f"INVALID_OPERATION:{i}")
            continue
        action = op.get("action")
        guard(action in {"create", "update"}, f"DESTRUCTIVE_OR_UNKNOWN_ACTION:{i}", findings)
        guard(action not in FORBIDDEN_OPERATIONS, f"DESTRUCTIVE_ACTION:{i}", findings)
        path = op.get("path", "")
        guard(isinstance(path, str) and path.startswith(DOC_ROOT) and ".." not in PurePosixPath(path).parts and "\\" not in path, f"OUT_OF_SCOPE_PUBLICATION:{i}", findings)
        guard(not any(part in path.lower() for part in ("private", "manifest_local", "inventory_local", "upload/", "secrets", ".env")), f"PRIVATE_PATH_PUBLICATION:{i}", findings)
        guard(op.get("sha256_local") is not None and isinstance(op.get("sha256_local"), str) and bool(SHA256.fullmatch(op["sha256_local"])), f"SOURCE_HASH_REQUIRED:{i}", findings)
        guard(op.get("readback_required") is True, f"READBACK_REQUIRED:{i}", findings)
        if action == "update":
            guard(isinstance(op.get("base_blob_sha"), str) and bool(GITSHA.fullmatch(op["base_blob_sha"])), f"CAS_BASE_SHA_REQUIRED:{i}", findings)
        if "content" in op:
            findings.append(f"INLINE_CONTENT_FORBIDDEN:{i}")


def check_zip(archive_path: Path, findings: list[str]) -> None:
    try:
        with zipfile.ZipFile(archive_path) as arc:
            for i, info in enumerate(arc.infolist()):
                name = info.filename
                normalized = name.replace("\\", "/")
                parts = PurePosixPath(normalized).parts
                if name.startswith(("/", "\\")) or ".." in parts or re.match(r"^[A-Za-z]:", name):
                    findings.append(f"ZIP_PATH_TRAVERSAL:{i}")
                mode = info.external_attr >> 16
                if stat.S_ISLNK(mode):
                    findings.append(f"ZIP_SYMLINK_ENTRY:{i}")
                # Reading central directory only: this does not certify CRC or decompression.
    except (zipfile.BadZipFile, OSError, zipfile.LargeZipFile):
        findings.append("ZIP_UNREADABLE")


def preflight(*, manifest: dict | None = None, summary: dict | None = None, pmo: dict | None = None, queue: dict | None = None, publication: dict | None = None, candidate_task: dict | None = None, history_ledger: dict | None = None, historical_index: dict | None = None, archives: list[Path] | None = None) -> list[str]:
    findings: list[str] = []
    if manifest is not None:
        check_manifest(manifest, findings)
    if summary is not None:
        check_summary(summary, findings)
    if pmo is not None and queue is not None:
        check_control_chain(pmo, queue, findings)
    elif queue is not None:
        findings.append("QUEUE_REQUIRES_MASTER_PMO")
    elif pmo is not None:
        check_pmo(pmo, findings)
    if publication is not None:
        check_publication(publication, findings)
    if candidate_task is not None or history_ledger is not None:
        if candidate_task is None or history_ledger is None or pmo is None:
            findings.append("ANTI_REWORK_REQUIRES_TASK_LEDGER_MASTER")
        else:
            answer = anti_rework_evaluate(candidate_task, history_ledger, pmo, historical_index)
            if answer["decision"] not in {"ALLOW_PREFLIGHT_ONLY", "ALLOW_REUSE_ANALYSIS_ONLY"}:
                findings.append("ANTI_REWORK_" + answer["code"])
    for archive in archives or []:
        check_zip(archive, findings)
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--pmo", type=Path)
    parser.add_argument("--queue", type=Path)
    parser.add_argument("--publication", type=Path)
    parser.add_argument("--candidate-task", type=Path)
    parser.add_argument("--history-ledger", type=Path)
    parser.add_argument("--historical-index", type=Path)
    parser.add_argument("--zip", action="append", type=Path, default=[])
    args = parser.parse_args()
    if not any((args.manifest, args.summary, args.pmo, args.queue, args.publication, args.candidate_task, args.history_ledger, args.historical_index, args.zip)):
        parser.error("specify at least one input; omitted domains are NOT evaluated")
    try:
        items = {name: json.loads(getattr(args, name).read_text(encoding="utf-8")) if getattr(args, name) else None for name in ("manifest", "summary", "pmo", "queue", "publication")}
        additions = {"candidate_task": json.loads(args.candidate_task.read_text(encoding="utf-8")) if args.candidate_task else None, "history_ledger": json.loads(args.history_ledger.read_text(encoding="utf-8")) if args.history_ledger else None, "historical_index": json.loads(args.historical_index.read_text(encoding="utf-8")) if args.historical_index else None}
        findings = preflight(**items, **additions, archives=args.zip)
    except (OSError, json.JSONDecodeError, UnicodeError, TypeError, ValueError) as exc:
        print(json.dumps({"decision": "BLOCK", "findings": [f"INPUT_READ_OR_PARSE_ERROR:{type(exc).__name__}"]}))
        return 2
    print(json.dumps({"decision": "BLOCK" if findings else "PASS_PREFLIGHT_ONLY", "findings": findings, "checked_domains": [name for name in items if items[name] is not None] + [name for name in additions if additions[name] is not None] + (["zip"] if args.zip else [])}, ensure_ascii=False, sort_keys=True))
    return 2 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
