#!/usr/bin/env python3
"""Read-only GitHub review evidence auditor; NEVER authorizes clinical release.

GitHub REST is an identity/review-state source, not a professional-credential,
regulatory-source, copyright, or Kernel-WO admission authority. No JSON field
or CI PASS can replace those independent authorities.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
API_BASE = "https://api.github.com"
MAX_REVIEW_PAGES = 20


def _review_sort_key(review: dict) -> tuple[datetime, int]:
    submitted = review.get("submitted_at")
    if not isinstance(submitted, str):
        raise ValueError("Review missing submitted_at")
    try:
        when = datetime.fromisoformat(submitted.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("Review has invalid submitted_at") from exc
    if when.tzinfo is None:
        raise ValueError("Review timestamp missing UTC offset")
    review_id = review.get("id")
    if not isinstance(review_id, int) or isinstance(review_id, bool):
        raise ValueError("Review missing numeric id")
    return when.astimezone(timezone.utc), review_id


def review_evidence(pr: dict, reviews: list[dict], *, expected_head_sha: str | None = None) -> dict[str, Any]:
    """Consider only final GitHub review events by independent accounts.

    A stale APPROVED followed by CHANGES_REQUESTED or DISMISSED is not an
    approval. Approval of previous commit does not approve the current HEAD.
    This deliberately NEVER issues clinical, normative or publication approval.
    """
    problems: set[str] = set()
    head = pr.get("head")
    sha = head.get("sha") if isinstance(head, dict) else None
    if not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
        problems.add("PR_HEAD_SHA_MISSING")
        sha = None
    if expected_head_sha is not None and sha != expected_head_sha:
        problems.add("PR_HEAD_SHA_CHANGED")
    author = pr.get("user")
    author_id = author.get("id") if isinstance(author, dict) else None
    if not isinstance(author_id, int):
        problems.add("PR_AUTHOR_ID_UNVERIFIED")
    if pr.get("draft") is True:
        problems.add("PR_DRAFT")
    if pr.get("state") != "open":
        problems.add("PR_NOT_OPEN")
    if pr.get("merged_at") is not None:
        problems.add("PR_ALREADY_MERGED")

    latest_by_user: dict[int, dict] = {}
    for rev in reviews:
        if not isinstance(rev, dict):
            problems.add("REVIEW_RECORD_MALFORMED")
            continue
        user = rev.get("user")
        reviewer_id = user.get("id") if isinstance(user, dict) else None
        reviewer_type = user.get("type") if isinstance(user, dict) else None
        state = rev.get("state")
        if not isinstance(reviewer_id, int) or isinstance(reviewer_id, bool) or not isinstance(state, str):
            problems.add("REVIEW_IDENTITY_OR_STATE_UNVERIFIED")
            continue
        if reviewer_type in {"Bot", "Organization"}:
            problems.add("NON_HUMAN_REVIEW")
            continue
        try:
            key = _review_sort_key(rev)
        except ValueError:
            problems.add("REVIEW_TIMESTAMP_UNVERIFIED")
            continue
        if key > _review_sort_key(latest_by_user[reviewer_id]) if reviewer_id in latest_by_user else True:
            latest_by_user[reviewer_id] = rev

    current_approvals = []
    for reviewer_id, review in latest_by_user.items():
        state = review["state"].upper()
        if reviewer_id == author_id:
            problems.add("AUTHOR_SELF_REVIEW")
            continue
        if state == "APPROVED":
            if review.get("commit_id") != sha or sha is None:
                problems.add("STALE_REVIEW_SHA")
                continue
            current_approvals.append(reviewer_id)
        elif state == "CHANGES_REQUESTED":
            problems.add("CHANGES_REQUESTED_ACTIVE")
        elif state == "DISMISSED":
            problems.add("REVIEW_DISMISSED")
        # COMMENTED is not approval, irrespective of text such as Reviewed-by.

    if not current_approvals:
        problems.add("NO_CURRENT_INDEPENDENT_GITHUB_APPROVAL")
    # Even a legitimate GitHub approval says nothing about nursing license,
    # professional independence, rights by operation or evidence per claim.
    problems.update({
        "PROFESSIONAL_CREDENTIAL_NOT_EXTERNALLY_VERIFIED",
        "REVIEW_SCOPE_BY_CLAIM_NOT_VERIFIED",
        "SOURCE_VERSION_AND_RIGHTS_NOT_VERIFIED",
        "KERNEL_ADMISSION_RECEIPT_NOT_VERIFIED",
        "MAIN_BRANCH_PROTECTION_NOT_VERIFIED",
    })
    return {
        "schema": "CE-G6-GITHUB-REVIEW-READONLY-1.0.0",
        "pr_number": pr.get("number"),
        "head_sha": sha,
        "expected_head_sha": expected_head_sha,
        "review_events_checked": len(reviews),
        "distinct_reviewer_accounts_seen": len(latest_by_user),
        "current_independent_github_approvals": len(current_approvals),
        "github_review_detected": bool(current_approvals),
        "clinical_approval": False,
        "normative_approval": False,
        "rights_approval": False,
        "publication_allowed": False,
        "kernel_wo_admission": False,
        "decision": "HOLD_G6_HUMAN_NORMATIVE_RIGHTS",
        "release_gate_exit_code": 2,
        "reasons": sorted(problems),
    }


def _github_get(path: str, token: str) -> dict | list:
    """GitHub API only; no redirects outside the normal API origin."""
    url = API_BASE + path
    req = Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + token,
        "User-Agent": "CE-G6-readonly-review-auditor",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urlopen(req, timeout=20) as response:
        if response.geturl().split("/")[2] != "api.github.com":
            raise ValueError("GitHub API redirect to untrusted host")
        return json.load(response)


def collect_github_reviews(repository: str, pr_number: int, token: str) -> tuple[dict, list[dict]]:
    if not REPOSITORY_RE.fullmatch(repository) or ".." in repository or not token:
        raise ValueError("Invalid repository or missing authenticated API token")
    if isinstance(pr_number, bool) or not 1 <= pr_number <= 1_000_000:
        raise ValueError("Invalid PR number")
    root = f"/repos/{repository}/pulls/{pr_number}"
    pr = _github_get(root, token)
    if not isinstance(pr, dict) or pr.get("number") != pr_number:
        raise ValueError("PR response is missing or mismatched")
    repo_data = pr.get("base", {}).get("repo")
    if not isinstance(repo_data, dict) or repo_data.get("full_name") != repository:
        raise ValueError("PR target repository mismatch")
    reviews = []
    for page in range(1, MAX_REVIEW_PAGES + 1):
        items = _github_get(root + f"/reviews?per_page=100&page={page}", token)
        if not isinstance(items, list):
            raise ValueError("Malformed review response")
        reviews.extend(items)
        if len(items) < 100:
            return pr, reviews
    raise ValueError("REVIEW_PAGINATION_LIMIT / HOLD")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Authenticated GitHub G6 review read-only audit; always HOLD")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--expected-head-sha", required=True)
    parser.add_argument("--diagnostic-only", action="store_true")
    args = parser.parse_args(argv)
    if not SHA_RE.fullmatch(args.expected_head_sha):
        print("HOLD_SOURCE:INVALID_EXPECTED_HEAD_SHA", file=sys.stderr)
        return 2
    try:
        pr, reviews = collect_github_reviews(
            args.repo, args.pr, os.environ.get("GITHUB_TOKEN", "")
        )
        report = review_evidence(pr, reviews, expected_head_sha=args.expected_head_sha)
    except (OSError, ValueError, HTTPError, URLError) as exc:
        print("HOLD_SOURCE:GITHUB_REVIEW_API_NOT_VERIFIED:" + type(exc).__name__, file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    # Explicit diagnostic mode must never issue a release decision.
    if args.diagnostic_only and report["release_gate_exit_code"] == 2 and report["head_sha"] == args.expected_head_sha:
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
