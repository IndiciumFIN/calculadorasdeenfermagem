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
    historical_label = data.get("activity_authorization", {}).get("m24_historical_label_disposition", "")
    guard(historical_label.startswith("CLOSED_ADMINISTRATIVE_UNRECONSTRUCTIBLE_HISTORY") and "FIVE_UNKNOWN_MEMBERS_STAY_UNPROCESSED_AND_UNAPPROVED" in historical_label,
          "M24_ADMIN_CLOSURE_MISREPRESENTED", findings)
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
    guard(queue.get("rules", {}).get("m24_historical_milestone_disposition", "").startswith("CLOSED_ADMINISTRATIVE_UNRECONSTRUCTIBLE_HISTORY"),
          "QUEUE_M24_HISTORIC_LABEL_REOPENED", findings)
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
    original_order = ["P1-CD-01", "P1-D-01", "P2-00", "P2-01", "P3-A", "P3-B", "P4-A", "P4-D", "P4-F", "P5-01", "P5-02"]
    guard(ids[:len(original_order)] == original_order, "QUEUE_HISTORICAL_TASK_ORDER_CHANGED", findings)
    discoveries = tasks[len(original_order):]
    find_map = {f.get("id"): f for f in queue.get("finds", []) if isinstance(f, dict)}
    guard(len(find_map) == len(queue.get("finds", [])), "QUEUE_FIND_ID_COLLISION", findings)
    for offset, task in enumerate(discoveries, 1):
        if not isinstance(task, dict):
            findings.append(f"POST_CLOSURE_TASK_INVALID:{offset}")
            continue
        fid = task.get("origin_find_id")
        f = find_map.get(fid, {})
        guard(task.get("id", "").startswith("POST-") and task.get("wave") == "POST_CLOSURE_BEFORE_HOMOLOGATION" and task.get("enqueue_position") == "TAIL" and task.get("execution_order") == offset,
              f"POST_CLOSURE_NOT_APPENDED_AT_TAIL:{offset}", findings)
        guard(task.get("discovered_after_closure") is True and bool(task.get("prior_closed_reference")) and bool(task.get("investigation")) and bool(task.get("root_cause")) and bool(task.get("correction")) and bool(task.get("source_refs")),
              f"POST_CLOSURE_FIND_INVESTIGATION_CORRECTION_REQUIRED:{offset}", findings)
        guard(f.get("type") == "POST_CLOSURE_FIND" and f.get("owner_task") == task.get("id") and bool(f.get("investigation")) and bool(f.get("root_cause")) and bool(f.get("correction")),
              f"POST_CLOSURE_LINKED_FIND_REQUIRED:{offset}", findings)
        guard(task.get("status") in {"READY_NOT_STARTED", "BLOCKED_DEPENDENCY", "HOLD_INVESTIGATION"},
              f"POST_CLOSURE_FALSE_COMPLETION:{offset}", findings)
    guard(queue.get("rules", {}).get("post_closure_discovery_invariant", "").startswith("INV-QUEUE-POST-CLOSURE-001") and queue.get("rules", {}).get("final_homologation", "").startswith("OUTSIDE_EXECUTION_QUEUE"),
          "POST_CLOSURE_QUEUE_POLICY_MISSING", findings)
    control = pmo.get("post_closure_control", {})
    guard(control.get("invariant_id") == "INV-QUEUE-POST-CLOSURE-001" and control.get("original_order_immutable") is True and control.get("final_homologation_outside_queue") is True and control.get("final_user_approval_pending") is True and control.get("new_tasks_not_automatically_admitted") is True,
          "POST_CLOSURE_MASTER_POLICY_MISSING", findings)
    guard(control.get("new_tasks_current_tail") == [t.get("id") for t in discoveries if isinstance(t, dict)], "POST_CLOSURE_MASTER_QUEUE_DIVERGENCE", findings)
    allowed_statuses = {"READY_NOT_STARTED", "BLOCKED_DEPENDENCY", "EVIDENCE_PARTIAL_RUNTIME_HOLD", "HOLD_INVESTIGATION"}
    historical_evidence_partial = {"P2-00", "P3-A", "P4-A"}
    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            findings.append(f"QUEUE_TASK_INVALID:{index}")
            continue
        guard(task.get("status") in allowed_statuses, f"QUEUE_FALSE_EXECUTION:{index}", findings)
        if task.get("id") in historical_evidence_partial:
            guard(task.get("status") == "EVIDENCE_PARTIAL_RUNTIME_HOLD", f"QUEUE_STALE_EVIDENCED_STATUS:{task.get('id')}", findings)
        guard(task.get("mode") in {"READ_ONLY", "DOCUMENTARY"}, f"QUEUE_RUNTIME_NOT_ADMITTED:{index}", findings)
        guard(bool(task.get("evidence_required")) and bool(task.get("acceptance")) and bool(task.get("release_gate")), f"QUEUE_EVIDENCE_OR_GATE_MISSING:{index}", findings)
        guard(all(dep in ids or dep == "P1-C-C" for dep in task.get("depends_on", [])), f"QUEUE_DEPENDENCY_UNRESOLVED:{index}", findings)
    guard(queue.get("rules", {}).get("runtime_scope", "").startswith("No productive run until"), "QUEUE_RUNTIME_POLICY_MISSING", findings)
    wo = [p for p in pmo.get("populations", []) if p.get("population_id") == "POP-PR2-WO"]
    guard(len(wo) == 1 and wo[0].get("count") == 164 and wo[0].get("approved") is None, "PR2_WO_POPULATION_NOT_164_HOLD", findings)
    p3 = [t for t in tasks if isinstance(t, dict) and t.get("id") == "P3-A"]
    guard(len(p3) == 1 and "164 PR2 WOs" in p3[0].get("action", "") and "38-to-164-to-102" in p3[0].get("acceptance", ""), "QUEUE_STALE_WO_COUNT", findings)


