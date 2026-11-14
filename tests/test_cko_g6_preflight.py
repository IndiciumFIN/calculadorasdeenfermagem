"""G6 preflight negative tests. No reviewer, norm or license is fabricated."""
from __future__ import annotations

import copy
import unittest

from scripts.cko_g6_preflight import inspect_pmo


def candidate():
    def register(name, rows):
        return {"register": name, "rows": rows}
    return {
        "release_allowed": False,
        "registers": [
            register("SOURCE_REGISTER", [[
                "SRC-COFEN-736-2024", "COFEN 736", "OFFICIAL_NORMATIVE_ACT",
                "COFEN", "BR", "pt-BR", "OFFICIAL",
                "https://www.cofen.gov.br/resolucao-cofen-no-736-de-17-de-janeiro-de-2024/",
                "CURRENT_VERSION_REVIEW_PENDING", "M03_RECOVERED_SOURCE_TEXT",
            ]]),
            register("EVIDENCE_ATOMS", [[
                "ATM-01", "DOC-01", "OFFICIAL_NORMATIVE_ACT", "CLAIM-01",
            ]]),
            register("CLAIM_LEDGER", [[
                "CLAIM-01", "Test clinical statement", "", "art. 1",
                "ATM-01", "BR", "pt-BR", "EXACT_SPAN",
                "CURRENT_VERSION_REVIEW_PENDING", "PENDING_CLINICAL_REVIEW",
            ]]),
            register("CONTENT_REGISTER", [[
                "CONTENT-01", "Text", "EDITORIAL_CONTENT_MASTER", "scope",
                "", "", "SRC-COFEN-736-2024", "CLAIM-01", "pt-BR",
                "HOLD_HUMAN", "CANDIDATE_NO_PUBLICATION",
            ]]),
            register("HOLD_HUMAN", [[
                "HOLD-01", "NORMATIVE_CLINICAL_RIGHTS", "CLAIM-01", "unverified",
                "source", "review", "risk", "reviewer", "OPEN",
            ]]),
            register("CONFLICT_REGISTER", [[
                "CONFLICT-01", "completeness", "CLAIM-01", "incomplete",
                "needs revision", "source", "HIGH", "review", "OPEN_HOLD",
            ]]),
        ],
    }


class G6ReviewPreflightTests(unittest.TestCase):
    def scan(self, data=None):
        return inspect_pmo(candidate() if data is None else data, "0" * 64)

    def rows(self, data, name):
        return next(x["rows"] for x in data["registers"] if x["register"] == name)

    def test_consistent_candidate_still_blocks_publication(self):
        result = self.scan()
        self.assertTrue(result["technically_consistent"], result["structural_issues"])
        self.assertEqual(result["status"], "HOLD_HUMAN_NORMATIVE_RIGHTS")
        self.assertEqual(result["clinical_release_gate_exit_code"], 2)
        self.assertFalse(result["independent_reviewer_verified"])
        self.assertFalse(result["can_publish"])

    def test_orphan_atom_rejected(self):
        d = candidate()
        self.rows(d, "CLAIM_LEDGER")[0][4] = "ATM-ABSENT"
        self.assertIn("CLAIM_ORPHAN_ATOM", self.scan(d)["structural_issues"])

    def test_orphan_claim_in_atom_rejected(self):
        d = candidate()
        self.rows(d, "EVIDENCE_ATOMS")[0][3] = "CLAIM-UNKNOWN"
        self.assertIn("ATOM_CLAIM_REFERENCE_MISSING", self.scan(d)["structural_issues"])

    def test_missing_normative_clause_rejected(self):
        d = candidate()
        self.rows(d, "CLAIM_LEDGER")[0][3] = ""
        self.assertIn("CLAIM_MISSING_NORMATIVE_CLAUSE", self.scan(d)["structural_issues"])

    def test_content_claim_source_links_must_exist(self):
        d = candidate()
        self.rows(d, "CONTENT_REGISTER")[0][7] = "CLAIM-UNKNOWN"
        self.rows(d, "CONTENT_REGISTER")[0][6] = "SRC-UNKNOWN"
        issues = self.scan(d)["structural_issues"]
        self.assertIn("CONTENT_CLAIM_REFERENCE_MISSING", issues)
        self.assertIn("CONTENT_UNKNOWN_SOURCE", issues)

    def test_approved_content_not_accepted_by_review_gate(self):
        d = candidate()
        self.rows(d, "CONTENT_REGISTER")[0][9] = "APPROVED"
        self.rows(d, "CONTENT_REGISTER")[0][10] = "PUBLISHED"
        self.assertIn("CONTENT_NOT_HELD", self.scan(d)["structural_issues"])

    def test_release_flag_does_not_override_external_authority(self):
        d = candidate()
        d["release_allowed"] = True
        result = self.scan(d)
        self.assertIn("SELF_ASSERTED_RELEASE_UNTRUSTED", result["structural_issues"])
        self.assertFalse(result["can_promote_to_canonical"])

    def test_malformed_or_duplicated_rows_are_rejected(self):
        d = candidate()
        self.rows(d, "CLAIM_LEDGER").append(copy.deepcopy(self.rows(d, "CLAIM_LEDGER")[0]))
        self.assertIn("CLAIM_LEDGER_DUPLICATE_ID", self.scan(d)["structural_issues"])
        self.rows(d, "CLAIM_LEDGER").append({"id": "improper"})
        self.assertIn("CLAIM_LEDGER_MALFORMED_ROW", self.scan(d)["structural_issues"])

    def test_unknown_source_url_or_changed_origin_hold(self):
        d = candidate()
        src = self.rows(d, "SOURCE_REGISTER")[0]
        src[7] = "https://example.net/replacement"
        src[9] = "FROM_UNVERIFIED_MODEL"
        issues = self.scan(d)["structural_issues"]
        self.assertIn("SOURCE_URL_NOT_VERIFIED", issues)
        self.assertIn("SOURCE_ORIGIN_NOT_RECONCILED", issues)

    def test_missing_explicit_open_human_hold_rejected(self):
        d = candidate()
        self.rows(d, "HOLD_HUMAN")[0][8] = "RESOLVED"
        self.assertIn("REVIEW_HOLD_NOT_DOCUMENTED", self.scan(d)["structural_issues"])

    def test_missing_open_conflict_rejected(self):
        d = candidate()
        self.rows(d, "CONFLICT_REGISTER")[0][8] = "CLOSED"
        self.assertIn("CONFLICT_HOLD_NOT_DOCUMENTED", self.scan(d)["structural_issues"])

    def test_claims_cannot_be_deemed_reviewed_by_status_token(self):
        d = candidate()
        claim = self.rows(d, "CLAIM_LEDGER")[0]
        claim[8] = "APPROVED"
        claim[9] = "REVIEWED_BY=SELF"
        self.assertIn("CLAIM_UNREVIEWED_STATUS_NOT_VERIFIED", self.scan(d)["structural_issues"])

    def test_missing_register_is_structural_failure(self):
        d = candidate()
        d["registers"] = [r for r in d["registers"] if r["register"] != "HOLD_HUMAN"]
        issues = self.scan(d)["structural_issues"]
        self.assertIn("REQUIRED_REGISTER_MISSING", issues)
        self.assertIn("REVIEW_HOLD_NOT_DOCUMENTED", issues)


if __name__ == "__main__":
    unittest.main()
