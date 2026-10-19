"""Adversarial tests for deterministic CE anti-rework documentary admission gate."""
import copy
import json
import unittest
from pathlib import Path

from ce_pmo_no_rework_agent_v01 import evaluate

ROOT = Path(__file__).resolve().parent


class NoReworkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads((ROOT / "CE_PMO_LEDGER_ANTI_RETRABALHO_20261019_CANDIDATE.json").read_text())
        cls.master = json.loads((ROOT / "CE_PMO_REGISTRO_MESTRE_20261019_v0.1.0_CANDIDATE.json").read_text())
        cls.history_index = json.loads((ROOT / "CE_PMO_INDICE_EVIDENCIAS_HISTORICAS_CE01_CE06_M_20261019_CANDIDATE.json").read_text())

    def candidate(self):
        return copy.deepcopy(self.ledger["tasks"][0])

    def reuse_candidate(self):
        task = self.candidate()
        task.update(task_id="P2-LINK-01", intent="Link existing P2 evidence only",
                    operation_kind="EVIDENCE_LINK_ONLY", mode="READ_ONLY",
                    target_artifact="P2_existing_evidence_crosswalk.json",
                    intended_outputs=["EVIDENCE_CROSSWALK_ONLY"],
                    source_ids=["S-19", "S-23"], prior_evidence_ids=["S-19", "S-23"],
                    evidence_of_new_scope="REUSE_ONLY_EXISTING_EVIDENCE",
                    parameters={"no_source_reprocessing": True, "no_remote_writes": True})
        return task

    def test_known_sources_link_only_admitted_as_analysis(self):
        answer = self.decision(self.reuse_candidate())
        self.assertEqual("ALLOW_REUSE_ANALYSIS_ONLY", answer["decision"])
        self.assertTrue(answer["not_kernel_admission"])

    def test_reuse_requires_registered_evidence(self):
        task = self.reuse_candidate()
        task["prior_evidence_ids"] = []
        self.assertEqual("HOLD_HISTORICAL_COVERAGE_INCOMPLETE", self.decision(task)["code"])

    def test_reuse_requires_no_processing_or_remote_writes(self):
        task = self.reuse_candidate()
        task["parameters"]["no_remote_writes"] = False
        self.assertEqual("HOLD_HISTORICAL_COVERAGE_INCOMPLETE", self.decision(task)["code"])

    def test_reuse_cannot_be_productive(self):
        task = self.reuse_candidate()
        task["mode"] = "PRODUCTION"
        self.assertEqual("RUNTIME_ADMISSION_NOT_PROVEN", self.decision(task)["code"])

    def test_reuse_existing_task_id_fails_closed(self):
        task = self.reuse_candidate()
        task["task_id"] = "P1-A"
        self.assertEqual("HOLD_VERSION_OR_CUTOFF_VARIANT", self.decision(task)["code"])

    def decision(self, candidate=None, ledger=None, master=None):
        return evaluate(candidate if candidate is not None else self.candidate(), ledger if ledger is not None else self.ledger, master if master is not None else self.master, self.history_index)

    def test_historical_artifact_blocks_new_documentary_task(self):
        task = self.candidate()
        task["task_id"] = "M-HISTORICAL-RETRY"
        task["target_artifact"] = self.history_index["local_reports"][0]["locator"]
        task["intent"] = "new unrelated attempt to generate prior document"
        self.assertEqual("HOLD_PRIOR_DOCUMENTARY_EVIDENCE_REVIEW", self.decision(task)["code"])

    def test_ce02_archive_evidence_blocks_auto_admission(self):
        task = self.candidate()
        task["task_id"] = "CE02-HIST-RETRY"
        task["domain"] = "CE-02"
        task["intent"] = "new processing of historical records"
        self.assertEqual("HOLD_PRIOR_FRONT_EVIDENCE_REVIEW", self.decision(task)["code"])

    def test_missing_history_index_blocks_unknown_work(self):
        task = self.candidate()
        task["task_id"] = "NEW-ID"
        task["intent"] = "new task only"
        self.assertEqual("HOLD_HISTORICAL_INDEX_NOT_LOADED", evaluate(task, self.ledger, self.master)["code"])

    def test_completed_history_blocks_same_task(self):
        self.assertEqual("BLOCK_ALREADY_EXECUTED_REUSE_EVIDENCE", self.decision()["code"])

    def test_changed_id_same_intent_blocks(self):
        task = self.candidate()
        task["task_id"] = "P1-A-NEW-ID"
        self.assertEqual("BLOCK_ALREADY_EXECUTED_REUSE_EVIDENCE", self.decision(task)["code"])

    def test_output_order_and_new_id_do_not_bypass(self):
        task = self.candidate()
        task["task_id"] = "DIFFERENT-ID"
        task["intended_outputs"] = list(reversed(task["intended_outputs"]))
        self.assertEqual("BLOCK_ALREADY_EXECUTED_REUSE_EVIDENCE", self.decision(task)["code"])

    def test_partial_history_blocks_new_task(self):
        task = self.candidate()
        task["intent"] = "brand new source audit"
        task["task_id"] = "NEW-AUDIT-01"
        task["target_artifact"] = "new-unique-output.json"
        task["evidence_of_new_scope"] = "DOCUMENTED_RECONCILIATION"
        self.assertEqual("HOLD_HISTORICAL_COVERAGE_INCOMPLETE", self.decision(task)["code"])

    def test_new_task_only_preflight_when_history_reconciled(self):
        task = self.candidate()
        task["intent"] = "brand new source audit"
        task["task_id"] = "NEW-AUDIT-01"
        task["target_artifact"] = "new-unique-output.json"
        task["evidence_of_new_scope"] = "DOCUMENTED_RECONCILIATION"
        ledger = copy.deepcopy(self.ledger)
        ledger["historical_coverage"] = "HISTORY_RECONCILED"
        self.assertEqual("ALLOW_PREFLIGHT_ONLY", self.decision(task, ledger)["decision"])

    def test_changed_cutoff_requires_review(self):
        task = self.candidate()
        task["cutoff"] = "NEW_CUTOFF"
        self.assertEqual("HOLD_VERSION_OR_CUTOFF_VARIANT", self.decision(task)["code"])

    def test_incomplete_evidence_blocks(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["tasks"][0]["evidence"]["readback"] = "UNKNOWN"
        self.assertEqual("EXECUTION_EVIDENCE_INCOMPLETE", self.decision(ledger=ledger)["code"])

    def test_running_blocks_concurrent_work(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["tasks"][0]["status"] = "IN_PROGRESS"
        self.assertEqual("BLOCK_CONCURRENT_EXECUTION", self.decision(ledger=ledger)["code"])

    def test_duplicate_history_blocks(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["tasks"].append(copy.deepcopy(ledger["tasks"][0]))
        self.assertEqual("LEDGER_DUPLICATE_IDENTITY", self.decision(ledger=ledger)["code"])

    def test_unknown_source_blocks(self):
        task = self.candidate()
        task["source_ids"] = ["S-DOES-NOT-EXIST"]
        self.assertEqual("SOURCE_IDS_NOT_VERIFIED", self.decision(task)["code"])

    def test_productive_runtime_blocked(self):
        task = self.candidate()
        task["mode"] = "PRODUCTION"
        self.assertEqual("RUNTIME_ADMISSION_NOT_PROVEN", self.decision(task)["code"])

    def test_empty_ledger_blocks(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["tasks"] = []
        self.assertEqual("LEDGER_EMPTY_OR_INVALID", self.decision(ledger=ledger)["code"])

    def test_jurisdiction_difference_not_auto_deduplicated(self):
        task = self.candidate()
        task["jurisdiction"] = "BR"
        self.assertEqual("HOLD_VERSION_OR_CUTOFF_VARIANT", self.decision(task)["code"])

    def test_missing_identity_blocks(self):
        task = self.candidate()
        del task["target_artifact"]
        self.assertEqual("TASK_IDENTITY_INCOMPLETE", self.decision(task)["code"])

    def test_untrusted_ledger_blocks(self):
        ledger = copy.deepcopy(self.ledger)
        ledger["state"] = "CANONICAL"
        self.assertEqual("LEDGER_NOT_TRUSTED", self.decision(ledger=ledger)["code"])


if __name__ == "__main__":
    unittest.main()