def check_parallel_controls(pmo: dict, queue: dict, dispatch: dict, findings: list[str]) -> None:
    """Cross-wave evidence references; no claim of Kernel or server-side enforcement."""
    check_control_chain(pmo, queue, findings)
    guard(dispatch.get("kind") == "PARALLEL_DOCUMENTARY_EVIDENCE_LINKAGE_REGISTER", "DISPATCH_IDENTITY_INVALID", findings)
    guard(dispatch.get("status") == "DOCUMENTARY_START_NOT_EXECUTION_COMPLETION", "DISPATCH_FALSE_COMPLETION", findings)
    controls = dispatch.get("cross_wave_controls", {})
    guard(controls.get("pmo_trusted") is False and controls.get("all_4_waves_productive_execution_admitted") is False and controls.get("project_completion_percent") is None and controls.get("m24") == "HOLD", "DISPATCH_FALSE_RELEASE", findings)
    known = {entry.get("source_id") for entry in pmo.get("source_register", []) if isinstance(entry, dict)}
    entries = dispatch.get("entries", [])
    guard(isinstance(entries, list) and len(entries) == 4, "DISPATCH_FOUR_WAVE_ENTRIES_REQUIRED", findings)
    if not isinstance(entries, list):
        return
    waves = [e.get("wave") for e in entries if isinstance(e, dict)]
    guard(sorted(waves) == ["P2", "P3", "P4", "P5"], "DISPATCH_WAVE_COVERAGE_INVALID", findings)
    for i, entry in enumerate(entries):
        if not isinstance(entry, dict):
            findings.append(f"DISPATCH_INVALID_ENTRY:{i}")
            continue
        refs = entry.get("source_ids", [])
        link_refs = [l.get("source_id") for l in entry.get("evidence_linkage", []) if isinstance(l, dict)]
        guard(bool(refs) and set(refs).issubset(known) and set(refs) == set(link_refs), f"DISPATCH_SOURCE_MISMATCH:{i}", findings)
        guard(entry.get("status", "").startswith("EVIDENCE_LINKED_") and bool(entry.get("release_blocker")), f"DISPATCH_ENTRY_FALSE_RELEASE:{i}", findings)
    plans = {p.get("wave"): p for p in pmo.get("parallel_wave_plans", []) if isinstance(p, dict)}
    guard(all(plans.get(w, {}).get("plan_state") == "DOCUMENTARY_EXISTING_EVIDENCE_LINKED" and "S-35" in plans.get(w, {}).get("source_ids", []) for w in ("P2", "P3", "P4", "P5")), "DISPATCH_PMO_PLANS_DIVERGE", findings)


