"""23 existing claim IDs, 20 evidence references, zero invented canonical IDs."""
import json
import unittest
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
GROUPED=ROOT/"evidence"/"PRIMARY_REVIEW_QUEUE_23.v1.json"
INDIVIDUAL=ROOT/"evidence"/"PRIMARY_REVIEW_QUEUE_23_INDIVIDUAL.v1.json"

class IndividualPrimaryReviewQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.grouped=json.loads(GROUPED.read_text(encoding="utf-8"))
        cls.index=json.loads(INDIVIDUAL.read_text(encoding="utf-8"))

    def test_all_original_claim_ids_reused_and_counts_match_four_documents(self):
        rows=self.index["claims"]
        self.assertEqual(len(rows),23)
        self.assertEqual(len({r["legacy_claim_id"] for r in rows}),23)
        self.assertTrue(self.index["original_identifiers_reused"])
        self.assertEqual(self.index["invented_canonical_claim_ids"],0)
        expected={x["document_version_id"]:x["reported_claims"]
                  for x in self.grouped["documents"]}
        actual=Counter(r["document_version_id"] for r in rows)
        self.assertEqual(dict(actual),expected)

    def test_evidence_sharing_preserved_but_not_verified(self):
        rows=self.index["claims"]
        refs=[e for row in rows for e in row["evidence_atom_ids"]]
        self.assertEqual(len(refs),23)
        self.assertEqual(len(set(refs)),20)
        self.assertEqual(self.index["unique_evidence_ids"],20)
        self.assertGreater(sum(v>1 for v in Counter(refs).values()),0)
        self.assertEqual(self.index["primary_verified_count"],0)

    def test_four_historical_claims_never_authorized(self):
        rows=self.index["claims"]
        historical=[r for r in rows if r["historical_only"]]
        self.assertEqual(len(historical),4)
        for row in historical:
            self.assertEqual(row["document_version_id"],"DOC-BR-COFEN-RES-429-2012")
            self.assertTrue(row["legacy_claim_id"].startswith("CLM-429-"))
            self.assertFalse(row["publication_allowed"])

    def test_every_claim_is_unapproved_and_canonic_mapping_not_invented(self):
        self.assertFalse(self.index["source_csv_original_bytes_verified"])
        self.assertIsNone(self.index["source_csv_original_bytes_sha256"])
        self.assertFalse(self.index["publication_allowed"])
        self.assertFalse(self.index["clinical_release_allowed"])
        for row in self.index["claims"]:
            with self.subTest(claim=row["legacy_claim_id"]):
                self.assertTrue(row["legacy_claim_id"].startswith("CLM-"))
                self.assertTrue(all(x.startswith("EV-DOC-") for x in row["evidence_atom_ids"]))
                self.assertIsNone(row["source_artifact_sha256"])
                self.assertIsNone(row["canonical_claim_id"])
                self.assertFalse(row["fragment_primary_verified"])
                self.assertFalse(row["source_ledger"]["legal_independent_approval"])
                self.assertFalse(row["publication_allowed"])
                self.assertEqual(row["status"],"HOLD_PRIMARY_EVIDENCE_AND_RIGHTS")
                self.assertEqual(len(row["original_missing_canonical_fields"]),12)
                for field in ("independent_source_receipt_id","normative_reviewer_receipt_id",
                              "clinical_reviewer_receipt_id"):
                    self.assertIsNone(row[field])

if __name__=="__main__":
    unittest.main()
