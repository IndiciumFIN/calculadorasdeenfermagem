"""Negative admission tests: no missing/parser stub can yield technical PASS."""
import tempfile
import unittest
from pathlib import Path

from scripts.cko_technical_admission import evaluate, is_unconditional_true_validator


def good():
    return dict(repository={"structural_pass": True, "strict_pass": True,
                             "counts": {"pending": 0}},
                parser_ast={"static_pass": True, "problems": [], "missing_parsers": []},
                validator_holds={}, missing_policy_validators=[], unconditional_true=[])


class TechnicalAdmissionTests(unittest.TestCase):
    def test_pure_synthetic_green_does_not_approve_clinical_release(self):
        result = evaluate(**good())
        self.assertTrue(result["technical_admission_pass"])
        self.assertFalse(result["clinical_release_allowed"])
        self.assertFalse(result["editorial_publication_allowed"])

    def test_missing_parser_blocks_even_if_files_elsewhere_exist(self):
        args = good()
        args["repository"]["strict_pass"] = False
        args["repository"]["counts"]["pending"] = 1
        args["parser_ast"]["missing_parsers"] = ["contracts/fontes/missing.json"]
        self.assertFalse(evaluate(**args)["technical_admission_pass"])

    def test_parser_ast_disagreement_blocks(self):
        args = good()
        args["parser_ast"]["static_pass"] = False
        args["parser_ast"]["problems"] = [{"code": "MISMATCH_SOURCE_CONTRACT"}]
        self.assertIn("PARSER_CONTRACT_AST_INVALID",
                      {x["code"] for x in evaluate(**args)["findings"]})

    def test_validator_self_test_holds_block(self):
        args = good()
        args["validator_holds"] = {"schema_validator": "SELF_TEST_FAILED"}
        result = evaluate(**args)
        self.assertFalse(result["technical_admission_pass"])
        self.assertEqual(result["validator_holds"], 1)

    def test_unimplemented_policy_validator_blocks(self):
        args = good()
        args["missing_policy_validators"] = ["test_unknown_validator"]
        self.assertFalse(evaluate(**args)["technical_admission_pass"])

    def test_unconditional_true_validator_blocks(self):
        args = good()
        args["unconditional_true"] = ["packages/cli/validators/unsafe_validator.py"]
        result = evaluate(**args)
        self.assertEqual(result["unconditional_true_validators"], 1)
        self.assertFalse(result["technical_admission_pass"])

    def test_static_stub_detector_catches_exact_unconditional_approval(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "validator.py"
            path.write_text("class Stub:\n    def validate(self, item):\n        return True, None\n")
            self.assertTrue(is_unconditional_true_validator(path))
            path.write_text("class Real:\n    def validate(self, item):\n"
                            "        if item.get('ok'):\n            return True, None\n"
                            "        return False, 'hold'\n")
            self.assertFalse(is_unconditional_true_validator(path))
            path.write_text("invalid-python:")
            self.assertTrue(is_unconditional_true_validator(path))


if __name__ == "__main__":
    unittest.main()
