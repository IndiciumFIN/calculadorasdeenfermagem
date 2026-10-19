"""Offline P4 matrix checks; documentary rights and source linkage remain HOLD."""
import json
import unittest
from collections import Counter
from pathlib import Path


DATA = Path(__file__).with_name("CE_PMO_P4_CROSSWALK_FONTES_61_ARQUIVOS_65_20261019_CANDIDATE.json")


def verify(payload):
    errors = []
    sources = payload.get("source_records", [])
    files = payload.get("file_descriptors", [])
    ids = [x.get("source_cid") for x in sources]
    known = {x.get("source_cid") for x in sources}
    if len(sources) != 61 or len(files) != 65 or len(known) != 61 or len(ids) != len(known):
        errors.append("POPULATION_OR_CID_INVALID")
    if len({(x.get("theme"), x.get("file_name")) for x in files}) != 65:
        errors.append("FILE_ID_DUPLICATE")
    if len({x.get("theme") for x in sources}) != 15 or len({s.get("source_url") for s in sources}) != 49:
        errors.append("DOMAIN_OR_URL_POPULATION_INVALID")
    if sum(str(s.get("source_url", "")).startswith("http://") for s in sources) != 3:
        errors.append("HTTP_COUNT_DRIFT")
    if any(s.get("rights_decision") != "HOLD_RIGHTS_NO_EVIDENCE_IN_SOURCE_OBJECT" or s.get("independent_license_review") != "PENDING" for s in sources):
        errors.append("FALSE_RIGHTS_APPROVAL")
    if any(s.get("license_field_in_manifest") is not None for s in sources):
        errors.append("LICENSE_FIELD_UNEXPECTED_REVIEW_REQUIRED")
    for i, f in enumerate(files):
        candidates = f.get("candidate_source_cids", [])
        if not candidates or not set(candidates).issubset(known):
            errors.append(f"SOURCE_CANDIDATES_INVALID:{i}")
        elif any(s.get("theme") != f.get("theme") for s in sources if s.get("source_cid") in candidates):
            errors.append(f"SOURCE_DOMAIN_CROSS_LINK:{i}")
        if f.get("record_level_provenance") != "HOLD_UNVERIFIED" or f.get("content_approval") != "HOLD":
            errors.append(f"FALSE_CONTENT_APPROVAL:{i}")
        expected = "SINGLE_DOMAIN_SOURCE_CANDIDATE_NOT_RECORD_PROVEN" if len(candidates) == 1 else "MULTISOURCE_RECORD_LEVEL_HOLD"
        if f.get("source_link_state") != expected:
            errors.append(f"ATTRIBUTION_STATE_INVALID:{i}")
    counts = Counter(x.get("source_link_state") for x in files)
    if counts.get("SINGLE_DOMAIN_SOURCE_CANDIDATE_NOT_RECORD_PROVEN") != 12 or counts.get("MULTISOURCE_RECORD_LEVEL_HOLD") != 53:
        errors.append("ATTRIBUTION_COUNTS_DRIFT")
    if payload.get("metrics", {}).get("rights_evidenced_approved") != 0 or payload.get("metrics", {}).get("rights_hold") != 61 or payload.get("metrics", {}).get("project_percent") is not None:
        errors.append("FALSE_AGGREGATE_RELEASE")
    return errors


class P4SourceRightsTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(DATA.read_text(encoding="utf-8"))

    def test_verified_matrix(self):
        self.assertEqual([], verify(self.payload))

    def test_false_rights_approval_denied(self):
        self.payload["source_records"][0]["rights_decision"] = "APPROVED"
        self.assertIn("FALSE_RIGHTS_APPROVAL", verify(self.payload))

    def test_wrong_source_cid_denied(self):
        self.payload["file_descriptors"][0]["candidate_source_cids"] = ["UNKNOWN"]
        self.assertIn("SOURCE_CANDIDATES_INVALID:0", verify(self.payload))

    def test_false_content_approval_denied(self):
        self.payload["file_descriptors"][0]["content_approval"] = "PASS"
        self.assertIn("FALSE_CONTENT_APPROVAL:0", verify(self.payload))

    def test_duplicate_file_denied(self):
        self.payload["file_descriptors"][1]["theme"] = self.payload["file_descriptors"][0]["theme"]
        self.payload["file_descriptors"][1]["file_name"] = self.payload["file_descriptors"][0]["file_name"]
        self.assertIn("FILE_ID_DUPLICATE", verify(self.payload))


if __name__ == "__main__":
    unittest.main()
