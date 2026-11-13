"""Ordens de trabalho emitidas somente pelo Kernel.

Nada é baixado, atomizado ou migrado sem uma WO cujo
`submission_sha256` foi calculado por este módulo.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "CE-WO-KERNEL-1.0.0"
SUBMITTED_BY = "kernel"
FOLDER_RE = re.compile(r"^[A-Za-z0-9_-]{10,80}$")
ACTIVITIES = frozenset({"obter", "atomizar"})


class WorkOrderError(RuntimeError):
    """WO ausente, forjada ou incompatível com a atividade. Fail-closed."""


def wo_directory(repo_root: Path) -> Path:
    return repo_root / "data" / "kernel" / "wo"


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    body = {k: v for k, v in payload.items() if k != "submission_sha256"}
    raw = json.dumps(body, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return raw.encode("utf-8")


def submission_sha256(payload: dict[str, Any]) -> str:
    return hashlib.sha256(_canonical_bytes(payload)).hexdigest()


def make_wo_id(activity: str, folder_id: str, day: str, policy_id: str | None) -> str:
    material = f"{activity}|{folder_id}|{policy_id or '-'}|{day}"
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]
    stamp = day.replace("-", "")
    return f"CE-WO-{stamp}-{activity.upper()}-{digest}"


def wo_path(repo_root: Path, wo_id: str) -> Path:
    if "/" in wo_id or wo_id in (".", ".."):
        raise WorkOrderError(f"wo_id inválido: {wo_id}")
    return wo_directory(repo_root) / f"{wo_id}.json"


def save_wo(repo_root: Path, payload: dict[str, Any]) -> Path:
    payload["schema"] = SCHEMA
    payload["submitted_by"] = SUBMITTED_BY
    payload["submission_sha256"] = submission_sha256(payload)
    path = wo_path(repo_root, payload["wo_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def load_wo(repo_root: Path, wo_id: str) -> dict[str, Any]:
    path = wo_path(repo_root, wo_id)
    if not path.exists():
        raise WorkOrderError(f"WO não encontrada: {wo_id}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    verify_wo(payload)
    return payload


def verify_wo(payload: dict[str, Any]) -> None:
    if not isinstance(payload, dict):
        raise WorkOrderError("WO não é um objeto JSON")
    if payload.get("schema") != SCHEMA:
        raise WorkOrderError("schema de WO não reconhecido pelo Kernel")
    if payload.get("submitted_by") != SUBMITTED_BY:
        raise WorkOrderError("WO não foi submetida pelo Kernel")
    expected = payload.get("submission_sha256")
    if not isinstance(expected, str) or expected != submission_sha256(payload):
        raise WorkOrderError("submission_sha256 da WO não confere; fail-closed")
    if payload.get("activity") not in ACTIVITIES:
        raise WorkOrderError("atividade da WO não é obter nem atomizar")


def require_wo(
    repo_root: Path,
    wo_id: str,
    *,
    activity: str,
    folder_id: str,
    policy_id: str | None = None,
) -> dict[str, Any]:
    payload = load_wo(repo_root, wo_id)
    if payload.get("activity") != activity:
        raise WorkOrderError(
            f"WO {wo_id} é atividade {payload.get('activity')}, exigida {activity}"
        )
    if payload.get("folder_id") != folder_id:
        raise WorkOrderError(f"WO {wo_id} não autoriza a pasta {folder_id}")
    if policy_id is not None and payload.get("policy_id") != policy_id:
        raise WorkOrderError(f"WO {wo_id} não autoriza a política {policy_id}")
    if payload.get("status") == "BLOQUEADO":
        raise WorkOrderError(f"WO {wo_id} está BLOQUEADO: {payload.get('motivo')}")
    return payload


def submit_wo(
    repo_root: Path,
    *,
    activity: str,
    folder_id: str,
    policy_id: str | None,
    now: datetime | None = None,
    status: str = "SUBMITTED",
    motivo: str | None = None,
) -> dict[str, Any]:
    """Emite ou atualiza a WO determinística desta atividade.

    O identificador depende da atividade, da pasta, da política e do dia UTC.
    Uma WO já PASS no mesmo dia é reutilizada sem reiniciar a atividade.
    """
    if activity not in ACTIVITIES:
        raise WorkOrderError(f"atividade não permitida: {activity}")
    if not FOLDER_RE.match(folder_id):
        raise WorkOrderError(f"folder_id inválido: {folder_id}")
    clock = now or datetime.now(timezone.utc)
    if clock.tzinfo is None:
        clock = clock.replace(tzinfo=timezone.utc)
    day = clock.astimezone(timezone.utc).date().isoformat()
    wo_id = make_wo_id(activity, folder_id, day, policy_id)
    path = wo_path(repo_root, wo_id)
    attempts = 1
    events: list[dict[str, Any]] = []
    if path.exists():
        current = json.loads(path.read_text(encoding="utf-8"))
        verify_wo(current)
        if current.get("status") == "PASS" and status == "SUBMITTED":
            return current
        attempts = int(current.get("attempts") or 0) + 1
        events = list(current.get("events") or [])
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "wo_id": wo_id,
        "submitted_by": SUBMITTED_BY,
        "activity": activity,
        "folder_id": folder_id,
        "policy_id": policy_id,
        "status": status,
        "motivo": motivo,
        "attempts": attempts,
        "day": day,
        "updated_at": clock.astimezone(timezone.utc).isoformat(),
        "events": events + [{"step": "submit", "activity": activity, "status": status}],
    }
    save_wo(repo_root, payload)
    return payload


def update_wo(repo_root: Path, payload: dict[str, Any], **changes: Any) -> dict[str, Any]:
    verify_wo(payload)
    updated = dict(payload)
    updated.update(changes)
    if changes.get("status") and changes.get("status") != payload.get("status"):
        events = list(updated.get("events") or [])
        events.append(
            {
                "step": "status",
                "status": changes["status"],
                "motivo": changes.get("motivo"),
            }
        )
        updated["events"] = events
    save_wo(repo_root, updated)
    return updated