def check_parallel_anti_rework(pmo: dict, dispatch: dict, history_ledger: dict, findings: list[str]) -> None:
    """Each wave receives a separate fail-closed semantic admission to link old evidence."""
    rows = history_ledger.get("tasks", []) if isinstance(history_ledger, dict) else []
    if not rows or not isinstance(rows[0], dict):
        findings.append("DISPATCH_ANTI_REWORK_HISTORY_UNAVAILABLE")
        return
    baseline = rows[0]
    for entry in dispatch.get("entries", []):
        if not isinstance(entry, dict):
            continue
        candidate = dict(baseline)
        candidate.update(
            task_id=entry.get("task_id"), intent="Link existing evidence for " + str(entry.get("wave")),
            operation_kind="EVIDENCE_LINK_ONLY", mode="READ_ONLY",
            target_artifact="EVIDENCE_CROSSWALK_ONLY_" + str(entry.get("wave")),
            intended_outputs=["EVIDENCE_CROSSWALK_ONLY"],
            source_ids=entry.get("source_ids"), prior_evidence_ids=entry.get("source_ids"),
            evidence_of_new_scope="REUSE_ONLY_EXISTING_EVIDENCE",
            parameters={"no_source_reprocessing": True, "no_remote_writes": True},
        )
        result = anti_rework_evaluate(candidate, history_ledger, pmo)
        guard(result.get("decision") == "ALLOW_REUSE_ANALYSIS_ONLY", "DISPATCH_ANTI_REWORK_" + str(entry.get("wave")) + ":" + str(result.get("code")), findings)


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


def preflight(*, manifest: dict | None = None, summary: dict | None = None, pmo: dict | None = None, queue: dict | None = None, dispatch: dict | None = None, publication: dict | None = None, candidate_task: dict | None = None, history_ledger: dict | None = None, historical_index: dict | None = None, archives: list[Path] | None = None) -> list[str]:
    findings: list[str] = []
    if manifest is not None:
        check_manifest(manifest, findings)
    if summary is not None:
        check_summary(summary, findings)
    if dispatch is not None:
        if pmo is None or queue is None:
            findings.append("DISPATCH_REQUIRES_MASTER_QUEUE")
        else:
            check_parallel_controls(pmo, queue, dispatch, findings)
            if history_ledger is not None:
                check_parallel_anti_rework(pmo, dispatch, history_ledger, findings)
    elif pmo is not None and queue is not None:
        check_control_chain(pmo, queue, findings)
    elif queue is not None:
        findings.append("QUEUE_REQUIRES_MASTER_PMO")
    elif pmo is not None:
        check_pmo(pmo, findings)
    if publication is not None:
        check_publication(publication, findings)
    if candidate_task is not None or (history_ledger is not None and dispatch is None):
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
    parser.add_argument("--dispatch", type=Path)
    parser.add_argument("--publication", type=Path)
    parser.add_argument("--candidate-task", type=Path)
    parser.add_argument("--history-ledger", type=Path)
    parser.add_argument("--historical-index", type=Path)
    parser.add_argument("--zip", action="append", type=Path, default=[])
    args = parser.parse_args()
    if not any((args.manifest, args.summary, args.pmo, args.queue, args.dispatch, args.publication, args.candidate_task, args.history_ledger, args.historical_index, args.zip)):
        parser.error("specify at least one input; omitted domains are NOT evaluated")
    try:
        items = {name: json.loads(getattr(args, name).read_text(encoding="utf-8")) if getattr(args, name) else None for name in ("manifest", "summary", "pmo", "queue", "dispatch", "publication")}
        additions = {"candidate_task": json.loads(args.candidate_task.read_text(encoding="utf-8")) if args.candidate_task else None, "history_ledger": json.loads(args.history_ledger.read_text(encoding="utf-8")) if args.history_ledger else None, "historical_index": json.loads(args.historical_index.read_text(encoding="utf-8")) if args.historical_index else None}
        findings = preflight(**items, **additions, archives=args.zip)
    except (OSError, json.JSONDecodeError, UnicodeError, TypeError, ValueError) as exc:
        print(json.dumps({"decision": "BLOCK", "findings": [f"INPUT_READ_OR_PARSE_ERROR:{type(exc).__name__}"]}))
        return 2
    print(json.dumps({"decision": "BLOCK" if findings else "PASS_PREFLIGHT_ONLY", "findings": findings, "checked_domains": [name for name in items if items[name] is not None] + [name for name in additions if additions[name] is not None] + (["zip"] if args.zip else [])}, ensure_ascii=False, sort_keys=True))
    return 2 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
