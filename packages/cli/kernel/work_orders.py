"""Submissão de WO pelo Kernel.

O Kernel não escolhe a tarefa. Ele registra a WO, congela o gate das
políticas e recusa execução quando nenhuma política passa.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from packages.cli.kernel.core import VALIDATORS, _ensure_validators
from packages.cli.kernel.policy_registry import get_policy, list_policies

SCHEMA = "CE-WO-AUTHORIZATION-1.0.0"
TASKS = frozenset({"obter", "atomizar", "validar"})
WO_ID_RE = re.compile(r"^CE-WO-[A-Za-z0-9_-]{8,180}$")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def _read_wo(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError(f"WO ilegível: {path.name}")
    return data


def assess_policy(policy_id: str) -> dict[str, Any]:
    """Gate de uma política. Não cria diretório e não promove átomo."""
    _ensure_validators()
    try:
        policy = get_policy(policy_id)
    except KeyError as exc:
        return {"policy_id": policy_id, "passed": False, "reason": str(exc)}

    source = Path(policy.source_contract)
    if not source.is_file():
        repo_source = Path(__file__).resolve().parents[3] / policy.source_contract
        source = repo_source
    if not source.is_file():
        return {
            "policy_id": policy_id,
            "passed": False,
            "reason": f"source_contract ausente: {policy.source_contract}",
        }

    try:
        source_data = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"policy_id": policy_id, "passed": False, "reason": f"source_contract inválido: {exc}"}

    if source_data.get("kernel_policy_id") != policy_id:
        return {
            "policy_id": policy_id,
            "passed": False,
            "reason": "kernel_policy_id da fonte não confere",
        }

    missing = [name for name in policy.validators if name not in VALIDATORS]
    if missing:
        return {
            "policy_id": policy_id,
            "passed": False,
            "reason": f"validadores ausentes: {', '.join(missing)}",
        }

    for name in policy.validators:
        if not VALIDATORS[name].run_tests():
            return {
                "policy_id": policy_id,
                "passed": False,
                "reason": f"test_suite reprovou {name}",
            }

    return {
        "policy_id": policy_id,
        "passed": True,
        "reason": "gate",
        "version": policy.version,
        "atoms_output": policy.atoms_output,
        "quarentena_output": policy.quarentena_output,
        "fonte_slug": source_data.get("fonte_slug"),
        "wo_required": policy.wo_required,
        "requires_human_review": policy.requires_human_review,
    }


def assess_all_policies() -> dict[str, Any]:
    """Avalia todas as políticas registradas. Falha fechada se o registry estiver vazio."""
    policies = list_policies()
    if not policies:
        raise RuntimeError("Nenhuma política registrada. Fail-closed.")
    results = [assess_policy(policy.id) for policy in policies]
    valid = [item["policy_id"] for item in results if item["passed"]]
    return {
        "results": results,
        "valid_policy_ids": valid,
        "assessed_at": _now(),
    }


def wo_path(wo_dir: Path, wo_id: str) -> Path:
    if not WO_ID_RE.fullmatch(wo_id):
        raise ValueError(f"wo_id fora do padrão: {wo_id}")
    return wo_dir / f"autorizacao_{wo_id}.json"


def submit_work_order(
    *,
    wo_dir: Path,
    wo_id: str,
    task: str,
    slug: str,
    source: str,
    folder_id: str,
    gate: dict[str, Any],
    depends_on: str | None = None,
) -> dict[str, Any]:
    """Registra a WO. Reenvio do mesmo id devolve o arquivo existente."""
    if task not in TASKS:
        raise ValueError(f"tarefa não autorizada: {task}")
    if not gate or "valid_policy_ids" not in gate or "results" not in gate:
        raise ValueError("gate do Kernel ausente")

    path = wo_path(wo_dir, wo_id)
    if path.exists():
        current = _read_wo(path)
        if current.get("submitted_by") != "kernel":
            raise ValueError("WO existente não foi submetida pelo Kernel")
        if current.get("task") != task or current.get("folder_id") != folder_id:
            raise ValueError("WO existente aponta para outra atividade")
        return current

    valid = list(gate["valid_policy_ids"])
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "wo_id": wo_id,
        "task": task,
        "slug": slug,
        "status": "SUBMITTED",
        "submitted_by": "kernel",
        "source": source,
        "folder_id": folder_id,
        "policy_ids": valid,
        "policy_gate": [
            {"policy_id": item["policy_id"], "passed": item["passed"], "reason": item["reason"]}
            for item in gate["results"]
        ],
        "depends_on": depends_on,
        "timestamp": _now(),
        "atualizado_em": _now(),
        "tentativas": 0,
        "motivo": None,
        "resultado": None,
        "conditions": [
            "READ_ONLY",
            "NO_DELETE",
            "NO_PUBLICATION",
            "NO_CANONICAL_WITHOUT_PASSING_POLICY",
            "VIGENCIA_NASCE_NAO_VERIFICADO",
            "BYTES_BRUTOS_NAO_VERSIONADOS",
            "ZIP_CONTENTS_NOT_INSPECTED",
        ],
    }
    _atomic_write(path, payload)
    return payload


def record_execution(
    wo_dir: Path,
    wo_id: str,
    *,
    status: str,
    motivo: str | None = None,
    resultado: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Atualiza a WO submetida pelo Kernel. Não cria WO nova."""
    if status not in {"PASS", "BLOQUEADO", "SUBMITTED"}:
        raise ValueError(f"status não autorizado: {status}")
    path = wo_path(wo_dir, wo_id)
    if not path.exists():
        raise FileNotFoundError(f"WO não submetida: {wo_id}")
    current = _read_wo(path)
    if current.get("submitted_by") != "kernel":
        raise ValueError("somente WO submetida pelo Kernel pode ser atualizada por este comando")
    current["tentativas"] = int(current.get("tentativas") or 0) + 1
    current["status"] = status
    current["motivo"] = motivo
    current["resultado"] = resultado
    current["atualizado_em"] = _now()
    _atomic_write(path, current)
    return current
