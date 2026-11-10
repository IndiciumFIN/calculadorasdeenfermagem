"""Submissão de WO pelo Kernel antes de obter ou atomizar uma pasta Drive.

O Kernel grava a WO e só libera a atividade quando uma política que passou
no gate declara a pasta, a pasta está nas raízes registradas e a credencial
existe. Promoção canônica continua fechada enquanto o contrato das raízes
impuser NO_CANONICAL_PROMOTION.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

FOLDER_ID = re.compile(r"^[A-Za-z0-9_-]{10,80}$")
ACTIVITIES = ("obter", "atomizar")
ROOTS_REL = "config/drive_inventory_roots_20261016.json"
AUTHORITY_REL = "data/legado/drive_raizes.json"

CredentialCheck = Callable[[], tuple[bool, str]]
ValidatorGate = Callable[[str], tuple[bool, str]]
Downloader = Callable[[str, Path], list[dict[str, Any]]]


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


def load_roots(root: Path) -> tuple[set[str], list[str]]:
    path = root / ROOTS_REL
    if not path.is_file():
        raise FileNotFoundError(f"raízes Drive ausentes: {ROOTS_REL}")
    data = _read_json(path)
    roots = data.get("roots")
    if not isinstance(roots, list) or not roots:
        raise ValueError("roots vazio no registro de pastas Drive")
    ids: list[str] = []
    for item in roots:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("raiz Drive sem id")
        ids.append(item["id"])
    if len(ids) != len(set(ids)):
        raise ValueError("raízes Drive duplicadas")
    restrictions = data.get("restrictions") or []
    if not isinstance(restrictions, list):
        raise ValueError("restrictions inválidas no registro de pastas Drive")
    return set(ids), [str(item) for item in restrictions]


def default_credentials() -> tuple[bool, str]:
    try:
        from drive_recursive_inventory import CredentialError, load_token
    except ImportError:
        from packages.cli.drive_recursive_inventory import CredentialError, load_token
    try:
        load_token()
    except CredentialError as exc:
        return False, str(exc)
    return True, "credencial Drive presente; valor omitido"


def default_validator_gate(policy_id: str) -> tuple[bool, str]:
    from kernel.core import Kernel

    return Kernel().policy_is_valid(policy_id)


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


def _canonical_id(legacy_id: str, year: int) -> str:
    digest = hashlib.sha256(legacy_id.encode("utf-8")).hexdigest()
    return f"NORM-{year}-{int(digest[:12], 16)}"


def submit_work_order(
    *,
    activity: str,
    folder_id: str,
    repo_root: Path | None = None,
    now: datetime | None = None,
    credential_check: CredentialCheck | None = None,
    validator_gate: ValidatorGate | None = None,
) -> tuple[int, dict[str, Any]]:
    """Grava a WO. Exit 0 somente com status AUTORIZADA."""
    root = (repo_root or repo_root_from_here()).resolve()
    motivos: list[str] = []
    if activity not in ACTIVITIES:
        motivos.append("atividade desconhecida; aceitas: obter, atomizar")
    if not FOLDER_ID.fullmatch(folder_id or ""):
        motivos.append("folder_id inválido")

    policies: list[dict[str, Any]] = []
    roots: set[str] = set()
    restrictions: list[str] = []
    try:
        policies = load_policies(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        motivos.append(f"políticas do Kernel ilegíveis: {exc}")
    try:
        roots, restrictions = load_roots(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        motivos.append(f"raízes Drive ilegíveis: {exc}")

    authority = root / AUTHORITY_REL
    if not authority.is_file():
        motivos.append(f"autoridade declarada ausente: {AUTHORITY_REL}")

    if folder_id and roots and folder_id not in roots:
        motivos.append(f"pasta ausente das raízes registradas ({ROOTS_REL})")

    gate = validator_gate or default_validator_gate
    valid_ids: list[str] = []
    invalid: list[str] = []
    for policy in policies:
        policy_id = str(policy.get("id"))
        try:
            ok, detail = gate(policy_id)
        except Exception as exc:
            ok, detail = False, f"gate indisponível: {exc}"
        if ok and policy.get("fail_closed") is True:
            valid_ids.append(policy_id)
        else:
            invalid.append(f"{policy_id}: {detail}")

    authorizing: list[str] = []
    for policy in policies:
        policy_id = str(policy.get("id"))
        folders = policy.get("drive_folder_ids")
        if policy_id in valid_ids and isinstance(folders, list) and folder_id in folders and folder_id in roots:
            authorizing.append(policy_id)
    if policies and folder_id and "folder_id inválido" not in " ".join(motivos):
        declared = [
            str(policy.get("id"))
            for policy in policies
            if isinstance(policy.get("drive_folder_ids"), list) and folder_id in policy["drive_folder_ids"]
        ]
        if not declared:
            motivos.append("nenhuma política registrada declara esta pasta em drive_folder_ids")
        elif not authorizing:
            motivos.append("a pasta está declarada, mas a política não passou no gate do Kernel")

    creds_ok, creds_detail = (credential_check or default_credentials)()
    if activity == "obter" and not creds_ok:
        motivos.append(creds_detail)

    if activity == "atomizar" and "NO_CANONICAL_PROMOTION" in restrictions:
        motivos.append(
            "contrato das raízes Drive impõe NO_CANONICAL_PROMOTION; "
            "atomização não grava data/canonical"
        )
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

    status = "AUTORIZADA" if not motivos else "BLOQUEADO"
    safe_activity = activity if activity in ACTIVITIES else "rejeitada"
    wo_id, legado, evidence = _wo_paths(root, safe_activity, folder_id or "invalido")
    timestamp = _now(now)
    decision: dict[str, Any] = {
        "schema": "CE-WO-AUTHORIZATION-1.0.0",
        "wo_id": wo_id,
        "slug": f"drive_{safe_activity}_{folder_id or 'invalido'}",
        "submitted_by": "kernel",
        "authorized_by": "kernel" if status == "AUTORIZADA" else None,
        "status": status,
        "estado": status,
        "tarefa": activity,
        "lote": f"drive:{folder_id}",
        "folder_id": folder_id,
        "policy_ids_evaluated": [str(policy.get("id")) for policy in policies],
        "valid_policy_ids": valid_ids,
        "invalid_policies": invalid,
        "authorizing_policy_ids": authorizing,
        "motivo": "; ".join(motivos) if motivos else "política válida, raiz e credencial conferidas",
        "motivos": motivos,
        "rationale": "WO submetida pelo Kernel antes de baixar ou atomizar.",
        "timestamp": timestamp,
        "bytes_acquired": False,
        "atoms_written": 0,
        "canonical_promoted": False,
        "root_restrictions": restrictions,
        "conditions": [
            "Somente status AUTORIZADA libera a atividade",
            "A política precisa passar no gate de validadores do Kernel",
            "A política precisa declarar drive_folder_ids com esta pasta",
            "A pasta precisa estar nas raízes registradas",
            "Obter exige credencial Drive sem gravar o segredo",
            "Atomizar exige WO de obter AUTORIZADA e ausência de NO_CANONICAL_PROMOTION",
            "Vigência de átomo nasce NAO_VERIFICADO",
        ],
        "restrictions": restrictions,
        "evidence_reference": evidence.relative_to(root).as_posix(),
    }
    if legado.is_file():
        try:
            previous = _read_json(legado)
        except (OSError, ValueError, json.JSONDecodeError):
            previous = {}
        previous_body = {k: v for k, v in previous.items() if k != "timestamp"}
        current_body = {k: v for k, v in decision.items() if k != "timestamp"}
        if previous_body == current_body:
            decision["timestamp"] = previous.get("timestamp", timestamp)
    _write_if_changed(legado, decision)
    _write_if_changed(evidence, decision)
    return (0 if status == "AUTORIZADA" else 2), decision


def _quarantine(root: Path, policy: dict[str, Any], record: dict[str, Any]) -> None:
    output = policy.get("quarentena_output") or "data/quarentena/drive/"
    path = root / str(output).rstrip("/") / "drive.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def atomize_texts(
    *,
    root: Path,
    policy: dict[str, Any],
    wo_id: str,
    texts: list[dict[str, str]],
    year: int,
) -> tuple[int, int]:
    """Transforma texto já obtido em átomos NAO_VERIFICADO ou quarentena."""
    written = 0
    quarantined = 0
    output = root / str(policy.get("atoms_output") or "data/canonical/atoms/drive")
    for item in texts:
        body = item.get("text") or ""
        origin = item.get("origin") or ""
        paragraphs = [line.strip() for line in body.splitlines() if len(line.strip()) >= 10]
        if not paragraphs:
            _quarantine(root, policy, {
                "motivo": "texto_curto",
                "arquivo": origin,
                "sha256_original": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "wo_id": wo_id,
            })
            quarantined += 1
            continue
        for index, line in enumerate(paragraphs):
            if len(line) > 800:
                _quarantine(root, policy, {
                    "motivo": "acima_contrato",
                    "arquivo": origin,
                    "sha256_original": hashlib.sha256(line.encode("utf-8")).hexdigest(),
                    "texto_regra_inteiro": line,
                    "wo_id": wo_id,
                })
                quarantined += 1
                continue
            legacy = f"{origin}:{index}"
            atom = {
                "id_atomo": _canonical_id(legacy, year),
                "versao_contrato": "1.2.0",
                "texto_regra": line,
                "idioma": "pt-BR",
                "vigencia": "NAO_VERIFICADO",
                "sha256_texto": hashlib.sha256(line.encode("utf-8")).hexdigest(),
                "hash_status": "CONFERIDO",
                "wo_id": wo_id,
                "fonte_slug": Path(str(policy.get("source_contract", "fonte"))).stem,
                "norma_origem": legacy[:120],
                "link_fonte": origin if origin.startswith("https://") else None,
            }
            atom = {k: v for k, v in atom.items() if v is not None}
            dest = output / f"{atom['id_atomo']}.json"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(atom, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            written += 1
    return written, quarantined


def run_activity(
    *,
    activity: str,
    folder_id: str,
    repo_root: Path | None = None,
    credential_check: CredentialCheck | None = None,
    validator_gate: ValidatorGate | None = None,
    downloader: Downloader | None = None,
    texts: list[dict[str, str]] | None = None,
) -> tuple[int, dict[str, Any]]:
    """Reavalia a WO. Sem AUTORIZADA, não baixa e não escreve átomo."""
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

    root = (repo_root or repo_root_from_here()).resolve()
    if activity == "obter":
        if downloader is None:
            decision = dict(decision)
            decision["executed"] = False
            decision["status"] = "BLOQUEADO"
            decision["motivo"] = "status AUTORIZADA sem coletor homologado; fail-closed, nada foi baixado"
            return 2, decision
        raw_dir = root / "data" / "raw" / "drive" / folder_id
        raw_dir.mkdir(parents=True, exist_ok=True)
        acquired = downloader(folder_id, raw_dir)
        decision = dict(decision)
        decision["executed"] = True
        decision["bytes_acquired"] = bool(acquired)
        decision["acquired_files"] = [
            {key: value for key, value in item.items() if key != "content"}
            for item in acquired
        ]
        _persist(root, decision)
        return 0, decision

    policies = load_policies(root)
    policy = next(item for item in policies if item.get("id") in decision.get("authorizing_policy_ids", []))
    if "NO_CANONICAL_PROMOTION" in decision.get("restrictions", []):
        decision = dict(decision)
        decision["executed"] = False
        decision["status"] = "BLOQUEADO"
        decision["motivo"] = "NO_CANONICAL_PROMOTION impede gravar átomos"
        return 2, decision
    written, quarantined = atomize_texts(
        root=root,
        policy=policy,
        wo_id=str(decision["wo_id"]),
        texts=texts or [],
        year=datetime.now(timezone.utc).year,
    )
    decision = dict(decision)
    decision["executed"] = True
    decision["atoms_written"] = written
    decision["quarantined"] = quarantined
    decision["canonical_promoted"] = written > 0 and "canonical" in str(policy.get("atoms_output", ""))
    _persist(root, decision)
    return 0, decision


def _persist(root: Path, decision: dict[str, Any]) -> None:
    activity = str(decision.get("tarefa") or "")
    folder_id = str(decision.get("folder_id") or "")
    if activity not in ACTIVITIES or not folder_id:
        return
    _wo_id, legado, evidence = _wo_paths(root, activity, folder_id)
    _write_if_changed(legado, decision)
    _write_if_changed(evidence, decision)
