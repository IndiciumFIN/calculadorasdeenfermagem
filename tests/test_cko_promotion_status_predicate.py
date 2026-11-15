"""Offline regression: characterize live CKO promotion predicate (not a release policy).

Source: SELECT pg_get_functiondef for cko_governance.guard_pilot_baseline_promotion()
in Supabase Calculadoras-Smart, 2026-11-15. No database connection or writes.
"""
import re
import unittest

LIVE = re.compile(r"(ACTIVE|ASSURED|APPROVED|PROMOTED|RELEASED|READY_FOR_RELEASE|CURRENT)")
EXACT_CANDIDATE = re.compile(r"^(?:ACTIVE|ASSURED|APPROVED|PROMOTED|RELEASED|READY_FOR_RELEASE|CURRENT)$")
REAL_STATUSES = (
    "ACTIVE", "CONTROLLED_CANDIDATE", "FINAL_TECHNICAL_WITH_SCOPED_HOLDS",
    "CANDIDATE", "FINAL_CONTROLLED", "RECOVERED_RECONCILIATION_CANDIDATE",
    "RECOVERED_HISTORICAL_PENDING_SUCCESSOR_RECONCILIATION", "CANDIDATE_HOLD",
    "PASS_WITH_SCOPED_HOLDS", "CONTROLLED_CANDIDATE_PENDING_CHECKER",
    "CONTROLLED_CONTRACT_CANDIDATE", "FROZEN", "ACTIVE_INTERNAL",
    "ACTIVE_VERIFIED", "APPROVED_NOT_DEPLOY_VERIFIED", "CANDIDATE_CONTROLLED",
    "CONTROLLED_CANDIDATE_NOT_FOR_PUBLICATION",
    "CONTROLLED_CONTRACT_CANDIDATE_VERIFIED",
    "CONTROLLED_DECISION_PENDING_DEPLOYMENT",
    "CONTROLLED_PAGE_CANDIDATE_PENDING_CHECKER",
    "CONTROLLED_RUNTIME_EVIDENCE_LOCAL_ONLY", "HOLD_STRICT_COMPLETENESS",
    "IN_PROGRESS", "PROPOSAL_HOLD", "RECOVERED_BYTE_VERIFIED",
    "RECOVERED_CURRENT_CONTROL_REFERENCE", "SUPERSEDED_BY_PILOT_V2_HOLD",
    "SUPERSEDED_PENDING_UNIVERSAL_REVALIDATION",
    "TECHNICAL_SCOPE_COMPLETE_WITH_SCOPED_HOLDS_NOT_RELEASED", "VALIDATED",
)

class PromotionPredicateCharacterization(unittest.TestCase):
    def test_inventory(self):
        self.assertEqual(len(REAL_STATUSES), 30)
        self.assertEqual(len(set(REAL_STATUSES)), 30)

    def test_real_status_substring_matches(self):
        for status in ("ACTIVE_INTERNAL", "ACTIVE_VERIFIED", "APPROVED_NOT_DEPLOY_VERIFIED"):
            with self.subTest(status=status):
                self.assertTrue(LIVE.search(status))
                self.assertFalse(EXACT_CANDIDATE.fullmatch(status))

    def test_adversarial_substrings(self):
        for status in ("NOT_APPROVED", "UNRELEASED", "INACTIVE", "NOT_CURRENT",
                       "PRE_ACTIVE_HOLD", "APPROVED_NOT_FOR_PUBLICATION"):
            with self.subTest(status=status):
                self.assertTrue(LIVE.search(status))
                self.assertFalse(EXACT_CANDIDATE.fullmatch(status))

    def test_exact_candidate_against_30_real_values(self):
        literals = {"ACTIVE", "ASSURED", "APPROVED", "PROMOTED",
                    "RELEASED", "READY_FOR_RELEASE", "CURRENT"}
        for status in REAL_STATUSES:
            with self.subTest(status=status):
                self.assertEqual(bool(EXACT_CANDIDATE.fullmatch(status)), status in literals)

if __name__ == "__main__":
    unittest.main()
