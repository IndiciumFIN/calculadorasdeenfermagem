"""Primary norm review queue must never manufacture claim IDs or approvals."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"evidence"/"P0_CLAIM_SOURCE_HOLD.v1.json"
QUEUE=ROOT/"evidence"/"PRIMARY_REVIEW_QUEUE_23.v1.json"


class PrimaryReviewQueueTests(unittest.TestCase):
    def test_reported_counts_reconcile_without_fake_claim_ids(self):
        source=json.loads(SOURCE.read_text(encoding="utf-8"))
        queue=json.loads(QUEUE.read_text(encoding="utf-8"))
        original=source["claims"]["counts_by_document"]
        counts={r["document_version_id"]:r["reported_claims"] for r in queue["documents"]}
        self.assertEqual(counts,original)
        self.assertEqual(sum(counts.values()),source["claims"]["total"])
        self.assertEqual(queue["reported_candidate_claims"],23)
        self.assertTrue(queue["no_claim_id_generation"])
        self.assertEqual(queue["primary_verified_claims"],0)
        self.assertFalse(queue["reviewer_receipts_present"])
        self.assertFalse(queue["authoritative_raw_artifacts_verified"])

    def test_revoked_norm_is_historical_and_legacy_claims_not_current(self):
        queue=json.loads(QUEUE.read_text(encoding="utf-8"))
        historical=[r for r in queue["documents"] if r["status"]=="REVOKED_HISTORICAL_ONLY"]
        self.assertEqual(len(historical),1)
        self.assertEqual(historical[0]["reported_claims"],4)
        self.assertEqual(historical[0]["document_version_id"],"DOC-BR-COFEN-RES-429-2012")
        self.assertEqual(historical[0]["superseded_by"],"DOC-BR-COFEN-RES-754-2024")

    def test_all_primary_review_documents_stay_on_hold(self):
        queue=json.loads(QUEUE.read_text(encoding="utf-8"))
        self.assertIs(queue["publication_allowed"],False)
        self.assertIs(queue["clinical_release_allowed"],False)
        self.assertFalse(queue["source_artifact_hashes_verified"])
        for record in queue["documents"]:
            with self.subTest(document=record["document_version_id"]):
                self.assertEqual(record["primary_verified_claims"],0)
                self.assertIs(record["publication_allowed"],False)
                self.assertIs(record["source_artifact_sha256"],None)
                self.assertIs(record["locator_by_claim_verified"],False)
                for receipt in ("primary_fragment_receipt_id","rights_operation_review_receipt_id",
                                "clinical_reviewer_receipt_id"):
                    self.assertIsNone(record[receipt])
                self.assertTrue(record["official_primary_url"].startswith("https://www.cofen.gov.br/"))

if __name__=="__main__":
    unittest.main()
