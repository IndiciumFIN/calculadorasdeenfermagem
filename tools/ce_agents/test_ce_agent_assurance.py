"""Adversarial tests for CE local assurance; synthetic fixtures only."""
import copy
import hashlib
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch
from ce_agent_assurance import evaluate, validate_catalog, EXIT_FAIL, EXIT_HOLD, EXIT_PASS

AGENT = {"agent_id":"P1-HASH-INDEXER","wave":"P1","deployment_state":"NOT_DEPLOYED"}
CATALOG = {"agents":[AGENT]}

class AssuranceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.bytes = b"immutable-source"
        (self.root/"sample.txt").write_bytes(self.bytes)
        self.good = {
            "process":"P1","agent_id":"P1-HASH-INDEXER","task_id":"TEST",
            "snapshot":{"git_commit_sha":"a"*40},
            "artifacts":[{"path":"sample.txt","sha256":hashlib.sha256(self.bytes).hexdigest(),"byte_length":len(self.bytes)}],
            "expected_paths":["sample.txt"],"producer_id":"maker","auditor_id":"checker",
            "stage":"LOCAL_CANDIDATE","rights":"AUTHORIZED","secrets_screened":True
        }

    def result(self, **updates):
        m = copy.deepcopy(self.good)
        m.update(updates)
        return evaluate(m,CATALOG,self.root)

    def test_legitimate_bounded_pass(self):
        r = self.result()
        self.assertEqual(r["decision"],"PASS_BOUNDED")
        self.assertFalse(r["kernel_admitted"])
        self.assertFalse(r["semantically_validated"])

    def test_tampered_bytes(self):
        (self.root/"sample.txt").write_bytes(b"corruption")
        self.assertTrue(any("HASH_MISMATCH" in x for x in self.result()["failures"]))

    def test_missing_file(self):
        self.assertIn("COMPLETENESS_MISMATCH",self.result(expected_paths=["sample.txt","lost"])["failures"])

    def test_duplicate_manifest(self):
        self.assertIn("DUPLICATE_OR_INVALID_PATHS",self.result(artifacts=self.good["artifacts"]*2)["failures"])

    def test_self_audit(self):
        self.assertIn("SELF_AUDIT_FORBIDDEN",self.result(auditor_id="maker")["failures"])

    def test_unauthorized_agent(self):
        self.assertIn("UNREGISTERED_OR_WRONG_PROCESS_AGENT",self.result(agent_id="unknown")["failures"])

    def test_missing_receipt(self):
        self.assertIn("KERNEL_RECEIPT_REQUIRED",self.result(stage="PRODUCTIVE")["failures"])

    def test_forged_receipt_cannot_pass(self):
        r=self.result(stage="PRODUCTIVE",kernel_receipt={"status":"ADMITTED","wo_sha256":"x","policy_sha256":"y"})
        self.assertEqual(r["decision"],"HOLD")
        self.assertIn("KERNEL_RECEIPT_SIGNATURE_NOT_EXTERNALLY_VERIFIED",r["holds"])

    def test_bad_snapshot(self):
        self.assertIn("UNPINNED_SNAPSHOT",self.result(snapshot={"git_commit_sha":"main"})["failures"])

    def test_secret_screen_holds(self):
        self.assertEqual(self.result(secrets_screened=False)["decision"],"HOLD")

    def test_clinical_human_gate(self):
        r=self.result(clinical_review_required=True)
        self.assertIn("CLINICAL_REVIEW_REQUIRED",r["holds"])

    def test_false_precision_claim(self):
        r=self.result(semantic_precision_claimed=True)
        self.assertIn("UNSUPPORTED_SEMANTIC_PRECISION_CLAIM",r["failures"])

    def test_path_traversal(self):
        a=copy.deepcopy(self.good["artifacts"]);a[0]["path"]="../outside"
        r=self.result(artifacts=a,expected_paths=["../outside"])
        self.assertTrue(any("PATH_TRAVERSAL" in e for e in r["failures"]))

    def test_duplicate_agents(self):
        self.assertTrue(any("DUPLICATE_AGENT_ID" in e for e in validate_catalog({"agents":[AGENT,AGENT]})))

    def test_false_deployment(self):
        a=dict(AGENT,deployment_state="DEPLOYED")
        self.assertTrue(any("FALSE_DEPLOYMENT" in e for e in validate_catalog({"agents":[a]})))

    def test_unknown_process(self):
        self.assertIn("UNKNOWN_PROCESS",self.result(process="OTHER")["failures"])

if __name__=="__main__":
    unittest.main()
