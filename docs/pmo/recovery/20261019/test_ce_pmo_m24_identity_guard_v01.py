import copy
import unittest

from ce_pmo_m24_identity_guard_v01 import validate_m24


def known_five_fixture():
    return {"population_id": "POP-M24-HOLD", "records": [
        {"git_path": f"data/legado/extracao_bruta/atomizado/fixture/file{i}.jsonl",
         "source_sha256": f"{i+1:064x}", "identity_evidence": f"TEST_ONLY:{i}", "state": "HOLD_ENVIRONMENT"}
        for i in range(5)]}


class M24GuardTests(unittest.TestCase):
    def test_fixture_exact_five_documentary_only(self):
        self.assertEqual([], validate_m24(known_five_fixture()))

    def test_no_identity_list_fails_closed(self):
        self.assertIn("M24_EXACT_FIVE_IDENTITIES_REQUIRED", validate_m24({"population_id": "POP-M24-HOLD", "records": []}))

    def test_missing_source_hash_denied(self):
        x = known_five_fixture()
        x["records"][1]["source_sha256"] = None
        self.assertIn("M24_SHA_UNVERIFIED:1", validate_m24(x))

    def test_duplicate_path_denied(self):
        x = known_five_fixture()
        x["records"][1]["git_path"] = x["records"][0]["git_path"]
        self.assertIn("M24_DUPLICATE_PATH", validate_m24(x))

    def test_implicit_release_denied(self):
        x = known_five_fixture()
        x["records"][2]["state"] = "APPROVED"
        self.assertIn("M24_PREMATURE_RELEASE:2", validate_m24(x))

    def test_missing_provenance_denied(self):
        x = known_five_fixture()
        x["records"][3]["identity_evidence"] = ""
        self.assertIn("M24_IDENTITY_EVIDENCE_MISSING:3", validate_m24(x))


if __name__ == "__main__":
    unittest.main()
