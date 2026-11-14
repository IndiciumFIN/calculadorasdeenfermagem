#!/usr/bin/env python3
"""Read-only, evidence-bound GitHub branch/PR/tree census for CE governance.

Runs inside GitHub Actions with GITHUB_TOKEN (contents:read, pull-requests:read).
Reads branch Git tree metadata, NEVER file contents or personal/source payloads.
A non-complete tree or failed API page is HOLD, not a missing/empty branch.
No issue writes, deletes, merges, state changes, or network outside GitHub API.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

VERSION = "CE-BRANCH-RECON-1.0.0"
REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
CRITICAL_PREFIXES = (
    ".github/workflows/", "contracts/", "packages/cli/", "packages/schemas/",
    "governance/", "docs/pmo/", "data/canonical/", "data/quarentena/",
    "src/", "supabase/",
)
SENSITIVE_RE = re.compile(
    r"(^|/)(\.env(\.|$)|.*(secret|credential|password|token|private[_-]?key).*)",
    re.I,
)


class CensusHold(RuntimeError):
    """Never confuse incomplete GitHub evidence with a clean audit."""


def fingerprint(changes: dict[str, tuple[str, str | None]]) -> str:
    """Stable identity of all *path + action + SHA* changes versus main."""
    data = [[path, status, blob] for path, (status, blob) in sorted(changes.items())]
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def delta(base: dict[str, str], head: dict[str, str]) -> dict[str, tuple[str, str | None]]:
    paths = base.keys() | head.keys()
    return {
        path: (
            "ADDED" if path not in base else "REMOVED" if path not in head else "MODIFIED",
            head.get(path),
        )
        for path in sorted(paths)
        if base.get(path) != head.get(path)
    }


def classify_paths(changes: dict[str, tuple[str, str | None]]) -> dict:
    affected = sorted(path for path in changes
                      if path.startswith(CRITICAL_PREFIXES))
    secret_like = sorted(path for path in changes if SENSITIVE_RE.search(path))
    return {
        "critical_path_count": len(affected),
        "critical_path_sample": affected[:50],
        "sensitive_path_count": len(secret_like),
        "sensitive_path_sample": secret_like[:25],
    }


def classify_pair(left: dict[str, tuple[str, str | None]],
                  right: dict[str, tuple[str, str | None]]) -> dict:
    lp, rp = set(left), set(right)
    shared = lp & rp
    differing = [p for p in shared if left[p] != right[p]]
    common_exact = len(shared) - len(differing)
    union = lp | rp
    return {
        "same_delta": left == right,
        "left_subset_right": bool(lp) and lp < rp
        and all(left[p] == right[p] for p in lp),
        "right_subset_left": bool(rp) and rp < lp
        and all(right[p] == left[p] for p in rp),
        "shared_paths": len(shared),
        "same_change_paths": common_exact,
        "conflicting_change_paths": len(differing),
        "conflicting_path_sample": sorted(differing)[:35],
        "jaccard_path_overlap": round(len(shared) / len(union), 4) if union else 1.0,
    }


def _url(repo: str, relative: str) -> str:
    return "https://api.github.com/repos/" + repo + "/" + relative


def api_json(repo: str, token: str, relative: str) -> object:
    if not REPO_RE.fullmatch(repo):
        raise CensusHold("Invalid repository identifier")
    if not token:
        raise CensusHold("Missing GITHUB_TOKEN: no unauthenticated fallback")
    url = _url(repo, relative)
    request = urllib.request.Request(url, headers={
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "CE-CKO-Audit-ReadOnly/1.0",
    })
    try:
        with urllib.request.urlopen(request, timeout=50) as response:
            return json.load(response)
    except (urllib.error.URLError, ValueError, TimeoutError) as exc:
        raise CensusHold("GitHub API unavailable for " + relative +
                         ": " + type(exc).__name__) from exc


def get_all(repo: str, token: str, kind: str) -> list[dict]:
    items = []
    for page in range(1, 31):
        data = api_json(repo, token, f"{kind}?per_page=100&page={page}")
        if not isinstance(data, list):
            raise CensusHold(f"Invalid GitHub {kind} response for page {page}")
        items.extend(data)
        if len(data) < 100:
            return items
    raise CensusHold(f"GitHub {kind} pagination exceeded safe bound")


def get_tree(repo: str, token: str, sha: str) -> dict[str, str]:
    data = api_json(repo, token, "git/trees/" + urllib.parse.quote(sha, safe="") + "?recursive=1")
    if not isinstance(data, dict) or data.get("truncated") is not False:
        raise CensusHold("Git tree missing/truncated at " + sha)
    records = data.get("tree")
    if not isinstance(records, list):
        raise CensusHold("Git tree entries unavailable: " + sha)
    blobs = {}
    for row in records:
        if row.get("type") != "blob":
            continue
        path, blob = row.get("path"), row.get("sha")
        if not isinstance(path, str) or not isinstance(blob, str) or not path:
            raise CensusHold("Invalid tree blob entry: " + sha)
        if path in blobs:
            raise CensusHold("Duplicate tree path: " + sha)
        blobs[path] = blob
    return blobs


def get_comparison(repo: str, token: str, mainsha: str, branchsha: str) -> dict:
    # Encoded fixed commit hashes avoid ambiguous user-supplied ref encoding.
    obj = api_json(repo, token, f"compare/{mainsha}...{branchsha}")
    if not isinstance(obj, dict) or obj.get("status") not in {
        "identical", "ahead", "behind", "diverged",
    }:
        raise CensusHold("GitHub ancestry unavailable: " + branchsha)
    return {
        "relation_to_main": obj["status"],
        "ahead_by": obj.get("ahead_by"),
        "behind_by": obj.get("behind_by"),
        "merge_base_sha": (obj.get("merge_base_commit") or {}).get("sha"),
        "compare_files_are_complete": False,  # GitHub caps the files list
    }


def scan(repo: str, token: str) -> dict:
    branches = get_all(repo, token, "branches")
    prs = get_all(repo, token, "pulls?state=open&sort=updated&direction=desc&")
    by_name = {row["name"]: row for row in branches}
    if len(branches) != len(by_name) or "main" not in by_name:
        raise CensusHold("Branch registry duplicate or missing main")
    mainsha = by_name["main"]["commit"]["sha"]
    base = get_tree(repo, token, mainsha)
    records = []
    deltas = {}
    matched_prs = defaultdict(list)
    for pr in prs:
        if pr.get("state") != "open":
            raise CensusHold("API returned non-open PR in open results")
        ref = ((pr.get("head") or {}).get("ref"))
        if ref:
            matched_prs[ref].append(pr.get("number"))
    for row in sorted(branches, key=lambda r: r["name"]):
        branch = row["name"]
        sha = row["commit"]["sha"]
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise CensusHold("Invalid Git commit SHA for branch " + branch)
        head = base if branch == "main" else get_tree(repo, token, sha)
        changed = delta(base, head)
        deltas[branch] = changed
        comparison = ({"relation_to_main": "identical",
                       "ahead_by": 0, "behind_by": 0,
                       "merge_base_sha": mainsha,
                       "compare_files_are_complete": True}
                      if branch == "main" else get_comparison(repo, token, mainsha, sha))
        kinds = Counter(status for status, _ in changed.values())
        records.append({
            "branch": branch,
            "head_sha": sha,
            "git_tree_fingerprint": fingerprint({p: ("BLOB", v) for p, v in head.items()}),
            "file_count": len(head),
            "changed_path_count": len(changed),
            "added": kinds["ADDED"], "removed": kinds["REMOVED"],
            "modified": kinds["MODIFIED"],
            "delta_sha256": fingerprint(changed),
            "changed_path_sample": sorted(changed)[:65],
            "linked_open_prs": sorted(matched_prs[branch]),
            **comparison,
            **classify_paths(changed),
        })
    same_delta = defaultdict(list)
    same_tree = defaultdict(list)
    for record in records:
        same_delta[record["delta_sha256"]].append(record["branch"])
        same_tree[record["git_tree_fingerprint"]].append(record["branch"])
    # Branches that touch identical paths but carry different blobs are
    # *not duplicates*. The report explicitly labels conflict candidates.
    cursor_names = sorted(n for n in deltas if n.startswith("cursor/"))
    similar = []
    for i, left in enumerate(cursor_names):
        for right in cursor_names[i + 1:]:
            c = classify_pair(deltas[left], deltas[right])
            if c["same_delta"] or c["left_subset_right"] or c["right_subset_left"] or (
                c["shared_paths"] >= 2 and c["jaccard_path_overlap"] >= 0.5
            ):
                similar.append({"branch_a": left, "branch_b": right, **c})
    counts = {
        "branches": len(records),
        "open_prs": len(prs),
        "cursor_branches": len(cursor_names),
        "cursor_open_prs": sum(
            str((p.get("head") or {}).get("ref", "")).startswith("cursor/")
            for p in prs),
        "changed_branches": sum(r["changed_path_count"] > 0 for r in records),
        "diverged_branches": sum(r["relation_to_main"] == "diverged" for r in records),
        "exact_duplicate_tree_groups": sum(len(v) > 1 for v in same_tree.values()),
        "exact_duplicate_delta_groups": sum(len(v) > 1 for v in same_delta.values()),
        "similar_cursor_pairs": len(similar),
        "branches_touching_sensitive_named_paths": sum(
            r["sensitive_path_count"] > 0 for r in records),
    }
    return {
        "schema_version": VERSION,
        "repository": repo,
        "base_ref": "main",
        "base_sha": mainsha,
        "scope": "READ_ONLY_TREE_METADATA",
        "promotion_allowed": False,
        "delete_allowed": False,
        "rights_verified": False,
        "clinical_review_verified": False,
        "counts": counts,
        "branches": records,
        "open_prs": [
            {
                "number": p["number"],
                "head": p.get("head", {}).get("ref"),
                "base": p.get("base", {}).get("ref"),
                "draft": p.get("draft"),
                "head_sha": p.get("head", {}).get("sha"),
            }
            for p in sorted(prs, key=lambda x: x["number"])
        ],
        "exact_tree_groups": [
            sorted(v) for v in same_tree.values() if len(v) > 1
        ],
        "exact_delta_groups": [
            sorted(v) for v in same_delta.values() if len(v) > 1
        ],
        "similar_cursor_pairs": sorted(similar, key=lambda r: (
            -r["shared_paths"], r["branch_a"], r["branch_b"])),
        "findings": [
            "Tree identity or diff equivalence is not normative or clinical approval",
            "A path collision can contain incompatible logic and requires human diff review",
            "Only GitHub tree metadata inspected; rights and content still require source checks",
            "GitHub comparison files may be limited; full tree diff computed independently",
            "No branch or PR can be deleted or merged from this artifact",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    repo, token = os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("GITHUB_TOKEN", "")
    try:
        catalog = scan(repo, token)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except CensusHold as exc:
        print("HOLD_INCOMPLETE_EVIDENCE:", str(exc), file=sys.stderr)
        return 2
    print(json.dumps(catalog["counts"], ensure_ascii=False, indent=2))
    print("READ_ONLY_CENSUS_PASS / NO_BRANCH_MUTATION / NO_CLINICAL_RELEASE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
