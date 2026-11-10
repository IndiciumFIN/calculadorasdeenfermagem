"""Submissão de WO pelo Kernel. Fail-closed: sem autorização, não baixa e não atomiza.

Uma atividade (obter ou atomizar) só pode seguir quando o próprio Kernel grava
uma WO com status AUTORIZADA. Política ausente, pasta fora das raízes
registradas, credencial ausente ou gate de validadores indisponível bloqueiam
a atividade e deixam a WO versionada.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

FOLDER_ID = re.compile(r"^[A-Za-z0-9_-]{10,80}$")
ACTIVITIES = ("obter", "atomizar")
ROOTS_REL = "config/drive_inventory_roots_20261016.json"
KERNEL_IMPORTS = (
    "Sha256Validator",
    "NormAtomIdValidator",
    "TextoLengthValidator",
    "UrlValidator",
    "AtomoSchemaValidator",
    "cid10_validator",
    "cid11_validator",
    "mesh_validator",
    "cvx_validator",
    "schema_validator",
    "loinc_validator",
    "ncm_validator",
    "catmat_validator",
    "human_review_validator",
)


def repo_root_from_here() -> Path:
    return Path(__file__).resolve().parents[3]


def _now(now: datetime | None) -> str:
    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    return current.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON objeto esperado: {path}")
    return data


def load_policies(root: Path) -> list[dict[str, Any]]:
    directory = root / "contracts" / "policies"
    if not directory.is_dir():
        raise FileNotFoundError("contracts/policies ausente")
    policies: list[dict[str, Any]] = []
    for path in sorted(directory.glob("KERNEL-POLICY-*.json")):
        data = _read_json(path)
        if data.get("id") != path.stem:
            raise ValueError(f"id de política diverge do arquivo: {path.name}")
        policies.append(data)
    if not policies:
        raise ValueError("nenhuma política KERNEL-POLICY registrada")
    return policies


def load_roots(root: Path) -> set[str]:
    path = root / ROOTS_REL
    if not path.is_file():
        raise FileNotFoundError(f"raízes Drive ausentes: {ROOTS_REL}")
    data = _read_json(path)
    roots = data.get("roots")
    if not isinstance(roots, list) or not roots:
        raise ValueError("roots vazio no registro de pastas Drive")
    ids = []
    for item in roots:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("raiz Drive sem id")
        ids.append(item["id"])
    if len(ids) != len(set(ids)):
        raise ValueError("raízes Drive duplicadas")
    return set(ids)


def default_credentials() -> tuple[bool, str]:
    from packages.cli.drive_recursive_inventory import CredentialError, load_token

    try:
        load_token()
    except CredentialError as exc:
        return False, str(exc)
    return True, "credencial Drive presente; valor omitido"


def default_validator_gate() -> tuple[bool, str]:
    import packages.cli.validators as validators

    missing = [name for name in KERNEL_IMPORTS if not hasattr(validators, name)]
    if missing:
        return False, "gate do Kernel indisponível; validadores não exportados: " + ", ".join(missing)
    return True, "gate de validadores carregado"


def _authorizing(policies: list[dict[str, Any]], folder_id: str, roots: set[str]) -> list[str]:
    matched: list[str] = []
    for policy in policies:
        folders = policy.get("drive_folder_ids")
        if not isinstance(folders, list):
            continue
        if folder_id in folders and folder_id in roots and policy.get("fail_closed") is True:
            matched.append(str(policy["id"]))
    return matched


def _wo_paths(root: Path, activity: str, folder_id: str) -> tuple[str, Path, Path]:
    wo_id = f"CE-WO-DRIVE-{folder_id}-{activity.upper()}"
    legado = root / "data" / "legado" / f"autorizacao_{wo_id}.json"
    evidence = root / "evidence" / f"CE-WO-DRIVE-{folder_id}" / f"{activity}.json"
    return wo_id, legado, evidence


def _write_if_changed(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path.is_file() and path.read_text(encoding="utf-8") == rendered:
        return
    path.write_text(rendered, encoding="utf-8")


def submit_work_order(
    *,
    activity: str,
    folder_id: str,
    repo_root: Path | None = None,
    now: datetime | None = None,
    credential_check: Callable[[], tuple[bool, str]] | None = None,
    validator_gate: Callable[[], tuple[bool, str]] | None = None,
) -> tuple[int, dict[str, Any]]:
    """Grava a WO e devolve exit 0 só quando a atividade fica AUTORIZADA."""
    root = (repo_root or repo_root_from_here()).resolve()
    motivos: list[str] = []
    if activity not in ACTIVITIES:
        motivos.append("atividade desconhecida; aceitas: obter, atomizar")
    if not FOLDER_ID.fullmatch(folder_id or ""):
        motivos.append("folder_id inválido")

    policies: list[dict[str, Any]] = []
    roots: set[str] = set()
    try:
        policies = load_policies(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        motivos.append(f"políticas do Kernel ilegíveis: {exc}")
    try:
        roots = load_roots(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        motivos.append(f"raízes Drive ilegíveis: {exc}")

    if folder_id and roots and folder_id not in roots:
        motivos.append(f"pasta ausente das raízes registradas ({ROOTS_REL})")

    authorizing = _authorizing(policies, folder_id, roots) if policies and roots else []
    if policies and not authorizing and "folder_id inválido" not in motivos:
        motivos.append("nenhuma política registrada autoriza esta pasta em drive_folder_ids")

    creds_ok, creds_detail = (credential_check or default_credentials)()
    if activity == "obter" and not creds_ok:
        motivos.append(creds_detail)

    gate_ok, gate_detail = (validator_gate or default_validator_gate)()
    if not gate_ok:
        motivos.append(gate_detail)

    human = [
        str(policy["id"])
        for policy in policies
        if str(policy.get("id")) in authorizing
        and (policy.get("requires_human_review") is True or policy.get("wo_required") is True)
    ]
    if human:
        motivos.append("política exige revisão humana ou WO prévia; Kernel não se autoautoriza: " + ", ".join(human))

    if activity == "atomizar" and folder_id and FOLDER_ID.fullmatch(folder_id):
        obter_id, obter_path, _ = _wo_paths(root, "obter", folder_id)
        obter_status = None
        if obter_path.is_file():
            try:
                obter_status = _read_json(obter_path).get("status")
            except (OSError, ValueError, json.JSONDecodeError):
                obter_status = None
        if obter_status not in {"AUTORIZADA", "PASS"}:
            motivos.append(f"WO de obter {obter_id} não está AUTORIZADA")
        motivos.append("bytes não adquiridos; sha256 ausente")

    status = "AUTORIZADA" if not motivos else "BLOQUEADO"
    wo_id, legado, evidence = _wo_paths(root, activity if activity in ACTIVITIES else "rejeitada", folder_id or "invalido")
    timestamp = _now(now)
    decision: dict[str, Any] = {
        "schema": "CE-WO-AUTHORIZATION-1.0.0",
        "wo_id": wo_id,
        "slug": f"drive_{activity}_{folder_id or 'invalido'}",
        "submitted_by": "kernel",
        "authorized_by": "kernel",
        "status": status,
        "estado": status,
        "tarefa": activity,
        "lote": f"drive:{folder_id}",
        "folder_id": folder_id,
        "policy_ids_evaluated": [str(policy.get("id")) for policy in policies],
        "authorizing_policy_ids": authorizing,
        "motivo": "; ".join(motivos) if motivos else "política, raiz, credencial e gate conferidos",
        "motivos": motivos,
        "rationale": "Decisão fail-closed do Kernel antes de baixar ou atomizar.",
        "timestamp": timestamp,
        "bytes_acquired": False,
        "canonical_promoted": False,
        "conditions": [
            "Somente status AUTORIZADA libera a atividade",
            "A pasta precisa estar nas raízes registradas",
            "A política precisa declarar drive_folder_ids",
            "Obter exige credencial Drive sem gravar o segredo",
            "Atomizar exige WO de obter AUTORIZADA e bytes com sha256",
            "Nenhum átomo canônico é promovido por esta decisão",
        ],
        "restrictions": [
            "NO_DOWNLOAD",
            "NO_ATOMIZE",
            "NO_CANONICAL_PROMOTION",
            "NO_PUBLICATION",
            "NO_DELETE",
        ],
        "evidence_reference": evidence.relative_to(root).as_posix(),
    }
    if legado.is_file():
        try:
            previous = _read_json(legado)
        except (OSError, ValueError, json.JSONDecodeError):
            previous = {}
        comparable = {"timestamp"}
        if {k: v for k, v in previous.items() if k not in comparable} == {
            k: v for k, v in decision.items() if k not in comparable
        }:
            decision["timestamp"] = previous.get("timestamp", timestamp)
    _write_if_changed(legado, decision)
    _write_if_changed(evidence, decision)
    return (0 if status == "AUTORIZADA" else 2), decision


def run_activity(
    *,
    activity: str,
    folder_id: str,
    repo_root: Path | None = None,
    credential_check: Callable[[], tuple[bool, str]] | None = None,
    validator_gate: Callable[[], tuple[bool, str]] | None = None,
) -> tuple[int, dict[str, Any]]:
    """Reavalia a WO. Não baixa e não atomiza enquanto o status não for AUTORIZADA."""
    code, decision = submit_work_order(
        activity=activity,
        folder_id=folder_id,
        repo_root=repo_root,
        credential_check=credential_check,
        validator_gate=validator_gate,
    )
    if code != 0 or decision.get("status") != "AUTORIZADA":
        decision = dict(decision)
        decision["executed"] = False
        return 2, decision
    decision = dict(decision)
    decision["executed"] = False
    decision["motivo"] = "status AUTORIZADA sem coletor de bytes acoplado; fail-closed, nada foi baixado"
    return 2, decision
