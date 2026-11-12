"""Planejamento de WO do Kernel para uma pasta do Drive.

O Kernel não escolhe pasta, não cria política e não adquire bytes por conta
própria. Uma atividade ``obter`` ou ``atomizar`` só recebe WO de execução
quando uma política já versionada lista a pasta, exige WO, passa no gate e
há credencial. Qualquer outra combinação é REJECTED e não baixa arquivo.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

SCHEMA = "CE-KERNEL-DRIVE-ACTIVITY-1.0.0"
ACTIVITIES = ("atomizar", "obter")
FOLDER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,128}$")
ROOTS_CONFIG = Path("config/drive_inventory_roots_20261016.json")
POLICIES_DIR = Path("contracts/policies")

RESTRICTIONS_WHEN_ROOTS_MISSING = (
    "READ_ONLY",
    "NO_DELETE",
    "NO_PUBLICATION",
    "NO_CANONICAL_PROMOTION",
)


def credential_present() -> bool:
    """Informa só a presença das variáveis. Não lê o segredo para o relatório."""
    return bool(os.environ.get("GDRIVE_SA_KEY") or os.environ.get("DRIVE_ACCESS_TOKEN"))


def _wo_id(policy_id: str, activity: str, folder_id: str, code: str) -> str:
    digest = hashlib.sha256(
        f"{policy_id}|{activity}|{folder_id}|{code}".encode("utf-8")
    ).hexdigest()[:16]
    return f"CE-WO-{digest}"


def _load_json(path: Path) -> dict | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def load_policies(repo_root: Path) -> list[dict]:
    directory = repo_root / POLICIES_DIR
    if not directory.is_dir():
        return []
    policies: list[dict] = []
    for path in sorted(directory.glob("KERNEL-POLICY-*.json")):
        document = _load_json(path)
        if document is None or document.get("id") != path.stem:
            continue
        policies.append(document)
    return policies


def load_roots(repo_root: Path) -> tuple[list[str], list[str]]:
    document = _load_json(repo_root / ROOTS_CONFIG)
    if not document:
        return [], list(RESTRICTIONS_WHEN_ROOTS_MISSING)
    roots = []
    for item in document.get("roots") or []:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            roots.append(item["id"])
    restrictions = document.get("restrictions")
    if not isinstance(restrictions, list) or not all(isinstance(x, str) for x in restrictions):
        restrictions = list(RESTRICTIONS_WHEN_ROOTS_MISSING)
    return roots, list(restrictions)


def _authorized_ids(policy: dict) -> set[str]:
    raw = policy.get("authorized_drive_folder_ids")
    if not isinstance(raw, list):
        return set()
    return {item for item in raw if isinstance(item, str) and item}


def plan_drive_folder(
    *,
    folder_id: str,
    policies: list[dict],
    registered_root_ids: list[str],
    credential_configured: bool,
    gate_exit_by_policy: dict[str, int] | None = None,
    restrictions: list[str] | None = None,
) -> dict:
    """Decide as WOs. Não acessa a rede e não grava átomos."""
    work_orders: list[dict] = []
    folder_ok = bool(FOLDER_ID_RE.fullmatch(folder_id or ""))
    registered = folder_ok and folder_id in set(registered_root_ids)

    if not folder_ok:
        decision = _envelope(
            folder_id=folder_id,
            decision="REJECTED",
            code="MALFORMED_FOLDER_ID",
            motivo="Identificador de pasta rejeitado. Nenhuma atividade foi submetida.",
            work_orders=[],
            credential_configured=credential_configured,
            registered=False,
            registered_root_ids=list(registered_root_ids),
            restrictions=restrictions,
        )
        return decision

    for policy in sorted(policies, key=lambda item: str(item.get("id") or "")):
        policy_id = str(policy.get("id") or "")
        listed = folder_id in _authorized_ids(policy)
        for activity in ACTIVITIES:
            if not listed:
                code = "FOLDER_NOT_IN_POLICY"
            elif policy.get("wo_required") is not True:
                code = "POLICY_WO_NOT_REQUIRED"
            else:
                gate_code = (gate_exit_by_policy or {}).get(policy_id)
                if gate_code is None:
                    code = "GATE_NOT_RUN"
                elif gate_code != 0:
                    code = "POLICY_GATE_FAILED"
                elif not credential_configured:
                    code = "CREDENTIAL_ABSENT"
                else:
                    code = "SUBMITTED"
            work_orders.append(
                {
                    "activity": activity,
                    "code": code,
                    "decision": "SUBMITTED" if code == "SUBMITTED" else "REJECTED",
                    "policy_id": policy_id,
                    "submitted_by": "kernel",
                    "wo_id": _wo_id(policy_id, activity, folder_id, code),
                }
            )

    applicable = [item for item in work_orders if item["code"] != "FOLDER_NOT_IN_POLICY"]
    if not work_orders:
        overall = "REJECTED"
        code = "NO_POLICIES"
        motivo = "Nenhuma política válida no registry. Fail-closed."
    elif not applicable:
        overall = "REJECTED"
        code = "FOLDER_NOT_IN_POLICY"
        motivo = (
            "Nenhuma política lista esta pasta em authorized_drive_folder_ids. "
            "O Kernel não submeteu WO de execução, não baixou bytes e não atomizou. "
            "Estar ausente ou presente nas raízes de inventário não autoriza aquisição."
        )
    elif all(item["decision"] == "SUBMITTED" for item in applicable):
        overall = "APPROVED"
        code = "SUBMITTED"
        motivo = "Políticas que listam a pasta submeteram WO de obter e atomizar."
    else:
        overall = "REJECTED"
        code = "ACTIVITY_REJECTED"
        motivo = "Pelo menos uma atividade da política aplicável foi recusada. Nada foi baixado nem atomizado."
    if overall != "APPROVED" and not credential_configured:
        motivo += " Credencial Drive ausente."

    return _envelope(
        folder_id=folder_id,
        decision=overall,
        code=code,
        motivo=motivo,
        work_orders=work_orders,
        credential_configured=credential_configured,
        registered=registered,
        registered_root_ids=list(registered_root_ids),
        restrictions=restrictions,
    )


def _envelope(
    *,
    folder_id: str,
    decision: str,
    code: str,
    motivo: str,
    work_orders: list[dict],
    credential_configured: bool,
    registered: bool,
    registered_root_ids: list[str],
    restrictions: list[str] | None,
) -> dict:
    approved = decision == "APPROVED"
    return {
        "activities": list(ACTIVITIES),
        "atoms_written": 0,
        "bytes_acquired": False,
        "code": code,
        "credential_present": bool(credential_configured),
        "decision": decision,
        "exit_code": 0 if approved else 2,
        "folder_id": folder_id,
        "folder_is_registered_root": registered,
        "motivo": motivo,
        "registered_root_ids": list(registered_root_ids),
        "restrictions": list(restrictions or RESTRICTIONS_WHEN_ROOTS_MISSING),
        "schema": SCHEMA,
        "submitted_by": "kernel",
        "work_orders": work_orders,
    }


def may_acquire(plan: dict) -> bool:
    """Aquisição só com plano APPROVED e WO SUBMITTED nas políticas que listam a pasta."""
    orders = plan.get("work_orders")
    if plan.get("decision") != "APPROVED" or plan.get("bytes_acquired") is not False:
        return False
    if not isinstance(orders, list) or not orders:
        return False
    submitted = False
    for item in orders:
        if not isinstance(item, dict) or item.get("submitted_by") != "kernel":
            return False
        if item.get("decision") == "SUBMITTED":
            submitted = True
            continue
        if item.get("code") == "FOLDER_NOT_IN_POLICY" and item.get("decision") == "REJECTED":
            continue
        return False
    return submitted


def write_plan(plan: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(output)


def run_drive_folder(
    folder_id: str,
    repo_root: Path,
    output: Path | None = None,
    gate_exit_by_policy: dict[str, int] | None = None,
) -> tuple[dict, int]:
    """Submete a decisão do Kernel e persiste a evidência. Não chama o Drive."""
    policies = load_policies(repo_root)
    roots, restrictions = load_roots(repo_root)
    plan = plan_drive_folder(
        folder_id=folder_id,
        policies=policies,
        registered_root_ids=roots,
        credential_configured=credential_present(),
        gate_exit_by_policy=gate_exit_by_policy,
        restrictions=restrictions,
    )
    if may_acquire(plan):
        for item in plan["work_orders"]:
            if item.get("decision") == "SUBMITTED":
                item["decision"] = "REJECTED"
                item["code"] = "ACQUISITION_NOT_ENABLED"
        plan["decision"] = "REJECTED"
        plan["code"] = "ACQUISITION_NOT_ENABLED"
        plan["exit_code"] = 2
        plan["bytes_acquired"] = False
        plan["atoms_written"] = 0
        plan["motivo"] = (
            "A política autorizaria a pasta, mas a aquisição de bytes não está habilitada. "
            "Nenhum arquivo foi baixado e nenhum átomo foi escrito."
        )
    destination = output or (
        repo_root / "data" / "grc" / "evidencias" / f"kernel_drive_{folder_id}.json"
    )
    resolved_repo = repo_root.resolve()
    resolved_out = destination.resolve()
    if resolved_repo != resolved_out and resolved_repo not in resolved_out.parents:
        raise RuntimeError("evidência fora do repositório; fail-closed")
    write_plan(plan, destination)
    return plan, int(plan["exit_code"])


def main() -> None:
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Kernel: WO de obter/atomizar uma pasta do Drive.")
    parser.add_argument("--folder", required=True)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output")
    args = parser.parse_args()
    plan, code = run_drive_folder(
        args.folder,
        Path(args.repo),
        Path(args.output) if args.output else None,
    )
    print(
        f"KERNEL {plan['decision']} code={plan['code']} "
        f"wos={len(plan['work_orders'])} bytes_acquired={plan['bytes_acquired']}"
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
