#!/usr/bin/env python3
"""CE local assurance CLI. Standard library only; does not write or grant authority."""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import sys

EXIT_PASS, EXIT_FAIL, EXIT_HOLD = 0, 2, 78
PROCESSES = {"PMO", "P1", "P2", "P3", "P4", "P5"}
STAGES = {"LOCAL_CANDIDATE", "PRODUCTIVE"}
REQUIRED = {"process", "agent_id", "task_id", "snapshot", "artifacts",
            "expected_paths", "producer_id", "auditor_id", "stage"}
SENSITIVE = {"password", "secret", "api_key", "private_key", "token"}

def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()

def _within(root: pathlib.Path, rel: str):
    if not isinstance(rel, str) or not rel or pathlib.PurePosixPath(rel).is_absolute():
        raise ValueError("PATH_INVALID")
    parts = pathlib.PurePosixPath(rel).parts
    if any(p in (".", "..") for p in parts) or "\\" in rel:
        raise ValueError("PATH_TRAVERSAL")
    target = root.joinpath(*parts)
    if target.is_symlink() or not target.resolve().is_relative_to(root.resolve()):
        raise ValueError("PATH_OUTSIDE_ROOT")
    return target

def validate_catalog(catalog: dict):
    errors = []
    agents = catalog.get("agents")
    if not isinstance(agents, list) or not agents:
        return ["EMPTY_CATALOG"]
    seen = set()
    for a in agents:
        if not isinstance(a, dict):
            errors.append("AGENT_NOT_OBJECT")
            continue
        aid = a.get("agent_id")
        if not isinstance(aid, str) or not aid.strip():
            errors.append("MISSING_AGENT_ID")
        elif aid in seen:
            errors.append("DUPLICATE_AGENT_ID:" + aid)
        seen.add(aid)
        if a.get("wave") not in PROCESSES:
            errors.append("UNKNOWN_PROCESS:" + str(aid))
        if a.get("deployment_state") == "DEPLOYED" and not a.get("kernel_receipt_ref"):
            errors.append("FALSE_DEPLOYMENT:" + str(aid))
    return sorted(set(errors))

def evaluate(manifest: dict, catalog: dict, root: pathlib.Path):
    failures, holds = [], []
    if not isinstance(manifest, dict):
        return {"decision":"FAIL", "failures":["MANIFEST_NOT_OBJECT"],"holds":[]}
    failures.extend("MISSING_FIELD:" + k for k in sorted(REQUIRED - manifest.keys()))
    failures.extend(validate_catalog(catalog))
    agent_index = {a.get("agent_id"): a for a in catalog.get("agents", []) if isinstance(a,dict)}
    if manifest.get("process") not in PROCESSES:
        failures.append("UNKNOWN_PROCESS")
    agent = agent_index.get(manifest.get("agent_id"))
    if not agent or agent.get("wave") != manifest.get("process"):
        failures.append("UNREGISTERED_OR_WRONG_PROCESS_AGENT")
    if manifest.get("producer_id") == manifest.get("auditor_id"):
        failures.append("SELF_AUDIT_FORBIDDEN")
    stage = manifest.get("stage")
    if stage not in STAGES:
        failures.append("UNKNOWN_STAGE")
    if stage == "PRODUCTIVE":
        receipt = manifest.get("kernel_receipt")
        if not isinstance(receipt, dict) or receipt.get("status") != "ADMITTED" or not receipt.get("wo_sha256") or not receipt.get("policy_sha256"):
            failures.append("KERNEL_RECEIPT_REQUIRED")
        else:
            holds.append("KERNEL_RECEIPT_SIGNATURE_NOT_EXTERNALLY_VERIFIED")
    snapshot = manifest.get("snapshot")
    if not isinstance(snapshot, dict) or not snapshot.get("git_commit_sha") or len(str(snapshot.get("git_commit_sha",""))) != 40:
        failures.append("UNPINNED_SNAPSHOT")
    artifacts = manifest.get("artifacts")
    expected = manifest.get("expected_paths")
    if not isinstance(artifacts,list) or not isinstance(expected,list):
        failures.append("ARTIFACT_COLLECTION_INVALID")
        artifacts, expected = [], []
    actual_paths = [a.get("path") for a in artifacts if isinstance(a,dict)]
    if len(actual_paths) != len(artifacts) or len(actual_paths) != len(set(actual_paths)):
        failures.append("DUPLICATE_OR_INVALID_PATHS")
    if set(actual_paths) != set(expected) or len(expected) != len(set(expected)):
        failures.append("COMPLETENESS_MISMATCH")
    for a in artifacts:
        if not isinstance(a,dict):
            continue
        p = a.get("path","")
        try:
            fp = _within(root,p)
            if not fp.is_file():
                failures.append("MISSING_BYTES:" + str(p))
                continue
            payload = fp.read_bytes()
            if sha256(payload) != a.get("sha256"):
                failures.append("HASH_MISMATCH:" + p)
            if len(payload) != a.get("byte_length"):
                failures.append("LENGTH_MISMATCH:" + p)
        except (ValueError, OSError) as exc:
            failures.append(str(exc) + ":" + str(p))
    if manifest.get("rights") not in ("AUTHORIZED", "NOT_APPLICABLE"):
        holds.append("RIGHTS_UNVERIFIED")
    if manifest.get("clinical_review_required") and manifest.get("clinical_review_status") != "APPROVED_BY_QUALIFIED_HUMAN":
        holds.append("CLINICAL_REVIEW_REQUIRED")
    if manifest.get("semantic_precision_claimed") and not manifest.get("independent_semantic_evidence"):
        failures.append("UNSUPPORTED_SEMANTIC_PRECISION_CLAIM")
    if manifest.get("secrets_screened") is not True:
        holds.append("SECRETS_SCREEN_PENDING")
    for k in manifest:
        if k.lower() in SENSITIVE:
            failures.append("SECRET_FIELD_FORBIDDEN:" + k)
    decision = "FAIL" if failures else "HOLD" if holds else "PASS_BOUNDED"
    return {"decision":decision,"failures":sorted(set(failures)),
            "holds":sorted(set(holds)), "artifacts_verified":len(artifacts),
            "scope":"LOCAL_INTEGRITY_AND_MANIFEST_COMPLETENESS_ONLY",
            "kernel_admitted":False,"semantically_validated":False}

def main(argv=None):
    ap = argparse.ArgumentParser(description="CE deterministic local assurance; no writes")
    sub = ap.add_subparsers(dest="command",required=True)
    p = sub.add_parser("audit")
    p.add_argument("--manifest",required=True)
    p.add_argument("--catalog",required=True)
    p.add_argument("--root",required=True)
    c = sub.add_parser("catalog-check")
    c.add_argument("--catalog",required=True)
    args = ap.parse_args(argv)
    try:
        catalog = json.loads(pathlib.Path(args.catalog).read_text(encoding="utf-8"))
        if args.command == "catalog-check":
            errors = validate_catalog(catalog)
            result = {"decision":"FAIL" if errors else "PASS_BOUNDED","errors":errors,
                      "count":len(catalog.get("agents",[]))}
        else:
            manifest = json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
            result = evaluate(manifest,catalog,pathlib.Path(args.root))
    except (OSError, ValueError, TypeError) as exc:
        result = {"decision":"FAIL","failures":["INPUT_ERROR:"+type(exc).__name__]}
    print(json.dumps(result,sort_keys=True,ensure_ascii=False))
    return {"PASS_BOUNDED":EXIT_PASS,"HOLD":EXIT_HOLD}.get(result["decision"],EXIT_FAIL)

if __name__ == "__main__":
    sys.exit(main())
