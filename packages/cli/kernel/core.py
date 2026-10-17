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

# Import tardio para evitar circular — cada validador se auto-registra
def _lazy_import_validators():
    from validators import (
        Sha256Validator, NormAtomIdValidator, TextoLengthValidator,
        UrlValidator, AtomoSchemaValidator,
        cid10_validator, cid11_validator, mesh_validator,
        cvx_validator, schema_validator, loinc_validator,
        ncm_validator, catmat_validator, human_review_validator,
    )
    return locals()

VALIDATORS: dict[str, Any] = {}
_validator_imported = False

def _ensure_validators():
    global _validator_imported, VALIDATORS
    if not _validator_imported:
        ctx = _lazy_import_validators()
        # Extrai validadores concretos (não classes, instâncias)
        for k, v in ctx.items():
            if k.endswith("_validator") and hasattr(v, "validate"):
                VALIDATORS[k] = v
        _validator_imported = True

from kernel.policy_registry import get_policy, PolicyRegistry


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
            results=all_results,
            approved_count=approved_count,
            rejected_count=rejected_count,
            pending_count=pending_count,
        )

    def gate(self, policy_id: str) -> int:
        """Executa gate para uma política. Retorna exit code."""
        _ensure_validators()
        try:
            policy = get_policy(policy_id)
        except (KeyError, FileNotFoundError) as exc:
            typer.secho(f"❌ Política não encontrada: {policy_id}", fg=typer.colors.RED)
            typer.secho(f"   {exc}", fg=typer.colors.RED)
            return 2

        if not policy.validators:
            typer.secho(f"❌ Política {policy_id} não tem validadores. Fail-closed.", fg=typer.colors.RED)
            return 2

        missing = [v for v in policy.validators if v not in VALIDATORS]
        if missing:
            typer.secho(f"❌ Validadores ausentes: {missing}. Fail-closed.", fg=typer.colors.RED)
            return 2

        typer.secho(f"✅ Gate {policy_id}@{policy.version}: {len(policy.validators)} validadores OK", fg=typer.colors.GREEN)

        for vname in policy.validators:
            validator = VALIDATORS[vname]
            if hasattr(validator, "run_tests"):
                if not validator.run_tests():
                    typer.secho(f"❌ Validador '{vname}' falhou nos testes. Fail-closed.", fg=typer.colors.RED)
                    return 2
                typer.secho(f"  ✅ {vname}: {len(validator.test_suite())} testes OK", fg=typer.colors.GREEN)
            else:
                typer.secho(f"❌ Validador {vname} sem run_tests. Fail-closed.", fg=typer.colors.RED)
                return 2

        output_dir = Path(policy.atoms_output)
        if not output_dir.exists():
            typer.secho(f"⚠️  Criando diretório de saída: {output_dir}", fg=typer.colors.YELLOW)
            output_dir.mkdir(parents=True, exist_ok=True)

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
