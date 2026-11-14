"""Adversarial review-state tests: no GitHub approval can authorize clinical G6."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from scripts.cko_g6_github_reviews import (
    collect_github_reviews, review_evidence, _review_sort_key,
)

HEAD = "a" * 40
OLD = "b" * 40
REPO = "IndiciumFIN/calculadorasdeenfermagem"


def fixture_pr(sha=HEAD, draft=False):
    return {
        "number": 57, "state": "open", "draft": draft,
        "merged_at": None,
        "head": {"sha": sha},
        "base": {"repo": {"full_name": REPO}},
        "user": {"id": 100, "login": "author", "type": "User"},
    }


def review(user_id=200, state="APPROVED", commit_id=HEAD, *,
           submitted_at="2026-11-14T13:00:00Z", review_id=1, user_type="User"):
    return {
        "id": review_id,
        "state": state,
        "commit_id": commit_id,
        "submitted_at": submitted_at,
        "user": {"id": user_id, "login": f"reviewer-{user_id}", "type": user_type},
    }


class GithubG6ReviewSafetyTests(unittest.TestCase):
    def scan(self, reviews=(), pr=None, expected=HEAD):
        return review_evidence(
            fixture_pr() if pr is None else pr,
            list(reviews), expected_head_sha=expected,
        )

    def test_empty_review_list_always_holds(self):
        x = self.scan()
        self.assertEqual(x["current_independent_github_approvals"], 0)
        self.assertIn("NO_CURRENT_INDEPENDENT_GITHUB_APPROVAL", x["reasons"])
        self.assertEqual(x["release_gate_exit_code"], 2)
        self.assertFalse(x["publication_allowed"])

    def test_actual_approval_is_not_clinical_license_or_rights(self):
        x = self.scan([review()])
        self.assertTrue(x["github_review_detected"])
        self.assertEqual(x["current_independent_github_approvals"], 1)
        self.assertFalse(x["clinical_approval"])
        self.assertFalse(x["rights_approval"])
        self.assertFalse(x["kernel_wo_admission"])
        self.assertEqual(x["decision"], "HOLD_G6_HUMAN_NORMATIVE_RIGHTS")

    def test_author_self_approval_cannot_count(self):
        x = self.scan([review(user_id=100)])
        self.assertEqual(x["current_independent_github_approvals"], 0)
        self.assertIn("AUTHOR_SELF_REVIEW", x["reasons"])

    def test_stale_commit_approval_is_not_current(self):
        x = self.scan([review(commit_id=OLD)])
        self.assertIn("STALE_REVIEW_SHA", x["reasons"])
        self.assertFalse(x["github_review_detected"])

    def test_changed_sha_between_fetch_and_execution_holds(self):
        x = self.scan([review(commit_id=OLD)], pr=fixture_pr(OLD), expected=HEAD)
        self.assertIn("PR_HEAD_SHA_CHANGED", x["reasons"])
        self.assertFalse(x["publication_allowed"])

    def test_followup_changes_requested_invalidates_earlier_approval(self):
        x = self.scan([
            review(review_id=1),
            review(state="CHANGES_REQUESTED",
                   submitted_at="2026-11-14T13:02:00Z", review_id=2),
        ])
        self.assertIn("CHANGES_REQUESTED_ACTIVE", x["reasons"])
        self.assertFalse(x["github_review_detected"])

    def test_followup_dismissal_invalidates_earlier_approval(self):
        x = self.scan([
            review(review_id=1),
            review(state="DISMISSED",
                   submitted_at="2026-11-14T13:03:00Z", review_id=3),
        ])
        self.assertIn("REVIEW_DISMISSED", x["reasons"])
        self.assertFalse(x["github_review_detected"])

    def test_comment_trailer_is_not_an_approval(self):
        x = self.scan([review(state="COMMENTED")])
        self.assertFalse(x["github_review_detected"])

    def test_two_events_from_same_reviewer_count_once(self):
        x = self.scan([
            review(review_id=1), review(review_id=2,
                   submitted_at="2026-11-14T13:01:00Z"),
        ])
        self.assertEqual(x["current_independent_github_approvals"], 1)
        self.assertEqual(x["distinct_reviewer_accounts_seen"], 1)

    def test_bot_review_is_rejected(self):
        x = self.scan([review(user_type="Bot")])
        self.assertIn("NON_HUMAN_REVIEW", x["reasons"])
        self.assertFalse(x["github_review_detected"])

    def test_missing_identity_and_timestamp_do_not_count(self):
        x = self.scan([dict(review(), user={}),
                       dict(review(review_id=2), submitted_at=None)])
        self.assertIn("REVIEW_IDENTITY_OR_STATE_UNVERIFIED", x["reasons"])
        self.assertIn("REVIEW_TIMESTAMP_UNVERIFIED", x["reasons"])

    def test_draft_even_with_review_stays_hold(self):
        x = self.scan([review()], pr=fixture_pr(draft=True))
        self.assertIn("PR_DRAFT", x["reasons"])
        self.assertFalse(x["publication_allowed"])

    def test_closed_or_merged_pr_cannot_release(self):
        x = self.scan([review()], pr={**fixture_pr(), "state": "closed",
                                      "merged_at": "2026-11-14T13:01:00Z"})
        self.assertIn("PR_NOT_OPEN", x["reasons"])
        self.assertIn("PR_ALREADY_MERGED", x["reasons"])

    def test_review_timestamps_need_offset(self):
        with self.assertRaises(ValueError):
            _review_sort_key(review(submitted_at="2026-11-14T13:01:00"))

    def test_invalid_repository_and_missing_api_token_block_before_network(self):
        for repo, token in [("../passwd/repo", "secret"), (REPO, "")]:
            with self.assertRaises(ValueError), patch(
                "scripts.cko_g6_github_reviews.urlopen",
                side_effect=AssertionError("NETWORK MUST NOT BE CALLED"),
            ):
                collect_github_reviews(repo, 57, token)

    def test_authenticated_response_repo_mismatch_is_rejected(self):
        wrong = {**fixture_pr(), "base": {"repo": {"full_name": "other/repo"}}}
        with patch("scripts.cko_g6_github_reviews._github_get", return_value=wrong):
            with self.assertRaisesRegex(ValueError, "mismatch"):
                collect_github_reviews(REPO, 57, "fake-synthetic-token")

    def test_paginated_review_array_requires_complete_response(self):
        payloads = [fixture_pr(), [review()] * 100, [review(review_id=101)]]
        with patch("scripts.cko_g6_github_reviews._github_get",
                   side_effect=payloads) as mock_get:
            _, reviews = collect_github_reviews(REPO, 57, "fake-synthetic-token")
        self.assertEqual(len(reviews), 101)
        self.assertEqual(mock_get.call_count, 3)

    def test_malformed_api_review_page_fails_closed(self):
        with patch("scripts.cko_g6_github_reviews._github_get",
                   side_effect=[fixture_pr(), {"error": "rate limit"}]):
            with self.assertRaisesRegex(ValueError, "Malformed"):
                collect_github_reviews(REPO, 57, "fake-synthetic-token")


if __name__ == "__main__":
    unittest.main()
