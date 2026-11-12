"""Submissão de WO pelo Kernel — uma atividade, uma decisão.

O Kernel não cria política e não adquire bytes. Ele lê as políticas em
``contracts/policies/`` e o registry de raízes Drive, grava uma WO e
recusa obter ou atomizar quando o modelo de política não autoriza a
atividade para a pasta pedida.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ACTIVITIES = ("obter", "atomizar")
FOLDER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,128}$")
FOLDER_KEYS = frozenset({"drive_folder_id", "folder_id", "drive_folder"})
SCHEMA = "CE-WO-AUTHORIZATION-1.0.0"
SUBMITTED_BY = "kernel"
TARGET_FOLDER = "1l0x3dQ0DbWwO7N6rfhZ3KdGuKkMnFHXC"

REPO_ROOT = Path(__file__).resolve().parents[3]
POLICIES_DIR = REPO_ROOT / "contracts" / "policies"
ROOTS_PATH = REPO_ROOT / "config" / "drive_inventory_roots_20261016.json"
WO_DIR_REL = Path("data") / "legado"

class KernelWorkOrderError(RuntimeError):
    """Falha fail-closed antes de qualquer obtenção ou atomização."""


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise KernelWorkOrderError(f"JSON inválido em {path}: {exc}") from exc
    except OSError as exc:
        raise KernelWorkOrderError(f"não foi possível ler {path}: {exc}") from exc


def _collect_bound_folder_ids(node: Any, found: set[str]) -> None:
    """Coleta ids só de campos que vinculam uma pasta."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key in FOLDER_KEYS:
                if isinstance(value, str):
                    found.add(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            found.add(item)
                        elif isinstance(item, dict) and isinstance(item.get("id"), str):
                            found.add(item["id"])
                elif isinstance(value, dict) and isinstance(value.get("id"), str):
                    found.add(value["id"])
            else:
                _collect_bound_folder_ids(value, found)
    elif isinstance(node, list):
        for item in node:
            _collect_bound_folder_ids(item, found)


def load_policies(policies_dir: Path) -> list[dict[str, Any]]:
    if not policies_dir.is_dir():
        raise KernelWorkOrderError(f"diretório de políticas ausente: {policies_dir}")
    policies: list[dict[str, Any]] = []
    for path in sorted(policies_dir.glob("KERNEL-POLICY-*.json")):
        data = _load_json(path)
        if not isinstance(data, dict) or not isinstance(data.get("id"), str) or not data["id"]:
            raise KernelWorkOrderError(f"política sem id: {path}")
        policies.append(data)
    if not policies:
        raise KernelWorkOrderError("nenhuma KERNEL-POLICY registrada; fail-closed")
    return policies


def binding_policy_ids(
    policies: list[dict[str, Any]],
    folder_id: str,
    repo_root: Path,
) -> list[str]:
    """Políticas cujo JSON ou contrato de fonte vincula esta pasta."""
    hits: list[str] = []
    for policy in policies:
        bound: set[str] = set()
        _collect_bound_folder_ids(policy, bound)
        source = policy.get("source_contract")
        if isinstance(source, str) and source:
            source_path = repo_root / source
            if source_path.is_file():
                _collect_bound_folder_ids(_load_json(source_path), bound)
            else:
                raise KernelWorkOrderError(
                    f"source_contract ausente para {policy['id']}: {source}"
                )
        if folder_id in bound:
            hits.append(str(policy["id"]))
    return hits


def load_drive_registry(roots_path: Path) -> tuple[list[str], list[str]]:
    if not roots_path.is_file():
        raise KernelWorkOrderError(f"registry de raízes Drive ausente: {roots_path}")
    document = _load_json(roots_path)
    if not isinstance(document, dict):
        raise KernelWorkOrderError("registry de raízes Drive não é um objeto JSON")
    roots = document.get("roots")
    if not isinstance(roots, list) or not roots:
        raise KernelWorkOrderError("registry de raízes Drive vazio; fail-closed")
    ids: list[str] = []
    for root in roots:
        if not isinstance(root, dict) or not isinstance(root.get("id"), str) or not root["id"]:
            raise KernelWorkOrderError("raiz Drive sem id; fail-closed")
        ids.append(root["id"])
    if len(ids) != len(set(ids)):
        raise KernelWorkOrderError("raízes Drive duplicadas; fail-closed")
    restrictions = document.get("restrictions") or []
    if not isinstance(restrictions, list) or not all(isinstance(item, str) for item in restrictions):
        raise KernelWorkOrderError("restrictions do registry Drive inválidas")
    return ids, list(restrictions)


def _credential_present(env: Mapping[str, str]) -> bool:
    return bool(env.get("GDRIVE_SA_KEY") or env.get("DRIVE_ACCESS_TOKEN"))


def decision_motivos(
    *,
    activity: str,
    folder_id: str,
    registered_ids: list[str],
    restrictions: list[str],
    binding: list[str],
    credential_present: bool,
) -> list[str]:
    motivos: list[str] = [
        "O modelo KernelPolicy não declara pasta Drive nem permissão de obter ou atomizar; "
        "nenhuma política carregada autoriza esta atividade."
    ]
    if not binding:
        motivos.append(
            "Nenhuma política nem contrato de fonte vincula esta pasta pelos campos "
            "drive_folder_id, folder_id ou drive_folder."
        )
    if folder_id not in registered_ids:
        motivos.append(
            "A pasta não está no registry canônico config/drive_inventory_roots_20261016.json."
        )
    motivos.append(
        "O inventário Drive registra hash_status BYTES_NOT_ACQUIRED; o Kernel não adquire bytes."
    )
    if activity == "obter" and not credential_present:
        motivos.append(
            "Credencial ausente: GDRIVE_SA_KEY e DRIVE_ACCESS_TOKEN não estão configuradas."
        )
    if activity == "atomizar" and (
        "NO_CANONICAL_PROMOTION" in restrictions or "NO_PUBLICATION" in restrictions
    ):
        motivos.append(
            "O registry Drive aplica NO_CANONICAL_PROMOTION e NO_PUBLICATION; "
            "atomização canônica recusada."
        )
    return motivos


def _semantic(document: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in document.items() if key != "timestamp"}


def wo_id_for(activity: str, folder_id: str) -> str:
    return f"CE-WO-{activity.upper()}-{folder_id}"


def submit_work_order(
    *,
    activity: str,
    folder_id: str,
    repo_root: Path | None = None,
    policies_dir: Path | None = None,
    roots_path: Path | None = None,
    wo_dir: Path | None = None,
    env: Mapping[str, str] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Grava a WO da atividade. Não baixa arquivo e não escreve átomo."""
    if activity not in ACTIVITIES:
        raise KernelWorkOrderError(
            f"atividade '{activity}' não é executável; use uma de {ACTIVITIES}"
        )
    if not FOLDER_ID_RE.fullmatch(folder_id):
        raise KernelWorkOrderError("folder_id inválido; fail-closed")

    root = (repo_root or REPO_ROOT).resolve()
    policies = load_policies(policies_dir or (root / "contracts" / "policies"))
    registered_ids, restrictions = load_drive_registry(
        roots_path or (root / "config" / "drive_inventory_roots_20261016.json")
    )
    binding = binding_policy_ids(policies, folder_id, root)
    environment = env if env is not None else os.environ
    credential_present = _credential_present(environment)
    motivos = decision_motivos(
        activity=activity,
        folder_id=folder_id,
        registered_ids=registered_ids,
        restrictions=restrictions,
        binding=binding,
        credential_present=credential_present,
    )
    if not motivos:
        raise KernelWorkOrderError(
            "predicado de autorização vazio sem executor de bytes; fail-closed"
        )

    moment = now or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    document: dict[str, Any] = {
        "schema": SCHEMA,
        "wo_id": wo_id_for(activity, folder_id),
        "slug": f"drive_{activity}_{folder_id}",
        "tarefa": activity,
        "folder_id": folder_id,
        "policy_ids_binding_folder": binding,
        "policies_consulted": [str(policy["id"]) for policy in policies],
        "registered_drive_roots": registered_ids,
        "status": "BLOQUEADO",
        "estado": "BLOQUEADO",
        "motivo": motivos[0],
        "motivos": motivos,
        "submitted_by": SUBMITTED_BY,
        "authorized_by": None,
        "credential_present": credential_present,
        "bytes_acquired": False,
        "atoms_written": 0,
        "restrictions_applied": restrictions,
        "timestamp": moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    target_dir = wo_dir or (root / WO_DIR_REL)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"autorizacao_{document['wo_id']}.json"
    if target.exists():
        existing = _load_json(target)
        if not isinstance(existing, dict):
            raise KernelWorkOrderError(f"WO existente inválida: {target}")
        if _semantic(existing) == _semantic(document):
            return existing
    payload = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(target)
    return document


def submit_folder_activities(
    folder_id: str,
    **kwargs: Any,
) -> list[dict[str, Any]]:
    """Submete uma WO de obter e uma WO de atomizar, nesta ordem."""
    return [
        submit_work_order(activity=activity, folder_id=folder_id, **kwargs)
        for activity in ACTIVITIES
    ]


def _print_document(document: Mapping[str, Any]) -> None:
    print(
        f"{document['wo_id']} estado={document['estado']} "
        f"bytes_acquired={str(document['bytes_acquired']).lower()} "
        f"atoms_written={document['atoms_written']}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Kernel submete WO e recusa obter/atomizar sem política."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    submit = sub.add_parser("submit", help="Submeter WO para uma atividade")
    submit.add_argument("--activity", required=True, choices=ACTIVITIES)
    submit.add_argument("--folder-id", required=True)

    folder = sub.add_parser(
        "submit-folder",
        help="Submeter WO de obter e de atomizar para uma pasta",
    )
    folder.add_argument("--folder-id", required=True)

    args = parser.parse_args(argv)
    try:
        if args.command == "submit":
            documents = [
                submit_work_order(activity=args.activity, folder_id=args.folder_id)
            ]
        else:
            documents = submit_folder_activities(args.folder_id)
    except KernelWorkOrderError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        return 2

    for document in documents:
        _print_document(document)
    if any(document["estado"] != "AUTORIZADO" for document in documents):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
