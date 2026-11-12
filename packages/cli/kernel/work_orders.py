"""Work orders submetidas pelo Kernel.

Nenhuma atividade de obtenção ou atomização grava arquivo sem uma WO
cujo authorized_by é o próprio Kernel e cuja política passou no gate.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kernel.policy_registry import KernelPolicy

SCHEMA = "CE-WO-AUTHORIZATION-1.0.0"
ACTIVITIES = frozenset({"obter", "atomizar"})
_WO_FILE = re.compile(r"^autorizacao_WO-(\d+)\.json$")


class WorkOrderRejected(Exception):
    """O Kernel recusou submeter ou aceitar a WO."""


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {k: v for k, v in data.items() if k != "_path"}
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def _read(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise WorkOrderRejected(f"WO ilegível: {path.name}")
    data["_path"] = str(path)
    return data


def wo_directory(wo_dir: Path | None) -> Path:
    return Path(wo_dir) if wo_dir is not None else repo_root() / "data" / "legado"


def _next_seq(directory: Path) -> int:
    highest = 0
    if directory.exists():
        for path in directory.glob("autorizacao_WO-*.json"):
            match = _WO_FILE.match(path.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return highest + 1


def find_work_order(
    directory: Path, policy_id: str, activity: str, target: str
) -> dict[str, Any] | None:
    if not directory.exists():
        return None
    found: dict[str, Any] | None = None
    for path in sorted(directory.glob("autorizacao_WO-*.json")):
        try:
            data = _read(path)
        except (OSError, json.JSONDecodeError, WorkOrderRejected):
            continue
        if (
            data.get("policy_id") == policy_id
            and data.get("activity") == activity
            and data.get("target") == target
        ):
            found = data
    return found


def create_work_order(
    *,
    policy: KernelPolicy,
    activity: str,
    target: str,
    rationale: str,
    wo_dir: Path | None = None,
    evidence_reference: str | None = None,
) -> dict[str, Any]:
    """Cria a WO, ou devolve a já submetida para a mesma política, atividade e alvo."""
    if activity not in ACTIVITIES:
        raise WorkOrderRejected(f"Atividade não permitida pelo Kernel: {activity}")
    if not isinstance(target, str) or not target.strip() or len(target) > 200:
        raise WorkOrderRejected("Alvo da WO ausente ou longo demais.")
    directory = wo_directory(wo_dir)
    existing = find_work_order(directory, policy.id, activity, target.strip())
    if existing:
        return existing

    seq = _next_seq(directory)
    timestamp = _now()
    wo_id = f"CE-WO-{datetime.now(timezone.utc).strftime('%Y%m%d')}-WO-{seq:04d}"
    data: dict[str, Any] = {
        "schema": SCHEMA,
        "wo_id": wo_id,
        "slug": f"{activity}-{policy.id.lower()}",
        "status": "SUBMITTED",
        "rationale": rationale,
        "authorized_by": "kernel",
        "timestamp": timestamp,
        "policy_id": policy.id,
        "policy_version": policy.version,
        "activity": activity,
        "target": target.strip(),
        "conditions": [
            "Política validada pelo Kernel antes da submissão",
            "Atividade recusada sem esta WO",
            "Fail-closed: credencial ausente ou política divergente bloqueia a atividade",
            "Nenhum átomo é gravado sem a validação da política",
        ],
        "evidence_reference": evidence_reference,
        "motivo": None,
        "historico": [{"status": "SUBMITTED", "timestamp": timestamp, "por": "kernel"}],
    }
    path = directory / f"autorizacao_WO-{seq:04d}.json"
    _write(path, data)
    data["_path"] = str(path)
    return data


def update_work_order(path: str | Path, **fields: Any) -> dict[str, Any]:
    """Atualiza uma WO submetida pelo Kernel. Não troca o autor."""
    if fields.get("authorized_by") not in (None, "kernel"):
        raise WorkOrderRejected("O Kernel não reatribui a autoria da WO.")
    fields.pop("authorized_by", None)
    fields.pop("_path", None)
    data = _read(Path(path))
    if data.get("authorized_by") != "kernel":
        raise WorkOrderRejected("WO não foi submetida pelo Kernel.")
    if data.get("schema") != SCHEMA:
        raise WorkOrderRejected("Schema de WO divergente.")
    status = fields.get("status")
    if status and status != data.get("status"):
        historico = list(data.get("historico") or [])
        historico.append(
            {
                "status": status,
                "timestamp": _now(),
                "por": "kernel",
                "motivo": fields.get("motivo"),
            }
        )
        data["historico"] = historico
    data.update(fields)
    data["timestamp"] = _now()
    _write(Path(path), data)
    data["_path"] = str(path)
    return data


def require_open(wo: dict[str, Any], policy_id: str, activity: str) -> None:
    """Recusa a atividade se a WO não estiver aberta e submetida pelo Kernel."""
    if wo.get("authorized_by") != "kernel":
        raise WorkOrderRejected("Atividade recusada: WO não submetida pelo Kernel.")
    if wo.get("schema") != SCHEMA:
        raise WorkOrderRejected("Atividade recusada: schema de WO divergente.")
    if wo.get("policy_id") != policy_id or wo.get("activity") != activity:
        raise WorkOrderRejected("Atividade recusada: WO não cobre esta política e atividade.")
    if wo.get("status") not in {"SUBMITTED", "PREAUTHORIZED"}:
        raise WorkOrderRejected(
            f"Atividade recusada: WO {wo.get('wo_id')} está {wo.get('status')}."
        )
