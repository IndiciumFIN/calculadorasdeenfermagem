"""Negative tests for static contract-bound CKO parser inspection."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.cko_parser_contract_audit import inspect


VALID = '''SOURCE_CONTRACT = "contracts/fontes/test_source.json"
PARSER_API_VERSION = "1.0.0"
class ParseHold(ValueError): pass

def parse(raw, *, source_id, document_id):
    if not source_id or not document_id:
        raise ParseHold("missing")
    return [{"publication_allowed": False, "release_allowed": False}]
'''


class ContractAstAuditTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.registry = self.root / "contracts/fontes"
        self.registry.mkdir(parents=True)
        self.module = self.root / "packages/cli/parsers/test_source.py"
        self.module.parent.mkdir(parents=True)
        self.module.write_text(VALID, encoding="utf-8")
        self.contract = self.registry / "test_source.json"
        self.record = {
            "fonte_slug": "test_source",
            "source_contract": "contracts/fontes/test_source.json",
            "parser": "packages/cli/parsers/test_source.py",
            "parser_version": "1.0.0",
        }
        self.save()

    def save(self):
        self.contract.write_text(json.dumps(self.record), encoding="utf-8")

    def codes(self):
        return {p["code"] for p in inspect(self.root)["problems"]}

    def test_valid_minimal_technical_candidate(self):
        x = inspect(self.root)
        self.assertTrue(x["static_pass"])
        self.assertEqual(x["contracts"], 1)
        self.assertEqual(x["missing_parsers"], [])
        self.assertFalse(x["publication_allowed"])

    def test_missing_parser_not_counted_as_verified(self):
        self.module.unlink()
        x = inspect(self.root)
        self.assertEqual(x["missing_parsers"], ["contracts/fontes/test_source.json"])
        self.assertEqual(x["candidate_parsers_checked"], [])

    def test_mismatched_contract_and_version_are_rejected(self):
        self.module.write_text(VALID.replace("1.0.0", "2.0.0")
                               .replace("fontes/test_source.json", "fontes/other.json"))
        self.assertIn("MISMATCH_SOURCE_CONTRACT", self.codes())
        self.assertIn("MISMATCH_PARSER_API_VERSION", self.codes())

    def test_file_existence_does_not_prove_entrypoint(self):
        self.module.write_text(VALID.replace("def parse(", "def noop("))
        self.assertIn("MISSING_PARSE_ENTRYPOINT", self.codes())

    def test_provenance_and_rejection_required(self):
        self.module.write_text(VALID.replace("source_id, document_id", "token"))
        self.assertIn("MISSING_PROVENANCE_PARAMETERS", self.codes())
        self.module.write_text(VALID.replace('raise ParseHold("missing")', 'return []'))
        self.assertIn("NO_EXPLICIT_REJECTION", self.codes())

    def test_no_implicit_release_policy(self):
        self.module.write_text(VALID.replace('"publication_allowed": False', '"publication_allowed": True')
                               .replace('"release_allowed": False', '"release_allowed": True'))
        self.assertIn("NO_STATIC_RELEASE_HOLD", self.codes())

    def test_stale_legacy_adapter_is_unassessed_not_approved(self):
        self.record["parser"] = "packages/cli/legacy/adaptor.py"
        self.save()
        path = self.root / self.record["parser"]
        path.parent.mkdir(parents=True)
        path.write_text("# legacy\n")
        x = inspect(self.root)
        self.assertEqual(x["legacy_adapters_unassessed"], ["contracts/fontes/test_source.json"])
        self.assertEqual(x["candidate_parsers_checked"], [])

    def test_unsafe_traversal_is_denied(self):
        self.record["parser"] = "packages/cli/../../etc/passwd"
        self.save()
        self.assertIn("UNSAFE_PARSER_PATH", self.codes())

    def test_invalid_json_contract_is_denied(self):
        self.contract.write_text("INVALID JSON")
        self.assertIn("INVALID_CONTRACT", self.codes())


if __name__ == "__main__":
    unittest.main()
