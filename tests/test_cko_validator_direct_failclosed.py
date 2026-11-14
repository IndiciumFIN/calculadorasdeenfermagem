"""No direct invocation of known incomplete validators may return True."""
import unittest

from packages.cli.kernel import core
from packages.cli.validators.registry import get_validator

STUBS = (
    "catmat_validator", "cid10_validator", "cid11_validator", "cvx_validator",
    "human_review_validator", "loinc_validator", "mesh_validator",
    "ncm_validator", "schema_validator",
)


class DirectValidatorHoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        core._ensure_validators()

    def test_every_unverified_validator_fails_closed_on_input(self):
        for name in STUBS:
            with self.subTest(validator=name):
                v = get_validator(name)
                for item in ({}, {"codigo": "A00", "descricao": "synthetic"},
                             {"status": "APPROVED", "rights_verified": True,
                              "clinical_approved": True,
                              "source_sha256": "a" * 64}):
                    valid, reason = v.validate(item)
                    self.assertIs(valid, False)
                    self.assertIsInstance(reason, str)
                    self.assertIn("HOLD_", reason)

    def test_batch_results_are_never_approved(self):
        for name in STUBS:
            with self.subTest(validator=name):
                v = get_validator(name)
                batch = v.validate_batch([{}, {"codigo": "A00"}])
                self.assertEqual(len(batch), 2)
                self.assertTrue(all(result[1] is False for result in batch))

    def test_kernel_still_holds_all_nine(self):
        for name in STUBS:
            with self.subTest(validator=name):
                self.assertNotIn(name, core.VALIDATORS)
                self.assertEqual(core.VALIDATOR_HOLDS.get(name), "SELF_TEST_FAILED")


if __name__ == "__main__":
    unittest.main()
