"""Synthetic regression tests for deterministic CKO contract/PMO metadata graphs."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from scripts.cko_catalog import build, render


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cko-catalog-fixture-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.sources = self.root / "contracts/fontes"
        self.policies = self.root / "contracts/policies"
        self.sources.mkdir(parents=True)
        self.policies.mkdir(parents=True)
        self.parser = self.root / "packages/cli/parsers/synthetic.py"
        self.parser.parent.mkdir(parents=True)
        self.parser.write_text("def parse(raw): return raw\n", encoding="utf-8")
        self.source = dict(
            fonte_slug="synthetic", source_contract="contracts/fontes/synthetic.json",
            kernel_policy_id="KERNEL-POLICY-001", parser="packages/cli/parsers/synthetic.py",
            validators=["schema_validator"], fonte_oficial="Synthetic Authority",
            tipo="NORMATIVO", description="Synthetic fixture, not authority"
        )
        self.policy = dict(
            id="KERNEL-POLICY-001", source_contract="contracts/fontes/synthetic.json",
            validators=["schema_validator"], version="1.0.0",
            requires_human_review=True, wo_required=True,
            sha256_required=True, publication_allowed=False,
        )
        self.save()

    def save(self):
        (self.sources / "synthetic.json").write_text(
            json.dumps(self.source), encoding="utf-8")
        (self.policies / "KERNEL-POLICY-001.json").write_text(
            json.dumps(self.policy), encoding="utf-8")

    def catalog(self, pmo=None):
        return build(self.root, pmo_file=pmo)

    def errors(self, catalog):
        return [f for f in catalog["findings"] if f["severity"] == "ERROR"]

    def test_valid_registry_has_no_dangling_graph_edges(self):
        c = self.catalog()
        self.assertFalse(self.errors(c), c["findings"])
        self.assertEqual(c["statistics"]["sources"], 1)
        self.assertEqual(c["statistics"]["policies"], 1)
        self.assertEqual(c["statistics"]["validators_declared"], 1)
        self.assertEqual(c["statistics"]["missing_parsers"], 0)
        self.assertEqual(c["statistics"]["edges"], 4)
        self.assertIs(c["publication_allowed"], False)

    def test_deterministic_dictionary_graph_and_mermaid(self):
        first = render(self.catalog())
        second = render(self.catalog())
        self.assertEqual(first, second)
        self.assertIn("synthetic", first["catalog.json"])
        self.assertIn("schema_validator", first["relations.mmd"])
        self.assertIn("fonte_slug", first["dictionary.md"])
        self.assertIn("AUSENTE / HOLD", first["SUMMARY.md"].replace(
            "PRESENTE ≠ HOMOLOGADO", "AUSENTE / HOLD"))

    def test_missing_parser_stays_pending_not_approved(self):
        self.parser.unlink()
        c = self.catalog()
        self.assertEqual(c["statistics"]["missing_parsers"], 1)
        self.assertIn("MISSING_PARSER", {f["code"] for f in c["findings"]})
        parser = next(n for n in c["entities"] if n["type"] == "SOURCE_PARSER")
        self.assertEqual(parser["admission"], "MISSING_IMPLEMENTATION")
        self.assertFalse(parser["release_allowed"])

    def test_source_policy_inverse_must_match(self):
        self.source["kernel_policy_id"] = "KERNEL-POLICY-777"
        self.save()
        self.assertIn("BROKEN_POLICY_SOURCE_INVERSE",
                      {f["code"] for f in self.errors(self.catalog())})

    def test_parser_traversal_rejected(self):
        self.source["parser"] = "packages/cli/../../sensitive.py"
        self.save()
        self.assertIn("INVALID_PARSER_PATH",
                      {f["code"] for f in self.errors(self.catalog())})

    def test_duplicate_validator_link_rejected(self):
        self.policy["validators"] = ["schema_validator", "schema_validator"]
        self.save()
        self.assertIn("DUPLICATE_VALIDATOR_LINK",
                      {f["code"] for f in self.errors(self.catalog())})

    def test_missing_human_review_is_pending_not_release(self):
        self.policy["requires_human_review"] = False
        self.save()
        c = self.catalog()
        self.assertIn("POLICY_REVIEW_INCOMPLETE",
                      {f["code"] for f in c["findings"]})
        policy = next(n for n in c["entities"] if n["type"] == "KERNEL_POLICY")
        self.assertFalse(policy["release_allowed"])

    def test_observed_data_dictionary_is_not_normative_claim(self):
        c = self.catalog()
        src = c["dictionary"]["SOURCE_CONTRACT"]
        field = next(f for f in src if f["field"] == "validators")
        self.assertEqual(field["observed_types"], ["array"])
        self.assertEqual(field["definition_origin"],
                         "OBSERVED_CONTRACT_METADATA_NOT_NORMATIVE_CLAIM")

    def pmo_file(self):
        pmo = {
            "registers": [
                {"register":"SOURCE_REGISTER","rows":[["SRC-EXAMPLE","Fixture"]]},
                {"register":"DOCUMENT_REGISTER","rows":[["DOC-EXAMPLE","SRC-EXAMPLE"]]},
                {"register":"EVIDENCE_ATOMS","rows":[[
                    "ATM-EXAMPLE","DOC-EXAMPLE","OFFICIAL_NORMATIVE_ACT",
                    "CKO-CLAIM-A;CKO-CLAIM-B"]]},
                {"register":"CLAIM_LEDGER","rows":[
                    ["CKO-CLAIM-A","","","","ATM-EXAMPLE","","","","",
                     "PENDING_CLINICAL_AND_EDITORIAL_REVIEW","EVIDENCE_BOUND_HOLD"],
                    ["CKO-CLAIM-B","","","","ATM-EXAMPLE","","","","",
                     "PENDING_CLINICAL_AND_EDITORIAL_REVIEW","EVIDENCE_BOUND_HOLD"]
                ]},
                {"register":"CONTENT_REGISTER","rows":[[
                    "CONTENT-EXAMPLE","","","","","","SRC-EXAMPLE",
                    "CKO-CLAIM-A;CKO-CLAIM-B","","HOLD_HUMAN","CANDIDATE_NO_PUBLICATION"]]}
            ]
        }
        file = self.root / "fixture-pmo.json"
        file.write_text(json.dumps(pmo), encoding="utf-8")
        return file

    def test_optional_pmo_lineage_supports_shared_evidence(self):
        c = self.catalog(self.pmo_file())
        self.assertFalse(self.errors(c), c["findings"])
        relations = {(x["source"], x["relation"], x["target"])
                     for x in c["relationships"]}
        self.assertIn(("EVIDENCE_ATOM:ATM-EXAMPLE", "SUPPORTS_CLAIM",
                       "CANDIDATE_CLAIM:CKO-CLAIM-A"), relations)
        self.assertIn(("EVIDENCE_ATOM:ATM-EXAMPLE", "SUPPORTS_CLAIM",
                       "CANDIDATE_CLAIM:CKO-CLAIM-B"), relations)
        self.assertIn("NORMATIVE_CROSSWALK_UNVERIFIED",
                      {x["code"] for x in c["findings"]})

    def test_pmo_orphan_claim_rejected(self):
        file = self.pmo_file()
        data = json.loads(file.read_text())
        evidence = next(x for x in data["registers"] if x["register"] == "EVIDENCE_ATOMS")
        evidence["rows"][0][3] = "CKO-UNKNOWN"
        file.write_text(json.dumps(data))
        self.assertIn("PMO_ORPHAN", {f["code"] for f in self.errors(self.catalog(file))})

    def test_pmo_claim_review_bypass_rejected(self):
        file = self.pmo_file()
        data = json.loads(file.read_text())
        claims = next(x for x in data["registers"] if x["register"] == "CLAIM_LEDGER")
        claims["rows"][0][9] = "CLINICALLY_APPROVED"
        file.write_text(json.dumps(data))
        self.assertIn("PMO_CLAIM_RELEASE_BYPASS",
                      {f["code"] for f in self.errors(self.catalog(file))})


if __name__ == "__main__":
    unittest.main()
