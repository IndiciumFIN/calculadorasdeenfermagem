"""Policy release is NOT equivalent to validation PASS; fail-closed regressions."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from packages.cli.kernel import core
from packages.cli.kernel.policy_registry import KernelPolicy


class AcceptingValidator:
    def validate(self, item):
        return True, None

    def run_tests(self):
        return True

    def test_suite(self):
        return [({"kind": "ok"}, True, "synthetic")]


class CrashingValidator(AcceptingValidator):
    def validate(self, item):
        raise RuntimeError("synthetic unhandled failure")


class KernelReleaseHoldTests(unittest.TestCase):
    def make_policy(self, **overrides):
        fields = dict(
            id="KERNEL-POLICY-998",
            name="Synthetic policy",
            description="Only synthetic inputs",
            source_contract="contracts/fontes/synthetic.json",
            validators=["test_validator"],
            publication_allowed=False,
            rights_by_operation_approved=False,
            requires_human_review=True,
            review_policy={"approval_required": True},
            wo_required=True,
        )
        fields.update(overrides)
        return KernelPolicy(**fields)

    def evaluate(self, policy, items=None, validator=None):
        instance = core.Kernel.__new__(core.Kernel)
        validator = validator or AcceptingValidator()
        with patch("packages.cli.kernel.core._ensure_validators", lambda: None), \
             patch("packages.cli.kernel.core.get_policy", return_value=policy), \
             patch.dict(core.VALIDATORS, {"test_validator": validator}, clear=True):
            if items is None:
                return instance.evaluate({"fixture": True}, policy.id)
            return instance.evaluate_batch(items, policy.id)

    def test_policy_fields_not_dropped_during_parse(self):
        policy = self.make_policy()
        restored = KernelPolicy.from_dict(policy.to_dict())
        self.assertFalse(restored.publication_allowed)
        self.assertFalse(restored.rights_by_operation_approved)
        self.assertTrue(restored.review_policy["approval_required"])

    def test_review_must_hold_even_when_validator_passes(self):
        policy = self.make_policy(publication_allowed=True,
                                  rights_by_operation_approved=True)
        decision = self.evaluate(policy)
        self.assertEqual(decision.decision, core.Decision.PENDING_REVIEW)
        self.assertGreater(decision.pending_count, 0)
        self.assertFalse(decision.has_failures())

    def test_rights_hold_even_if_editorial_flag_disabled(self):
        policy = self.make_policy(publication_allowed=True,
                                  requires_human_review=False,
                                  review_policy={"approval_required": False})
        self.assertEqual(self.evaluate(policy).decision, core.Decision.PENDING_REVIEW)

    def test_publication_hold_even_with_rights(self):
        policy = self.make_policy(rights_by_operation_approved=True,
                                  requires_human_review=False,
                                  review_policy={"approval_required": False})
        self.assertEqual(self.evaluate(policy).decision, core.Decision.PENDING_REVIEW)

    def test_batch_holds_even_if_all_validators_pass(self):
        policy = self.make_policy()
        decision = self.evaluate(policy, [{"ok": 1}, {"ok": 2}])
        self.assertEqual(decision.decision, core.Decision.PENDING_REVIEW)

    def test_reject_empty_batch(self):
        decision = self.evaluate(self.make_policy(), [])
        self.assertEqual(decision.decision, core.Decision.REJECTED)
        self.assertTrue(decision.has_failures())

    def test_missing_validator_must_report_failure_not_approval(self):
        decision = self.evaluate(self.make_policy(validators=["missing"]))
        self.assertEqual(decision.decision, core.Decision.REJECTED)
        self.assertTrue(decision.has_failures())
        self.assertIn("não implementado", decision.errors[0])

    def test_crashing_validator_rejects_instead_of_escaping(self):
        decision = self.evaluate(self.make_policy(), validator=CrashingValidator())
        self.assertEqual(decision.decision, core.Decision.REJECTED)
        self.assertTrue(decision.has_failures())
        self.assertIn("VALIDATOR_EXCEPTION", decision.results[0].error)

    def test_explicitly_unrestricted_synthetic_policy_may_validate(self):
        policy = self.make_policy(
            id="TEST-KERNEL-POLICY-998",
            source_contract="contracts/fixtures/synthetic.json",
            processing_scope="SYNTHETIC_ONLY",
            publication_allowed=True, rights_by_operation_approved=True,
            requires_human_review=False, review_policy={"approval_required": False},
            wo_required=False, sha256_required=False)
        self.assertEqual(self.evaluate(policy).decision, core.Decision.APPROVED)

    def test_self_declared_clinical_review_and_rights_cannot_unlock_real_policy(self):
        policy = self.make_policy(
            id="KERNEL-POLICY-001",
            source_contract="contracts/fontes/cofen_dou.json",
            processing_scope="OFFICIAL_NORMATIVE",
            publication_allowed=True, rights_by_operation_approved=True,
            requires_human_review=False, review_policy={"approval_required": False},
            wo_required=False, sha256_required=False)
        self.assertEqual(self.evaluate(policy).decision, core.Decision.PENDING_REVIEW)
        self.assertEqual(self.evaluate(policy, [{"fixture": True}]).decision, core.Decision.PENDING_REVIEW)

    def test_fake_synthetic_scope_cannot_unlock_normative_identity(self):
        policy = self.make_policy(
            id="KERNEL-POLICY-001",
            source_contract="contracts/fontes/cofen_dou.json",
            processing_scope="SYNTHETIC_ONLY",
            publication_allowed=True, rights_by_operation_approved=True,
            requires_human_review=False, review_policy={"approval_required": False},
            wo_required=False, sha256_required=False)
        self.assertEqual(self.evaluate(policy).decision, core.Decision.PENDING_REVIEW)

    def test_synthetic_name_without_fixture_source_remains_hold(self):
        policy = self.make_policy(
            id="TEST-POLICY-998",
            source_contract="contracts/fontes/cofen_dou.json",
            processing_scope="SYNTHETIC_ONLY",
            publication_allowed=True, rights_by_operation_approved=True,
            requires_human_review=False, review_policy={"approval_required": False},
            wo_required=False, sha256_required=False)
        self.assertEqual(self.evaluate(policy).decision, core.Decision.PENDING_REVIEW)

    def test_wo_required_without_verified_work_order_holds(self):
        policy = self.make_policy(
            publication_allowed=True, rights_by_operation_approved=True,
            requires_human_review=False, review_policy={"approval_required": False},
            sha256_required=False, wo_required=True)
        self.assertEqual(self.evaluate(policy).decision, core.Decision.PENDING_REVIEW)

    def test_sha_requirement_without_validator_holds(self):
        policy = self.make_policy(
            publication_allowed=True, rights_by_operation_approved=True,
            requires_human_review=False, review_policy={"approval_required": False},
            wo_required=False, sha256_required=True)
        self.assertEqual(self.evaluate(policy).decision, core.Decision.PENDING_REVIEW)

    def test_kernel_gate_does_not_write_to_file_system(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "must-not-exist"
            policy = self.make_policy(atoms_output=str(output))
            instance = core.Kernel.__new__(core.Kernel)
            with patch("packages.cli.kernel.core._ensure_validators", lambda: None), \
                 patch("packages.cli.kernel.core.get_policy", return_value=policy), \
                 patch.dict(core.VALIDATORS, {"test_validator": AcceptingValidator()}, clear=True):
                self.assertEqual(instance.gate(policy.id), 2)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
