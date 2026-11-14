"""Submissão de WO pelo Kernel para atividades de Drive.

O Kernel não escolhe política, não amplia raiz registrada e não baixa bytes
quando o contrato vigente é somente metadado. A saída é a WO submetida e o
exit code 2 quando a atividade não está autorizada.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

SCHEMA = "CE-WO-KERNEL-SUBMISSION-1.0.0"
FOLDER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,80}$")
ACTIVITIES = ("atomizar", "obter")
CREDENTIAL_ENV = ("GDRIVE_SA_KEY", "DRIVE_ACCESS_TOKEN")
ROOTS_REL = Path("config/drive_inventory_roots_20261016.json")
POLICIES_REL = Path("contracts/policies")
AUTHORIZATIONS_REL = Path("data/legado")
VALIDATORS_REL = Path("packages/cli/validators")
NAME_RE = re.compile(r'(?m)^[ \t]+NAME[ \t]*=[ \t]*"([a-z0-9_]+)"')
ATTR_RE = re.compile(r'(?m)^[ \t]+([a-z0-9_]+)[ \t]*=[ \t]*"\1"')


def _utc_now(now: datetime | None) -> str:
    moment = now or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON objeto esperado: {path}")
    return data


def _reason(code: str, detail: str) -> dict[str, str]:
    return {"code": code, "detail": detail}


def _validator_names(validators_dir: Path) -> set[str]:
    names: set[str] = set()
    if not validators_dir.is_dir():
        return names
    for file in sorted(validators_dir.glob("*_validator.py")):
        text = file.read_text(encoding="utf-8")
        names.update(NAME_RE.findall(text))
        names.update(ATTR_RE.findall(text))
    return names


def _authorization_mentions(authorizations_dir: Path, folder_id: str) -> bool:
    if not authorizations_dir.is_dir() or not folder_id:
        return False
    for file in sorted(authorizations_dir.glob("autorizacao_WO-*.json")):
        if folder_id in file.read_text(encoding="utf-8"):
            return True
    return False


def _output_for(repo_root: Path, folder_id: str, output_path: Path | None) -> Path:
    if output_path is None:
        token = folder_id if FOLDER_ID_RE.fullmatch(folder_id) else hashlib.sha256(
            folder_id.encode("utf-8")
        ).hexdigest()[:16]
        output_path = repo_root / "data/legado/kernel_wo" / f"CE-WO-KERNEL-DRIVE-{token}.json"
    elif not output_path.is_absolute():
        output_path = repo_root / output_path
    if not _inside(repo_root, output_path):
        raise ValueError("output fora do repositório")
    return output_path


def _fingerprint(document: dict) -> dict:
    return {key: value for key, value in document.items() if key != "submitted_at"}


def submit_drive_work_order(
    repo_root: Path,
    folder_id: str,
    activities: Sequence[str],
    policy_id: str | None = None,
    *,
    roots_path: Path | None = None,
    policies_dir: Path | None = None,
    authorizations_dir: Path | None = None,
    validators_dir: Path | None = None,
    output_path: Path | None = None,
    env: Mapping[str, str] | None = None,
    now: datetime | None = None,
) -> dict:
    """Registra a WO e recusa obter/atomizar fora do contrato vigente.

    Não acessa a rede e não grava bytes de arquivo do Drive.
    """
    repo_root = Path(repo_root).resolve()
    roots_path = Path(roots_path) if roots_path else repo_root / ROOTS_REL
    policies_dir = Path(policies_dir) if policies_dir else repo_root / POLICIES_REL
    authorizations_dir = (
        Path(authorizations_dir) if authorizations_dir else repo_root / AUTHORIZATIONS_REL
    )
    validators_dir = Path(validators_dir) if validators_dir else repo_root / VALIDATORS_REL
    target = _output_for(repo_root, folder_id, output_path)
    requested = tuple(sorted(dict.fromkeys(activities)))
    reasons: list[dict[str, str]] = []

    if not requested or any(activity not in ACTIVITIES for activity in requested):
        reasons.append(_reason(
            "UNKNOWN_ACTIVITY",
            "atividades aceitas: atomizar, obter",
        ))

    if not FOLDER_ID_RE.fullmatch(folder_id):
        reasons.append(_reason("INVALID_FOLDER_ID", "id de pasta fora do formato Drive"))

    restrictions: list[str] = []
    scope = None
    registered: set[str] = set()
    if not roots_path.is_file():
        reasons.append(_reason("ROOTS_CONTRACT_MISSING", str(roots_path)))
    else:
        try:
            roots_doc = _load_json(roots_path)
        except (OSError, ValueError) as exc:
            reasons.append(_reason("ROOTS_CONTRACT_INVALID", type(exc).__name__))
            roots_doc = {}
        scope = roots_doc.get("scope")
        raw_roots = roots_doc.get("roots")
        raw_restrictions = roots_doc.get("restrictions")
        if not isinstance(raw_roots, list) or not raw_roots:
            reasons.append(_reason("ROOTS_CONTRACT_INVALID", "lista roots ausente"))
        else:
            registered = {
                item.get("id")
                for item in raw_roots
                if isinstance(item, dict) and isinstance(item.get("id"), str)
            }
            if len(registered) != len(raw_roots):
                reasons.append(_reason("ROOTS_CONTRACT_INVALID", "raiz sem id"))
        if isinstance(raw_restrictions, list):
            restrictions = [item for item in raw_restrictions if isinstance(item, str)]
        if scope != "registered_roots_metadata_only":
            reasons.append(_reason(
                "UNKNOWN_ROOTS_SCOPE",
                "escopo de raízes não autoriza leitura de bytes",
            ))
        elif "obter" in requested:
            reasons.append(_reason(
                "METADATA_ONLY",
                "contrato registered_roots_metadata_only não autoriza download",
            ))
        if folder_id not in registered:
            reasons.append(_reason(
                "UNREGISTERED_DRIVE_ROOT",
                "pasta ausente de config/drive_inventory_roots_20261016.json",
            ))
        if "atomizar" in requested and "NO_CANONICAL_PROMOTION" in restrictions:
            reasons.append(_reason(
                "NO_CANONICAL_PROMOTION",
                "atomização para corpus canônico não autorizada pelo contrato de raízes",
            ))

    policy = None
    if not policy_id:
        reasons.append(_reason(
            "POLICY_REQUIRED",
            "Kernel não escolhe política; informe --policy",
        ))
    else:
        policy_path = policies_dir / f"{policy_id}.json"
        if not policy_path.is_file():
            reasons.append(_reason("POLICY_NOT_FOUND", policy_id))
        else:
            try:
                policy = _load_json(policy_path)
            except (OSError, ValueError) as exc:
                reasons.append(_reason("POLICY_INVALID", type(exc).__name__))
            else:
                if policy.get("id") != policy_id:
                    reasons.append(_reason("POLICY_ID_MISMATCH", policy_id))
                validators = policy.get("validators")
                known = _validator_names(validators_dir)
                if not isinstance(validators, list) or not validators:
                    reasons.append(_reason("POLICY_NO_VALIDATORS", policy_id))
                else:
                    missing = sorted(name for name in validators if name not in known)
                    if missing:
                        reasons.append(_reason(
                            "POLICY_VALIDATOR_MISSING",
                            ", ".join(missing),
                        ))
                if policy.get("wo_required") and not _authorization_mentions(
                    authorizations_dir, folder_id
                ):
                    reasons.append(_reason(
                        "WO_AUTHORIZATION_MISSING",
                        "política exige autorização e nenhuma cita esta pasta",
                    ))

    if not _authorization_mentions(authorizations_dir, folder_id):
        reasons.append(_reason(
            "NO_MATCHING_AUTHORIZATION",
            "nenhuma autorizacao_WO cita esta pasta",
        ))

    environment = os.environ if env is None else env
    credentials_present = any(environment.get(name) for name in CREDENTIAL_ENV)
    if "obter" in requested and not credentials_present:
        reasons.append(_reason(
            "CREDENTIALS_MISSING",
            "GDRIVE_SA_KEY e DRIVE_ACCESS_TOKEN ausentes; fail-closed",
        ))

    if not reasons:
        reasons.append(_reason(
            "NO_ALLOW_RULE",
            "nenhuma regra registrada autoriza obter ou atomizar; fail-closed",
        ))

    blocking = [item["code"] for item in reasons if item["code"] != "CREDENTIALS_MISSING"]
    status = "BLOQUEADO" if not blocking else "REJECTED"
    document = {
        "schema": SCHEMA,
        "wo_id": f"CE-WO-KERNEL-DRIVE-{folder_id}" if FOLDER_ID_RE.fullmatch(folder_id)
        else f"CE-WO-KERNEL-DRIVE-{hashlib.sha256(folder_id.encode('utf-8')).hexdigest()[:16]}",
        "submitted_by": "kernel",
        "status": status,
        "exit_code": 2,
        "activities": list(requested),
        "folder_id": folder_id,
        "policy_id": policy_id,
        "roots_scope": scope,
        "folder_registered": folder_id in registered,
        "restrictions_applied": restrictions,
        "credentials_present": credentials_present,
        "bytes_acquired": False,
        "atoms_written": 0,
        "network_access": False,
        "reasons": sorted(reasons, key=lambda item: item["code"]),
        "submitted_at": _utc_now(now),
    }

    if target.is_file():
        try:
            existing = _load_json(target)
        except (OSError, ValueError) as exc:
            raise ValueError(f"WO existente ilegível; não sobrescrever: {exc}") from exc
        if _fingerprint(existing) == _fingerprint(document):
            document["submitted_at"] = existing.get("submitted_at", document["submitted_at"])
            return document

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(target)
    return document


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Submete obter/atomizar de uma pasta Drive ao Kernel."
    )
    parser.add_argument("--folder-id", required=True)
    parser.add_argument("--activity", action="append", required=True, dest="activities")
    parser.add_argument("--policy", default=None)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    try:
        document = submit_drive_work_order(
            args.repo_root,
            args.folder_id,
            args.activities,
            args.policy,
            output_path=args.output,
        )
    except ValueError as exc:
        parser.exit(2, f"{exc}\n")
    print(json.dumps(
        {
            "wo_id": document["wo_id"],
            "status": document["status"],
            "bytes_acquired": document["bytes_acquired"],
            "atoms_written": document["atoms_written"],
            "reasons": [item["code"] for item in document["reasons"]],
        },
        ensure_ascii=False,
    ))
    return int(document["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
