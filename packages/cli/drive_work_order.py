"""Submissão de WO pelo Kernel para obter ou atomizar uma pasta Drive.

O Kernel não concede autorização e não emite PREAUTHORIZED. Ele só
confere a atividade com as políticas já versionadas. Se alguma não
confere, grava a WO com estado BLOQUEADO e devolve exit 2.

Este módulo não acessa a rede, não baixa arquivo e não escreve átomo.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ACTIVITIES = ("obter", "atomizar")
SCHEMA = "CE-WO-AUTHORIZATION-1.0.0"
ROOTS_SCHEMA = "CE-DRIVE-ROOTS-1.0.0"
HUMAN_STATUSES = {"PREAUTHORIZED", "AUTORIZADA", "APROVADA"}


class WorkOrderRejected(RuntimeError):
    """Falha de contrato antes de existir uma WO registrável."""


def load_json_document(path: Path) -> dict:
    """Lê um JSON objeto, ignorando comentários após o primeiro valor."""
    text = path.read_text(encoding="utf-8")
    start = text.find("{")
    if start < 0:
        raise WorkOrderRejected(f"JSON ausente em {path}")
    try:
        obj, _ = json.JSONDecoder().raw_decode(text[start:])
    except json.JSONDecodeError as exc:
        raise WorkOrderRejected(f"JSON inválido em {path}: {exc}") from exc
    if not isinstance(obj, dict):
        raise WorkOrderRejected(f"contrato inválido em {path}")
    return obj


def load_roots(path: Path) -> dict:
    doc = load_json_document(path)
    if doc.get("schema") != ROOTS_SCHEMA:
        raise WorkOrderRejected("contrato de raízes Drive ausente ou divergente")
    roots = doc.get("roots")
    if not isinstance(roots, list) or not roots:
        raise WorkOrderRejected("raízes Drive inválidas")
    ids = []
    for root in roots:
        if not isinstance(root, dict) or not root.get("id") or not root.get("label"):
            raise WorkOrderRejected("raiz Drive incompleta")
        ids.append(root["id"])
    if len(set(ids)) != len(ids):
        raise WorkOrderRejected("raízes Drive duplicadas")
    restrictions = doc.get("restrictions")
    if not isinstance(restrictions, list) or "NO_CANONICAL_PROMOTION" not in restrictions:
        raise WorkOrderRejected("restrição NO_CANONICAL_PROMOTION ausente")
    if "READ_ONLY" not in restrictions or "NO_PUBLICATION" not in restrictions:
        raise WorkOrderRejected("restrições READ_ONLY ou NO_PUBLICATION ausentes")
    return doc


def load_policy(policies_dir: Path, policy_id: str | None) -> dict | None:
    if not policy_id:
        return None
    path = policies_dir / f"{policy_id}.json"
    if not path.is_file():
        raise WorkOrderRejected(f"política não registrada: {policy_id}")
    policy = load_json_document(path)
    if policy.get("id") != policy_id:
        raise WorkOrderRejected(f"id divergente na política {policy_id}")
    if not policy.get("validators"):
        raise WorkOrderRejected(f"política {policy_id} sem validadores")
    return policy


def credentials_present() -> bool:
    return bool(os.environ.get("GDRIVE_SA_KEY") or os.environ.get("DRIVE_ACCESS_TOKEN"))


def human_authorization_exists(folder_id: str, legado_dir: Path) -> bool:
    if not legado_dir.is_dir():
        return False
    for path in sorted(legado_dir.glob("autorizacao_WO-*.json")):
        try:
            doc = load_json_document(path)
        except WorkOrderRejected:
            continue
        author = str(doc.get("authorized_by") or "")
        status = str(doc.get("status") or doc.get("estado") or "")
        if author == "KERNEL" or status not in HUMAN_STATUSES:
            continue
        blob = json.dumps(doc, ensure_ascii=False)
        if folder_id in blob:
            return True
    return False


def decide_work_order(
    *,
    activity: str,
    folder_id: str,
    roots_doc: dict,
    policy: dict | None,
    credentials_ok: bool,
    human_authorization: bool,
) -> dict:
    """Decide a WO. Nunca devolve PREAUTHORIZED."""
    if activity not in ACTIVITIES:
        raise WorkOrderRejected("atividade fora do contrato: obter ou atomizar")
    if not isinstance(folder_id, str) or len(folder_id) < 10 or "/" in folder_id:
        raise WorkOrderRejected("folder_id inválido")

    motivos: list[str] = []
    root_ids = {root["id"] for root in roots_doc.get("roots", [])}
    restrictions = list(roots_doc.get("restrictions") or [])

    if folder_id not in root_ids:
        motivos.append(
            "pasta ausente do registry de raízes Drive "
            "(config/drive_inventory_roots_20261016.json)"
        )
    if activity == "obter" and not credentials_ok:
        motivos.append(
            "credencial ausente: nem GDRIVE_SA_KEY nem DRIVE_ACCESS_TOKEN; fail-closed"
        )
    if activity == "atomizar" and "NO_CANONICAL_PROMOTION" in restrictions:
        motivos.append(
            "NO_CANONICAL_PROMOTION: o Drive registrado não promove átomo canônico"
        )
    if policy is None:
        motivos.append(
            "nenhuma KERNEL-POLICY pôde ser selecionada para os arquivos; fail-closed"
        )
    else:
        policy_id = policy["id"]
        if policy.get("wo_required") and not human_authorization:
            motivos.append(
                f"{policy_id} exige WO humana preexistente; o Kernel não concede autorização"
            )
        if activity == "atomizar" and policy.get("requires_human_review"):
            motivos.append(
                f"{policy_id} exige revisão humana antes de átomo canônico"
            )
        output = str(policy.get("atoms_output") or "")
        if activity == "atomizar" and output.startswith("data/canonical/"):
            motivos.append(
                f"{policy_id} grava em {output}, o que é promoção canônica"
            )

    blocked = bool(motivos)
    status = "BLOQUEADO" if blocked else "REGISTRADA"
    if status == "PREAUTHORIZED":
        raise WorkOrderRejected("o Kernel não emite PREAUTHORIZED")
    return {
        "schema": SCHEMA,
        "wo_id": f"CE-WO-DRIVE-{activity}-{folder_id}",
        "activity": activity,
        "folder_id": folder_id,
        "policy_id": None if policy is None else policy.get("id"),
        "status": status,
        "estado": status,
        "motivo": "; ".join(motivos) if motivos else None,
        "authorized_by": "KERNEL",
        "grants_download": status == "REGISTRADA" and activity == "obter",
        "grants_atomize": status == "REGISTRADA" and activity == "atomizar",
        "conditions": [
            "O Kernel não cria política nova",
            "O Kernel não emite PREAUTHORIZED",
            "Obter exige raiz registrada e credencial já configurada",
            "Atomizar exige política selecionada, sem promoção canônica vedada, e revisão humana quando a política a exige",
        ],
    }


def _semantic(doc: dict) -> dict:
    return {key: value for key, value in doc.items() if key != "timestamp"}


def render_work_order(decision: dict, timestamp: str, evidence: list[str]) -> dict:
    return {
        "schema": decision["schema"],
        "wo_id": decision["wo_id"],
        "slug": f"drive_{decision['activity']}_{decision['folder_id']}",
        "status": decision["status"],
        "estado": decision["estado"],
        "activity": decision["activity"],
        "folder_id": decision["folder_id"],
        "policy_id": decision["policy_id"],
        "rationale": decision["motivo"] or "políticas versionadas conferem com a atividade",
        "motivo": decision["motivo"],
        "authorized_by": "KERNEL",
        "timestamp": timestamp,
        "grants_download": decision["grants_download"],
        "grants_atomize": decision["grants_atomize"],
        "conditions": decision["conditions"],
        "evidence": evidence,
    }


def write_work_order(output_dir: Path, decision: dict, evidence: list[str] | None = None) -> tuple[Path, dict, bool]:
    """Grava a WO. Regrava só quando o conteúdo semântico muda."""
    if decision["status"] not in {"BLOQUEADO", "REGISTRADA"}:
        raise WorkOrderRejected("estado de WO fora do contrato do Kernel")
    if decision["authorized_by"] != "KERNEL":
        raise WorkOrderRejected("WO do Kernel com autor divergente")
    if decision["grants_download"] or decision["grants_atomize"]:
        if decision["status"] != "REGISTRADA":
            raise WorkOrderRejected("concessão sem registro")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"autorizacao_{decision['wo_id']}.json"
    notes = list(evidence or [])
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if path.is_file():
        current = load_json_document(path)
        candidate = render_work_order(decision, str(current.get("timestamp") or now), notes)
        if _semantic(current) == _semantic(candidate):
            return path, current, False
        payload = candidate
    else:
        payload = render_work_order(decision, now, notes)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path, payload, True


def submit(
    *,
    activity: str,
    folder_id: str,
    roots_path: Path,
    output_dir: Path,
    policies_dir: Path,
    policy_id: str | None = None,
    credentials_ok: bool | None = None,
    legado_dir: Path | None = None,
    evidence: list[str] | None = None,
) -> tuple[dict, int]:
    roots = load_roots(roots_path)
    policy = load_policy(policies_dir, policy_id)
    if credentials_ok is None:
        credentials_ok = credentials_present()
    human = human_authorization_exists(folder_id, legado_dir or output_dir)
    decision = decide_work_order(
        activity=activity,
        folder_id=folder_id,
        roots_doc=roots,
        policy=policy,
        credentials_ok=credentials_ok,
        human_authorization=human,
    )
    _path, payload, _changed = write_work_order(output_dir, decision, evidence)
    code = 2 if payload["status"] == "BLOQUEADO" else 0
    return payload, code


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Submete uma WO pelo Kernel, sem baixar e sem atomizar.")
    parser.add_argument("--activity", required=True, choices=ACTIVITIES)
    parser.add_argument("--folder", required=True)
    parser.add_argument("--policy", default=None)
    parser.add_argument("--roots", type=Path, required=True)
    parser.add_argument("--policies-dir", type=Path, default=Path("contracts/policies"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/legado"))
    parser.add_argument("--evidence", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        payload, code = submit(
            activity=args.activity,
            folder_id=args.folder,
            roots_path=args.roots,
            output_dir=args.output_dir,
            policies_dir=args.policies_dir,
            policy_id=args.policy,
            evidence=args.evidence,
        )
    except WorkOrderRejected as exc:
        print(f"WO_REJECTED {exc}", file=sys.stderr)
        return 2
    print(
        f"WO {payload['wo_id']} status={payload['status']} "
        f"download={payload['grants_download']} atomize={payload['grants_atomize']}"
    )
    if payload.get("motivo"):
        print(payload["motivo"])
    return code


if __name__ == "__main__":
    raise SystemExit(main())
