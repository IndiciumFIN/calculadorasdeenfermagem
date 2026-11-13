"""WO submetida exclusivamente pelo Kernel.

Nada é baixado, atomizado ou migrado sem este registro.
O identificador é determinístico: a mesma atividade e a mesma pasta
reutilizam o mesmo arquivo e apenas acrescentam histórico.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SCHEMA = "CE-WO-AUTHORIZATION-1.0.0"
TAREFAS = frozenset({"obter", "atomizar"})
ESTADOS = frozenset({"SUBMITTED", "BLOQUEADO", "EXECUTADO"})
RESTRICTIONS = [
    "READ_ONLY",
    "NO_DELETE",
    "NO_PUBLICATION",
    "NO_CANONICAL_PROMOTION",
]


def work_order_id(tarefa: str, folder_id: str) -> str:
    if tarefa not in TAREFAS:
        raise ValueError(f"tarefa inválida: {tarefa}")
    digest = hashlib.sha256(f"{tarefa}|{folder_id}".encode("utf-8")).hexdigest()[:12]
    return f"CE-WO-{tarefa.upper()}-{digest}"


def work_order_path(root: Path, wo_id: str) -> Path:
    if "/" in wo_id or wo_id in ("", ".", ".."):
        raise ValueError("wo_id inválido")
    path = (root / "data" / "legado" / f"autorizacao_WO-{wo_id}.json").resolve()
    legado = (root / "data" / "legado").resolve()
    if legado not in path.parents:
        raise ValueError("WO fora de data/legado")
    return path


def load_work_order(root: Path, wo_id: str) -> dict[str, Any] | None:
    path = work_order_path(root, wo_id)
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("WO ilegível")
    return data


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def submit_work_order(
    *,
    root: Path,
    tarefa: str,
    folder_id: str,
    estado: str,
    motivo: str,
    sha256_fonte: str | None = None,
    politicas_validas: list[str] | None = None,
    depends_on: str | None = None,
    contagens: dict[str, Any] | None = None,
    acao_necessaria: str | None = None,
    clock: Callable[[], str] | None = None,
) -> dict[str, Any]:
    """Grava a WO. submitted_by é sempre o kernel."""
    if tarefa not in TAREFAS:
        raise ValueError(f"tarefa inválida: {tarefa}")
    if estado not in ESTADOS:
        raise ValueError(f"estado inválido: {estado}")
    if estado == "EXECUTADO" and (
        not isinstance(sha256_fonte, str) or len(sha256_fonte) != 64
    ):
        raise ValueError("WO EXECUTADO sem sha256_fonte")
    if sha256_fonte is not None and (
        not isinstance(sha256_fonte, str) or len(sha256_fonte) != 64
    ):
        raise ValueError("sha256_fonte inválido")

    wo_id = work_order_id(tarefa, folder_id)
    path = work_order_path(root, wo_id)
    existing = load_work_order(root, wo_id) if path.is_file() else None
    if existing is not None:
        if existing.get("submitted_by") != "kernel":
            raise ValueError("WO existente não foi submetida pelo kernel")
        if existing.get("tarefa") != tarefa or existing.get("pasta_drive_id") != folder_id:
            raise ValueError("WO existente diverge da atividade")
        historico = list(existing.get("historico") or [])
    else:
        historico = []

    timestamp = (clock or _now)()
    historico.append(
        {
            "timestamp": timestamp,
            "estado": estado,
            "motivo": motivo,
            "sha256_fonte": sha256_fonte,
        }
    )
    tentativas = sum(1 for item in historico if item.get("estado") != "SUBMITTED")
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "wo_id": wo_id,
        "tarefa": tarefa,
        "lote": f"drive_{folder_id}",
        "pasta_drive_id": folder_id,
        "estado": estado,
        "submitted_by": "kernel",
        "motivo": motivo,
        "sha256_fonte": sha256_fonte,
        "tentativas": tentativas,
        "politicas_validas": list(politicas_validas or []),
        "depends_on": depends_on,
        "contagens": contagens or {},
        "acao_necessaria": acao_necessaria,
        "timestamp": timestamp,
        "restrictions": list(RESTRICTIONS),
        "historico": historico,
    }
    _atomic_write(path, payload)
    return payload
