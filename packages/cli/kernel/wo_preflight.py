"""Read-only WO preflight: candidate documents are NEVER Kernel admission.

This reconciles the competing historical implementations without importing their
implicit permissions. Only exact typed relationships are checked. A successful
technical preflight is still HOLD until an independently verified admission
receipt bound to a Git blob exists; this module has no such trust authority.

No network, credential reading, file writes, Drive download, or publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

POLICY_ID = re.compile(r"^KERNEL-POLICY-[0-9]{3,5}$")
FOLDER_ID = re.compile(r"^[A-Za-z0-9_-]{16,80}$")
ACTIVITIES = frozenset({"obter", "atomizar"})
ROOTS_PATH = Path("config/drive_inventory_roots_20261016.json")
POLICY_DIR = Path("contracts/policies")


def git_blob_sha1(data: bytes) -> str:
    """Git's real blob object identity, independent of local commit metadata."""
    return hashlib.sha1(
        b"blob " + str(len(data)).encode("ascii") + b"\x00" + data
    ).hexdigest()


def _read_json(root: Path, relative: Path, findings: set[str], kind: str) -> tuple[dict, str | None]:
    """Fail closed on path escape, symlinks, missing files and malformed JSON."""
    if relative.is_absolute() or ".." in relative.parts:
        findings.add(kind + "_UNSAFE_PATH")
        return {}, None
    candidate = root / relative
    try:
        if candidate.is_symlink() or not candidate.resolve().is_relative_to(root.resolve()):
            findings.add(kind + "_UNSAFE_PATH")
            return {}, None
        raw = candidate.read_bytes()
        obj = json.loads(raw)
        if not isinstance(obj, dict):
            findings.add(kind + "_INVALID_JSON_OBJECT")
            return {}, None
        return obj, git_blob_sha1(raw)
    except (OSError, UnicodeError, ValueError, TypeError):
        findings.add(kind + "_MISSING_OR_INVALID")
        return {}, None


