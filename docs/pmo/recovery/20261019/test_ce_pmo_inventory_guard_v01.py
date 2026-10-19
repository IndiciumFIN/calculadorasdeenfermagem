"""Adversarial fail-closed tests for CE inventory documentary guard."""
import copy
import json
import io
import unittest
import zipfile
from pathlib import Path

from ce_pmo_inventory_guard_v01 import preflight

ROOT = Path(__file__).resolve().parent


class InventoryGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pmo = json.loads((ROOT / "CE_PMO_REGISTRO_MESTRE_20261019_v0.1.0_CANDIDATE.json").read_text())
        cls.queue = json.loads((ROOT / "CE_PMO_FILA_EXECUCAO_P1_P5_20261019_CANDIDATE.json").read_text())
        cls.dispatch = json.loads((ROOT / "CE_PMO_EXECUCAO_PARALELA_P2_P5_REUSE_20261019_CANDIDATE.json").read_text())
        cls.history = json.loads((ROOT / "CE_PMO_LEDGER_ANTI_RETRABALHO_20261019_CANDIDATE.json").read_text())
        cls.summary = json.loads((ROOT / "CE_PMO_INVENTARIO_RECURSIVO_RESUMO_20261019_CANDIDATE.json").read_text())
        cls.manifest = {"root_scope": "recursive_workspace_only", "files": [{"relative_path": "sample.txt", "sha256": "a" * 64, "bytes": 2, "external_persistence": "NOT_PROVEN_BY_LOCAL_SCAN"}]}
        cls.plan = {"branch": "pmo/recovery-controlled-20261019", "operations": [{"action": "create", "path": "docs/pmo/recovery/20261019/sample.md", "sha256_local": "b" * 64, "readback_required": True}]}

    def assert_block(self, domain, modified, expected):
        self.assertTrue(any(expected in issue for issue in preflight(**{domain: modified})))

    def test_valid_preflight_not_release(self):
        self.assertEqual([], preflight(manifest=self.manifest, summary=self.summary, pmo=self.pmo, queue=self.queue, dispatch=self.dispatch, history_ledger=self.history, publication=self.plan))

    def test_each_parallel_wave_anti_rework_passes_only_linking(self):
        self.assertEqual([], preflight(pmo=self.pmo, queue=self.queue, dispatch=self.dispatch, history_ledger=self.history))

    def test_parallel_anti_rework_missing_ledger_blocks(self):
        history = copy.deepcopy(self.history)
        history["tasks"] = []
        self.assertIn("DISPATCH_ANTI_REWORK_HISTORY_UNAVAILABLE", preflight(pmo=self.pmo, queue=self.queue, dispatch=self.dispatch, history_ledger=history))

    def test_stale_p3_wo_population_blocked(self):
        q = copy.deepcopy(self.queue)
        next(t for t in q["tasks"] if t["id"] == "P3-A")["action"] = "38 tasks and 76 PR2 WOs"
        self.assertIn("QUEUE_STALE_WO_COUNT", preflight(pmo=self.pmo, queue=q))

    def test_missing_parallel_wave_blocked(self):
        d = copy.deepcopy(self.dispatch)
        d["entries"].pop()
        self.assertIn("DISPATCH_FOUR_WAVE_ENTRIES_REQUIRED", preflight(pmo=self.pmo, queue=self.queue, dispatch=d))

    def test_unregistered_source_in_parallel_wave_blocked(self):
        d = copy.deepcopy(self.dispatch)
        d["entries"][0]["source_ids"].append("S-UNVERIFIED")
        self.assertIn("DISPATCH_SOURCE_MISMATCH:0", preflight(pmo=self.pmo, queue=self.queue, dispatch=d))

    def test_false_parallel_release_blocked(self):
        d = copy.deepcopy(self.dispatch)
        d["cross_wave_controls"]["all_4_waves_productive_execution_admitted"] = True
        self.assertIn("DISPATCH_FALSE_RELEASE", preflight(pmo=self.pmo, queue=self.queue, dispatch=d))

    def test_known_work_reexecution_blocked_by_guardian(self):
        issues = preflight(pmo=self.pmo, candidate_task=self.history["tasks"][0], history_ledger=self.history)
        self.assertIn("ANTI_REWORK_BLOCK_ALREADY_EXECUTED_REUSE_EVIDENCE", issues)

    def test_guardian_admits_registered_link_only(self):
        task = copy.deepcopy(self.history["tasks"][0])
        task.update(task_id="P2-LINK-01", intent="Link existing P2 evidence only",
                    operation_kind="EVIDENCE_LINK_ONLY", mode="READ_ONLY",
                    target_artifact="P2_existing_evidence_crosswalk.json",
                    intended_outputs=["EVIDENCE_CROSSWALK_ONLY"],
                    source_ids=["S-19", "S-23"], prior_evidence_ids=["S-19", "S-23"],
                    evidence_of_new_scope="REUSE_ONLY_EXISTING_EVIDENCE",
                    parameters={"no_source_reprocessing": True, "no_remote_writes": True})
        self.assertEqual([], preflight(pmo=self.pmo, candidate_task=task, history_ledger=self.history))

    def test_guardian_missing_history_fails_closed(self):
        issues = preflight(pmo=self.pmo, candidate_task=self.history["tasks"][0])
        self.assertIn("ANTI_REWORK_REQUIRES_TASK_LEDGER_MASTER", issues)

    def test_queue_cannot_stand_alone(self):
        self.assert_block("queue", self.queue, "QUEUE_REQUIRES_MASTER_PMO")

    def test_removed_all_gates_blocked(self):
        x = copy.deepcopy(self.pmo)
        x["gates"] = []
        self.assert_block("pmo", x, "PMO_GATE_POPULATION_INVALID")

    def test_fake_project_percent_blocked(self):
        x = copy.deepcopy(self.pmo)
        x["progress_metrics"]["full_project_completion"]["percent"] = 100
        self.assert_block("pmo", x, "UNSUPPORTED_PROJECT_PERCENT")

    def test_queue_task_false_completion_blocked(self):
        x = copy.deepcopy(self.queue)
        x["tasks"][0]["status"] = "COMPLETE"
        self.assertTrue(any("QUEUE_FALSE_EXECUTION" in issue for issue in preflight(pmo=self.pmo, queue=x)))

    def test_queue_id_collision_blocked(self):
        x = copy.deepcopy(self.queue)
        x["tasks"][1]["id"] = x["tasks"][0]["id"]
        self.assertTrue(any("QUEUE_TASK_IDENTITIES_INVALID" in issue for issue in preflight(pmo=self.pmo, queue=x)))

    def test_queue_unadmitted_runtime_blocked(self):
        x = copy.deepcopy(self.queue)
        x["tasks"][0]["mode"] = "EXECUTE_PRODUCTION"
        self.assertTrue(any("QUEUE_RUNTIME_NOT_ADMITTED" in issue for issue in preflight(pmo=self.pmo, queue=x)))

    def test_false_pass(self):
        x = copy.deepcopy(self.pmo)
        x["pmo_trusted"] = True
        self.assert_block("pmo", x, "PMO_FALSE_PASS")

    def test_m24_release(self):
        x = copy.deepcopy(self.pmo)
        x["populations"] = [v for v in x["populations"] if v["population_id"] != "POP-M24-HOLD"]
        self.assert_block("pmo", x, "M24_POPULATION_RELEASED")

    def test_gate_false_pass(self):
        x = copy.deepcopy(self.pmo)
        x["gates"][0]["status"] = "PASS"
        self.assert_block("pmo", x, "GATE_FALSE_PASS")

    def test_delete_blocked(self):
        x = copy.deepcopy(self.plan)
        x["operations"][0]["action"] = "deduplicate_delete"
        self.assert_block("publication", x, "DESTRUCTIVE_OR_UNKNOWN_ACTION")

    def test_main_blocked(self):
        x = copy.deepcopy(self.plan)
        x["branch"] = "main"
        self.assert_block("publication", x, "UNAUTHORIZED_TARGET_BRANCH")

    def test_upload_path_blocked(self):
        x = copy.deepcopy(self.plan)
        x["operations"][0]["path"] = "docs/pmo/recovery/20261019/upload/private_manifest.json"
        self.assert_block("publication", x, "PRIVATE_PATH_PUBLICATION")

    def test_readback_required(self):
        x = copy.deepcopy(self.plan)
        x["operations"][0]["readback_required"] = False
        self.assert_block("publication", x, "READBACK_REQUIRED")

    def test_base_sha_required_for_update(self):
        x = copy.deepcopy(self.plan)
        x["operations"][0]["action"] = "update"
        self.assert_block("publication", x, "CAS_BASE_SHA_REQUIRED")

    def test_hash_missing(self):
        x = copy.deepcopy(self.manifest)
        del x["files"][0]["sha256"]
        self.assert_block("manifest", x, "HASH_MISSING_OR_INVALID")

    def test_duplicate_inventory_path(self):
        x = copy.deepcopy(self.manifest)
        x["files"].append(copy.deepcopy(x["files"][0]))
        self.assert_block("manifest", x, "DUPLICATE_MANIFEST_PATH")

    def test_false_custody(self):
        x = copy.deepcopy(self.manifest)
        x["files"][0]["external_persistence"] = "LIBRARY_VERIFIED"
        self.assert_block("manifest", x, "FALSE_CUSTODY_CLAIM")

    def test_summary_private_hash(self):
        x = copy.deepcopy(self.summary)
        x["sha256"] = "a" * 64
        self.assert_block("summary", x, "PRIVATE_FIELD_IN_PUBLIC_SUMMARY")

    def test_zip_traversal(self):
        target = io.BytesIO()
        with zipfile.ZipFile(target, "w") as arc:
            arc.writestr("../escape.txt", "data")
        target.seek(0)
        self.assert_block("archives", [target], "ZIP_PATH_TRAVERSAL")

    def test_zip_safe(self):
        target = io.BytesIO()
        with zipfile.ZipFile(target, "w") as arc:
            arc.writestr("safe/document.txt", "data")
        target.seek(0)
        self.assertEqual([], preflight(archives=[target]))


if __name__ == "__main__":
    unittest.main()
