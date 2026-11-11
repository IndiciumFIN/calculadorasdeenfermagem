"""Kernel core — executor determinístico de políticas.

O Kernel compara INPUT contra POLÍTICA. Se confere → APPROVED. Se não → REJECTED (exit 2).
Tudo importa de um ponto único: packages.schemas.invariantes.AtomoBlindado.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import typer

from packages.schemas.invariantes import AtomoBlindado
from .policy_registry import POLICIES_DIR, PolicyRegistry, get_policy

REPO_ROOT = POLICIES_DIR.parents[1]

VALIDATORS: dict[str, Any] = {}
_validator_imported = False
_validator_tests: dict[str, bool] = {}


def _ensure_validators():
    global _validator_imported, VALIDATORS
    if not _validator_imported:
        import packages.cli.validators  # noqa: F401 — auto-registro
        from packages.cli.validators.registry import VALIDATORS as registered

        VALIDATORS.clear()
        VALIDATORS.update(registered)
        _validator_imported = True


class Decision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PENDING_REVIEW = "PENDING_HUMAN_REVIEW"


@dataclass
class ValidationResult:
    validator_name: str
    is_valid: bool
    error: str | None = None

    def __str__(self) -> str:
        if self.is_valid:
            return f"  ✅ {self.validator_name}"
        return f"  ❌ {self.validator_name}: {self.error}"


@dataclass
class KernelDecision:
    decision: Decision
    policy_id: str
    policy_version: str
    results: list[ValidationResult] = field(default_factory=list)
    approved_count: int = 0
    rejected_count: int = 0
    pending_count: int = 0
    errors: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def print_summary(self) -> None:
        icon = "✅" if self.decision == Decision.APPROVED else "❌"
        print(f"{icon} Kernel {self.decision.value} | Policy: {self.policy_id}@{self.policy_version}")
        print(f"   Approved: {self.approved_count} | Rejected: {self.rejected_count} | Pending: {self.pending_count}")
        for r in self.results:
            print(r)

    def has_failures(self) -> bool:
        return any(not r.is_valid for r in self.results)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class Kernel:
    """Executor determinístico de políticas do Kernel.

    Usage:
        kernel = Kernel()
        decision = kernel.evaluate(item, policy_id="KERNEL-POLICY-001")
        if decision.decision == Decision.REJECTED:
            sys.exit(2)
    """

    def __init__(self, fail_closed: bool = True) -> None:
        self.fail_closed = fail_closed
        self.registry = PolicyRegistry()
        _ensure_validators()

    def evaluate(self, item: dict[str, Any], policy_id: str) -> KernelDecision:
        """Avalia um item contra uma política do Kernel."""
        _ensure_validators()
        policy = get_policy(policy_id)
        validators = policy.validators

        if not validators:
            return KernelDecision(
                decision=Decision.REJECTED,
                policy_id=policy_id,
                policy_version=policy.version,
                errors=["Nenhum validador registrado na política. Fail-closed."],
            )

        results: list[ValidationResult] = []
        for vname in validators:
            if vname not in VALIDATORS:
                # Validador registrado na política mas não implementado → fail-closed
                return KernelDecision(
                    decision=Decision.REJECTED,
                    policy_id=policy_id,
                    policy_version=policy.version,
                    errors=[f"Validador '{vname}' referenciado na política mas não implementado."],
                )

            validator = VALIDATORS[vname]
            is_valid, error = validator.validate(item)
            results.append(ValidationResult(validator_name=vname, is_valid=is_valid, error=error))

        failed = [r for r in results if not r.is_valid]
        pending = [r for r in results if r.is_valid and r.validator_name == "human_review_validator"]

        if failed:
            decision = Decision.REJECTED
        elif pending:
            decision = Decision.PENDING_REVIEW
        else:
            decision = Decision.APPROVED

        return KernelDecision(
            decision=decision,
            policy_id=policy_id,
            policy_version=policy.version,
            results=results,
            approved_count=len([r for r in results if r.is_valid]),
            rejected_count=len(failed),
            pending_count=len(pending),
        )

    def evaluate_batch(
        self, items: list[dict[str, Any]], policy_id: str
    ) -> KernelDecision:
        """Avalia lote de itens contra uma política."""
        _ensure_validators()
        policy = get_policy(policy_id)
        validators = policy.validators

        if not validators:
            return KernelDecision(
                decision=Decision.REJECTED,
                policy_id=policy_id,
                policy_version=policy.version,
                errors=["Nenhum validador registrado na política. Fail-closed."],
            )

        all_results: list[ValidationResult] = []
        approved_count = 0
        rejected_count = 0
        pending_count = 0

        for item in items:
            for vname in validators:
                if vname not in VALIDATORS:
                    return KernelDecision(
                        decision=Decision.REJECTED,
                        policy_id=policy_id,
                        policy_version=policy.version,
                        errors=[f"Validador '{vname}' não implementado."],
                    )
                validator = VALIDATORS[vname]
                is_valid, error = validator.validate(item)
                all_results.append(ValidationResult(validator_name=vname, is_valid=is_valid, error=error))
                if is_valid:
                    approved_count += 1
                elif vname == "human_review_validator":
                    pending_count += 1
                else:
                    rejected_count += 1

        failed = [r for r in all_results if not r.is_valid]
        pending = [r for r in all_results if r.is_valid and r.validator_name == "human_review_validator"]

        if failed:
            decision = Decision.REJECTED
        elif pending:
            decision = Decision.PENDING_REVIEW
        else:
            decision = Decision.APPROVED

        return KernelDecision(
            decision=decision,
            policy_id=policy_id,
            policy_version=policy.version,
            results=all_results[: len(validators)],
            approved_count=approved_count,
            rejected_count=rejected_count,
            pending_count=pending_count,
        )

    def check_policy(self, policy_id: str) -> tuple[int, str]:
        """Confere se a política está implementada e se os testes dos validadores passam.

        Não cria diretórios. Exit 2 é fail-closed.
        """
        _ensure_validators()
        try:
            policy = get_policy(policy_id)
        except (KeyError, FileNotFoundError) as exc:
            return 2, f"Política não encontrada: {policy_id}: {exc}"

        if not policy.validators:
            return 2, f"Política {policy_id} não tem validadores. Fail-closed."

        missing = [v for v in policy.validators if v not in VALIDATORS]
        if missing:
            return 2, f"Validadores ausentes: {missing}. Fail-closed."

        for vname in policy.validators:
            validator = VALIDATORS[vname]
            if not hasattr(validator, "run_tests"):
                return 2, f"Validador '{vname}' sem test_suite. Fail-closed."
            if vname not in _validator_tests:
                _validator_tests[vname] = bool(validator.run_tests())
            if not _validator_tests[vname]:
                return 2, f"Validador '{vname}' falhou nos testes. Fail-closed."

        return 0, (
            f"Gate {policy_id}@{policy.version}: "
            f"{len(policy.validators)} validadores OK"
        )

    def gate(self, policy_id: str) -> int:
        """Executa gate para uma política. Retorna exit code."""
        code, message = self.check_policy(policy_id)
        if code != 0:
            typer.secho(f"❌ {message}", fg=typer.colors.RED)
            return 2

        policy = get_policy(policy_id)
        output_dir = REPO_ROOT / policy.atoms_output
        if not output_dir.exists():
            typer.secho(f"⚠️  Criando diretório de saída: {output_dir}", fg=typer.colors.YELLOW)
            output_dir.mkdir(parents=True, exist_ok=True)

        typer.secho(f"✅ {message}", fg=typer.colors.GREEN)
        typer.secho(f"✅ Gate {policy_id}: TODOS OS VALIDADORES APROVADOS", fg=typer.colors.GREEN)
        return 0

    def list_policies(self) -> None:
        """Lista todas as políticas registradas."""
        policies = self.registry.list_policies()
        if not policies:
            typer.secho("Nenhuma política registrada.", fg=typer.colors.YELLOW)
            return
        typer.secho(f"{len(policies)} políticas registradas:\n", fg=typer.colors.CYAN)
        for p in policies:
            typer.echo(f"  {p.id}  ({p.name})")
            typer.echo(f"    Validadores: {', '.join(p.validators)}")
            typer.echo(f"    WO required: {p.wo_required} | Revisão humana: {p.requires_human_review}")
            typer.echo()
