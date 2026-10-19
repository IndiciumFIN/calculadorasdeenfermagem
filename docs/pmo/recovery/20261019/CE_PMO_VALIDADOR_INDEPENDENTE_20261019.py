#!/usr/bin/env python3
"""Independent read-only PMO candidate verifier; never writes, never certifies itself."""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent
REGISTER = BASE / "CE_PMO_REGISTRO_MESTRE_20261019_v0.1.0_CANDIDATE.json"
SUMMARY = BASE / "CE_PMO_INVENTARIO_RECURSIVO_RESUMO_20261019_CANDIDATE.json"
COLLECTOR = BASE / "ce_pmo_inventory_recursive_v02.py"


def report(condition: bool, code: str, description: str, severity: str = "BLOCK") -> dict:
    return {"code": code, "severity": "PASS" if condition else severity, "description": description}


def verify(rescan: bool = False) -> list[dict]:
    checks = []
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    population = {entry["population_id"]: entry for entry in register["populations"]}
    source = {entry["source_id"]: entry for entry in register["source_register"]}
    gates = {entry["id"]: entry for entry in register["gates"]}

    checks.append(report(register["pmo_trusted"] is False and register["project_execution_allowed"] is False, "VAL-001", "candidate is not certified as trusted/executable"))
    checks.append(report(len(gates) == 8 and all(g["status"] == "HOLD" for g in gates.values()), "VAL-002", "all eight independent PMO gates explicitly held"))
    checks.append(report(len(population) == len(register["populations"]) and len(source) == len(register["source_register"]), "VAL-003", "unique population and evidence IDs"))
    checks.append(report(all(set(p["source_ids"]).issubset(source) for p in register["populations"]), "VAL-004", "population source references resolvable"))
    checks.append(report(all(set(w["source_ids"]).issubset(source) for w in register["workstreams"]), "VAL-005", "workstream source references resolvable"))
    checks.append(report(population["POP-LOCAL-RECURSIVE-REGULAR"]["count"] == summary["file_count"], "VAL-006", "local population matches aggregate snapshot"))
    checks.append(report(sum(group["files"] for group in summary["groups"].values()) == summary["file_count"], "VAL-007", "group file totals match"))
    checks.append(report(sum(group["bytes"] for group in summary["groups"].values()) == summary["bytes_total"], "VAL-008", "group byte totals match"))
    checks.append(report(summary["file_count"] >= summary["unique_file_sha256"] and summary["file_count"]-summary["unique_file_sha256"] == summary["files_in_duplicate_groups"]-summary["exact_duplicate_hash_groups"], "VAL-009", "duplicate group cardinality reconciles"))
    checks.append(report(summary["privacy"] == "AGGREGATE_ONLY_NO_FILENAMES_OR_HASHES" and "files" not in summary and "zip_containers" not in summary, "VAL-010", "public summary excludes item-level names and hashes"))
    checks.append(report(summary["pmo_gate"] == "HOLD" and population["POP-LOCAL-RECURSIVE-REGULAR"]["approved"] == 0, "VAL-011", "hashed local count is not mistaken for accepted files"))
    checks.append(report("M24_HOLD" in register["scope_restrictions"] and population["POP-M24-HOLD"]["count"] == 5 and population["POP-M24-HOLD"]["approved"] == 0, "VAL-012", "five M24 items remain explicitly blocked"))
    checks.append(report(register["pmo_preservation_exception"]["allowed_target_branch"] == register["preservation_readback"]["branch"] and "NO_REMOTE_MUTATIONS_EXCEPT_PMO_DOCUMENTARY_BRANCH" in register["scope_restrictions"], "VAL-013", "documentary exception branch and restrictions consistent"))
    checks.append(report(all(p.get("processed") is None or (0 <= p["processed"] <= p["count"]) for p in register["populations"]), "VAL-014", "processed population counts bounded"))
    checks.append(report(all(p.get("approved") is None or (0 <= p["approved"] <= p["count"]) for p in register["populations"]), "VAL-015", "approved population counts bounded"))
    checks.append(report(not any(p.get("approved", 0) not in (None, 0) for p in register["populations"]), "VAL-016", "no unexplained approvals declared"))
    checks.append(report("NO_MERGE" in register["scope_restrictions"] and register["preservation_readback"]["main_mutated"] is False, "VAL-017", "main mutation not represented as authorized"))

    # These are design gaps, not automatic logical contradictions. They prevent
    # asserting independently audited completeness even when static checks pass.
    checks.append(report(False, "VAL-GAP-001", "register embeds its own older commit/readback and lacks a current independent receipt", "HOLD"))
    checks.append(report(False, "VAL-GAP-002", "aggregate snapshot lacks timestamp/scan-id and an independently retained detailed manifest for full byte replay", "HOLD"))
    checks.append(report(False, "VAL-GAP-003", "ZIP central-directory enumeration does not validate every member CRC/content or reject unsafe paths", "HOLD"))
    checks.append(report(False, "VAL-GAP-004", "local filesystem enumeration is not evidence of complete GitHub/Library/Supabase reconciliation", "HOLD"))

    if rescan:
        spec = importlib.util.spec_from_file_location("collector_v02", COLLECTOR)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        _, fresh = module.inventory(module.DEFAULT_MANIFEST, module.DEFAULT_SUMMARY)
        comparables = ["file_count", "bytes_total", "symlink_count_skipped", "groups", "unique_file_sha256", "exact_duplicate_hash_groups", "files_in_duplicate_groups", "zip_count", "zip_invalid_or_unreadable", "zip_regular_entries_declared"]
        diff = [key for key in comparables if summary[key] != fresh[key]]
        checks.append(report(not diff, "VAL-RESCAN-001", "snapshot matches fresh recursive read-only scan; differing fields="+repr(diff), "HOLD"))
    return checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rescan", action="store_true", help="recompute file hashes from workspace; no writes")
    opts = parser.parse_args()
    results = verify(opts.rescan)
    print(json.dumps({"checks": results, "count": Counter(x["severity"] for x in results), "release_decision": "HOLD_NOT_CERTIFIED"}, ensure_ascii=False, indent=2))
    if any(item["severity"] == "BLOCK" for item in results):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
