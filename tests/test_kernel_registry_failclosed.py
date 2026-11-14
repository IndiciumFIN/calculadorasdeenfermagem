"""Fail-closed regression tests for real validator registration."""
import unittest

from packages.cli.kernel import core


class KernelRegistryFailClosedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        core._ensure_validators()

    def test_schema_stub_is_not_approved(self):
        self.assertNotIn("schema_validator", core.VALIDATORS)
        self.assertEqual(core.VALIDATOR_HOLDS.get("schema_validator"), "SELF_TEST_FAILED")

    def test_human_review_stub_is_not_approved(self):
        self.assertNotIn("human_review_validator", core.VALIDATORS)
        self.assertEqual(core.VALIDATOR_HOLDS.get("human_review_validator"), "SELF_TEST_FAILED")

    def test_classification_stub_is_not_approved(self):
        self.assertNotIn("cid10_validator", core.VALIDATORS)
        self.assertEqual(core.VALIDATOR_HOLDS.get("cid10_validator"), "SELF_TEST_FAILED")

    def test_sha256_validator_is_tested_and_enabled(self):
        self.assertIn("sha256_validator", core.VALIDATORS)
        validator = core.VALIDATORS["sha256_validator"]
        self.assertEqual(validator.validate({"sha256_texto": "a" * 64}), (True, None))
        self.assertFalse(validator.validate({"sha256_texto": 123})[0])

    def test_no_placeholder_validator_is_silently_approved(self):
        self.assertTrue(core.VALIDATOR_HOLDS)
        self.assertTrue(set(core.VALIDATORS).isdisjoint(core.VALIDATOR_HOLDS))


if __name__ == "__main__":
    unittest.main()