def preflight(
    repo_root: Path, wo_path: Path, *,
    folder_id: str, activity: str, policy_id: str,
) -> dict[str, Any]:
    """Evaluate structured evidence and emit a non-authorizing HOLD report.

    Passing typed structural conditions cannot turn this into an authorization.
    A future admission service requires a *separate*, external trust mechanism.
    """
    root = Path(repo_root).resolve()
    findings: set[str] = set()
    if not FOLDER_ID.fullmatch(folder_id):
        findings.add("INVALID_FOLDER_ID")
    if activity not in ACTIVITIES:
        findings.add("UNKNOWN_ACTIVITY")
    if not POLICY_ID.fullmatch(policy_id):
        findings.add("INVALID_POLICY_ID")
        policy_rel = Path("contracts/policies/_invalid.json")
    else:
        policy_rel = POLICY_DIR / (policy_id + ".json")

    roots, roots_sha = _read_json(root, ROOTS_PATH, findings, "ROOTS")
    policy, policy_sha = _read_json(root, policy_rel, findings, "POLICY")
    wo, wo_sha = _read_json(root, Path(wo_path), findings, "WO")

    if roots.get("scope") != "registered_roots_metadata_only":
        findings.add("ROOTS_UNKNOWN_SCOPE")
    registered = {
        row.get("id") for row in roots.get("roots", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    } if isinstance(roots.get("roots"), list) else set()
    if folder_id not in registered:
        findings.add("ROOT_NOT_REGISTERED")

    # This root contract is metadata-only: it never authorizes byte retrieval
    # nor conversion of any item into a canonical clinical atom.
    if roots.get("scope") == "registered_roots_metadata_only":
        findings.add("SCOPE_METADATA_ONLY_NO_BYTES")
    if not isinstance(roots.get("restrictions"), list) or "NO_CANONICAL_PROMOTION" not in roots["restrictions"]:
        findings.add("ROOTS_RESTRICTIONS_INCOMPLETE")

    if policy.get("id") != policy_id:
        findings.add("POLICY_ID_MISMATCH")
    policy_folders = policy.get("drive_folder_ids")
    exact_binding = (
        policy.get("drive_folder_id") == folder_id
        or (isinstance(policy_folders, list) and folder_id in policy_folders)
    )
    if not exact_binding:
        findings.add("NO_EXPLICIT_POLICY_FOLDER_BINDING")
    if policy.get("fail_closed") is not True:
        findings.add("POLICY_NOT_FAIL_CLOSED")
    if policy.get("wo_required") is not True:
        findings.add("POLICY_WO_NOT_REQUIRED")
    if policy.get("requires_human_review") is not True:
        findings.add("POLICY_REVIEW_NOT_REQUIRED")

    # Legacy WO text is never searched: "description": "folderId" and a
    # filename mentioning the folder are NOT structured authorization.
    if wo.get("folder_id") != folder_id:
        findings.add("WO_FOLDER_NOT_BOUND")
    activities = wo.get("activities")
    exact_activity = (
        wo.get("tarefa") == activity
        or (isinstance(activities, list) and activity in activities)
    )
    if not exact_activity:
        findings.add("WO_ACTIVITY_NOT_BOUND")
    if wo.get("policy_id") != policy_id:
        findings.add("WO_POLICY_NOT_BOUND")
    if not isinstance(wo.get("id") or wo.get("wo_id"), str):
        findings.add("WO_ID_MISSING")
    if not isinstance(wo.get("task_id"), str) or not wo["task_id"].strip():
        findings.add("WO_TASK_NOT_BOUND")
    if not isinstance(wo.get("find_ids"), list) or not wo["find_ids"]:
        findings.add("WO_FIND_SCOPE_MISSING")

    if wo.get("status") in {"PREAUTHORIZED", "AUTHORIZED", "APPROVED", "ADMITTED"}:
        findings.add("WO_SELF_ASSERTED_AUTHORIZATION")
    if wo.get("authorized_by") or wo.get("reviewed_by") or wo.get("approval_receipt"):
        findings.add("WO_SELF_ASSERTED_REVIEW_UNTRUSTED")
    if wo.get("bytes_acquired") is True or wo.get("atoms_emitted", 0):
        findings.add("WO_CLAIMS_EXECUTION_WITHOUT_ADMISSION")

    # This preflight has deliberately no mechanism to produce a trusted receipt.
    # Git-hash checks bind bytes but neither prove human identity nor rights.
    findings.add("INDEPENDENT_KERNEL_ADMISSION_NOT_VERIFIED")
    findings.add("G6_CLINICAL_REVIEW_NOT_VERIFIED")
    return {
        "schema": "CE-WO-G6-PREFLIGHT-1.0.0",
        "status": "HOLD",
        "exit_code": 2,
        "activity": activity,
        "folder_id": folder_id,
        "policy_id": policy_id,
        "object_git_blob_shas": {
            "roots": roots_sha,
            "policy": policy_sha,
            "wo": wo_sha,
        },
        "technically_complete": not any(
            x for x in findings if x not in {
                "INDEPENDENT_KERNEL_ADMISSION_NOT_VERIFIED",
                "G6_CLINICAL_REVIEW_NOT_VERIFIED",
                "SCOPE_METADATA_ONLY_NO_BYTES",
            }
        ),
        "trusted_kernel_receipt": None,
        "clinical_approval": False,
        "bytes_acquired": False,
        "atoms_published": 0,
        "network_used": False,
        "findings": sorted(findings),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="CE WO G6 preflight, always HOLD until independently admitted")
    p.add_argument("--repo-root", type=Path, default=Path.cwd())
    p.add_argument("--wo", type=Path, required=True, help="WO JSON relative to --repo-root")
    p.add_argument("--folder-id", required=True)
    p.add_argument("--activity", required=True)
    p.add_argument("--policy", required=True)
    args = p.parse_args(argv)
    result = preflight(args.repo_root, args.wo, folder_id=args.folder_id,
                       activity=args.activity, policy_id=args.policy)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 2


if __name__ == "__main__":
    sys.exit(main())
