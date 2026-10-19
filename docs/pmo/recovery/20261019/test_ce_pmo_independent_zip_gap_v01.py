"""Adversarial test of independently re-run local ZIP integrity gate."""
import unittest

from CE_PMO_VALIDADOR_INDEPENDENTE_20261019 import verify_zip_payload_evidence


class ZipEvidenceGateTests(unittest.TestCase):
    def evidence(self):
        observed = {"status": "PASS_ZIP_INTEGRITY_ONLY", "failure_codes": {}, "zip_count": 13,
                    "totals": {"zip_verified": 13, "declared_regular_entries": 1956,
                               "payload_crc_verified": 1956, "declared_uncompressed_bytes": 63658956,
                               "payload_bytes_verified": 63658956}}
        prior = {"zip_containers": 13, "payload_crc_verified": 1956,
                 "streamed_payload_bytes_verified": 63658956}
        return observed, prior

    def test_exact_bounded_crc_replay_pass(self):
        self.assertEqual("PASS", verify_zip_payload_evidence(*self.evidence())["severity"])

    def test_missing_crc_fails_closed(self):
        obs, prior = self.evidence()
        obs["totals"]["payload_crc_verified"] -= 1
        self.assertEqual("HOLD", verify_zip_payload_evidence(obs, prior)["severity"])

    def test_unsafe_name_fails_closed(self):
        obs, prior = self.evidence()
        obs["failure_codes"] = {"ZIP_PATH_TRAVERSAL": 1}
        self.assertEqual("HOLD", verify_zip_payload_evidence(obs, prior)["severity"])

    def test_partial_zip_population_fails_closed(self):
        obs, prior = self.evidence()
        obs["zip_count"] = 12
        self.assertEqual("HOLD", verify_zip_payload_evidence(obs, prior)["severity"])


if __name__ == "__main__":
    unittest.main()
