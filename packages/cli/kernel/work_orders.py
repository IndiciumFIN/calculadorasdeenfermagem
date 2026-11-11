"""Submissão de WO pelo Kernel antes de obter ou atomizar uma pasta do Drive.

O Kernel não cria política, não acrescenta raiz e não baixa bytes quando a
pasta está fora do contrato. Credencial ausente, pasta fora do registry ou
política que não declara a pasta → WO BLOQUEADO e exit 2.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import pkgutil
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.request import Request, urlopen

PACKAGE_REPO = Path(__file__).resolve().parents[3]
ROOTS_RELATIVE = Path("config/drive_inventory_roots_20261016.json")
AUTHORITY_RELATIVE = Path("data/legado/drive_raizes.json")
FOLDER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,80}$")
LEGAL_RE = re.compile(r"(art\.|artigo|§|inciso|parágrafo|paragrafo)", re.IGNORECASE)
URL_RE = re.compile(r"https://[^\s<>\"']+")
HTML_PREFIXES = (b"<!doctype", b"<html")
MAX_FILE_BYTES = 50 * 1024 * 1024
TEXT_EXPORTS = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
}
OPINATIVE = (
    "infelizmente",
    "importante destacar",
    "recomenda-se",
    "sugerimos",
    "a nosso ver",
    "consideramos que",
    "acreditamos que",
    "no nosso entendimento",
)


def _now(value: str | None) -> str:
    if value:
        return value
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _root_ids(document: dict[str, Any] | None) -> list[str]:
    if not document:
        return []
    roots = document.get("roots")
    if not isinstance(roots, list):
        return []
    return [item["id"] for item in roots if isinstance(item, dict) and isinstance(item.get("id"), str)]


def credentials_present() -> bool:
    """True só quando o carregador fail-closed devolve um token. O token não sai daqui."""
    import os

    if not os.environ.get("GDRIVE_SA_KEY") and not os.environ.get("DRIVE_ACCESS_TOKEN"):
        return False
    from packages.cli.drive_recursive_inventory import CredentialError, load_token

    try:
        load_token()
    except CredentialError:
        return False
    return True


def _policies(repo: Path) -> list[dict[str, Any]]:
    directory = repo / "contracts" / "policies"
    found: list[dict[str, Any]] = []
    if not directory.is_dir():
        return found
    for path in sorted(directory.glob("KERNEL-POLICY-*.json")):
        data = _read_json(path)
        if data and data.get("id") == path.stem:
            found.append(data)
    return found


def _policy_mentions(policy: dict[str, Any], folder_id: str) -> bool:
    return folder_id in json.dumps(policy, ensure_ascii=False)


def _authorizing_policies(policies: list[dict[str, Any]], folder_id: str) -> list[str]:
    selected: list[str] = []
    for policy in policies:
        declared = policy.get("drive_folder_ids")
        if isinstance(declared, list) and folder_id in declared and all(isinstance(item, str) for item in declared):
            selected.append(policy["id"])
    return selected


def _wo_id(tarefa: str, folder_id: str) -> str:
    return f"CE-WO-{tarefa.upper()}-{folder_id}"


def _wo_path(repo: Path, tarefa: str, folder_id: str) -> Path:
    return repo / "data" / "legado" / f"autorizacao_WO-{tarefa.upper()}-{folder_id}.json"


def _evidence_path(repo: Path, folder_id: str) -> Path:
    return repo / "data" / "grc" / "evidencias" / f"drive_{folder_id}.json"


def assess_drive_folder(
    folder_id: str,
    *,
    repo: Path | None = None,
    policy_id: str | None = None,
    credential_present_flag: bool | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Avalia os gates e monta as WO. Não acessa a rede."""
    repo = repo or PACKAGE_REPO
    now = _now(now)
    present = credentials_present() if credential_present_flag is None else credential_present_flag
    roots = _read_json(repo / ROOTS_RELATIVE)
    authority = _read_json(repo / AUTHORITY_RELATIVE)
    root_ids = _root_ids(roots)
    authority_ids = _root_ids(authority)
    policies = _policies(repo)
    authorizing = _authorizing_policies(policies, folder_id)
    mentions = [policy["id"] for policy in policies if _policy_mentions(policy, folder_id)]
    scope = roots.get("scope") if isinstance(roots, dict) else None
    declared: list[str] = []
    if isinstance(roots, dict) and isinstance(roots.get("restrictions"), list):
        declared = [item for item in roots["restrictions"] if isinstance(item, str)]

    obter_reasons: list[str] = []
    if not FOLDER_ID_RE.fullmatch(folder_id or ""):
        obter_reasons.append("folder_id inválido")
    if folder_id not in root_ids:
        obter_reasons.append(f"pasta ausente nas raízes registradas {ROOTS_RELATIVE.as_posix()}")
    if authority is None:
        obter_reasons.append(f"autoridade {AUTHORITY_RELATIVE.as_posix()} ausente")
    elif folder_id not in authority_ids:
        obter_reasons.append(f"pasta ausente na autoridade {AUTHORITY_RELATIVE.as_posix()}")
    if scope == "registered_roots_metadata_only" or "READ_ONLY" in declared:
        obter_reasons.append("contrato Drive autoriza somente metadados; aquisição de bytes bloqueada")
    if not present:
        obter_reasons.append("nem GDRIVE_SA_KEY nem DRIVE_ACCESS_TOKEN configurado")
    if folder_id not in authorizing and not (policy_id and policy_id in authorizing):
        obter_reasons.append("nenhuma política do Kernel declara drive_folder_ids com esta pasta")
    if policy_id and policy_id not in {policy["id"] for policy in policies}:
        obter_reasons.append(f"política {policy_id} não está registrada")

    atom_reasons = list(obter_reasons)
    if "NO_CANONICAL_PROMOTION" in declared:
        atom_reasons.append("NO_CANONICAL_PROMOTION impede gravar átomos em data/canonical")
    if not policy_id:
        atom_reasons.append("política não informada; o Kernel não infere KERNEL-POLICY")
    elif policy_id not in authorizing:
        atom_reasons.append(f"política {policy_id} não autoriza esta pasta")

    def build(tarefa: str, reasons: list[str]) -> dict[str, Any]:
        blocked = bool(reasons)
        return {
            "atoms_written": 0,
            "autorizado_por": None if blocked else "kernel",
            "bytes_acquired": False,
            "conditions_failed": list(reasons),
            "estado": "BLOQUEADO" if blocked else "SUBMETIDA",
            "folder_id": folder_id,
            "folder_url": f"https://drive.google.com/drive/folders/{folder_id}",
            "kernel_decision": "REJECTED" if blocked else "APPROVED",
            "motivo": " | ".join(reasons),
            "policy_id": policy_id if tarefa == "atomizar" else None,
            "schema": "CE-WO-AUTHORIZATION-1.0.0",
            "sha256_fonte": None,
            "status": "BLOQUEADO" if blocked else "SUBMETIDA",
            "submitted_at": now,
            "submitted_by": "kernel",
            "tarefa": tarefa,
            "wo_id": _wo_id(tarefa, folder_id),
        }

    orders = [build("obter", obter_reasons), build("atomizar", atom_reasons)]
    return {
        "schema": "CE-WO-DRIVE-RUN-1.0.0",
        "atoms_written": 0,
        "authority_present": authority is not None,
        "bytes_acquired": False,
        "credential_present": present,
        "exit_code": 2 if any(order["estado"] != "SUBMETIDA" for order in orders) else 0,
        "folder_id": folder_id,
        "folder_in_registered_roots": folder_id in root_ids,
        "now": now,
        "orders": orders,
        "policies_authorizing_folder": authorizing,
        "policies_consulted": [policy["id"] for policy in policies],
        "policy_mentions_folder": mentions,
        "policy_id": policy_id,
        "registered_root_ids": root_ids,
        "repo": repo,
        "restrictions": declared,
        "scope": scope,
        "submitted_by": "kernel",
    }


def _dump(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _public_order(order: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in order.items() if key != "repo"}


def _persist(assessment: dict[str, Any]) -> dict[str, Any]:
    repo: Path = assessment["repo"]
    folder_id = assessment["folder_id"]
    for order in assessment["orders"]:
        _dump(_wo_path(repo, order["tarefa"], folder_id), _public_order(order))
    evidence = {
        "atoms_written": assessment["atoms_written"],
        "authority_present": assessment["authority_present"],
        "bytes_acquired": assessment["bytes_acquired"],
        "credential_present": assessment["credential_present"],
        "exit_code": assessment["exit_code"],
        "folder_id": folder_id,
        "folder_in_registered_roots": assessment["folder_in_registered_roots"],
        "orders": [
            {
                "estado": order["estado"],
                "tarefa": order["tarefa"],
                "wo_id": order["wo_id"],
            }
            for order in assessment["orders"]
        ],
        "policies_authorizing_folder": assessment["policies_authorizing_folder"],
        "policies_consulted": assessment["policies_consulted"],
        "policy_id": assessment["policy_id"],
        "policy_mentions_folder": assessment["policy_mentions_folder"],
        "registered_root_ids": assessment["registered_root_ids"],
        "restrictions": assessment["restrictions"],
        "schema": assessment["schema"],
        "scope": assessment["scope"],
        "submitted_at": assessment["now"],
        "submitted_by": "kernel",
    }
    _dump(_evidence_path(repo, folder_id), evidence)
    persisted = dict(assessment)
    persisted.pop("repo", None)
    return persisted


def _safe_relative(repo: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative or relative.startswith(("/", "\\")):
        raise ValueError("caminho de saída da política rejeitado")
    parts = Path(relative).parts
    if ".." in parts:
        raise ValueError("caminho de saída da política rejeitado")
    destination = (repo / relative).resolve()
    if not destination.is_relative_to(repo.resolve()):
        raise ValueError("caminho de saída escapa o repositório")
    return destination


def _load_validators() -> dict[str, Any]:
    import validators

    for module in pkgutil.iter_modules(validators.__path__):
        if module.name in {"base", "registry"}:
            continue
        importlib.import_module(f"validators.{module.name}")
    from validators.registry import VALIDATORS

    return VALIDATORS


def _canonical_id(legacy_id: str, year: int) -> str:
    digest = hashlib.sha256(legacy_id.encode("utf-8")).hexdigest()[:12]
    return f"NORM-{year}-{int(digest, 16)}"


def _official_url(text: str) -> str | None:
    from packages.cli.validators.sha256_validator import UrlValidator

    validator = UrlValidator()
    for match in URL_RE.findall(text):
        candidate = match.rstrip(".,;)")
        ok, _error = validator.validate({"link_fonte": candidate})
        if ok and candidate:
            return candidate
    return None


def _quarantine(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _fonte_slug(repo: Path, policy: dict[str, Any]) -> str:
    source = policy.get("source_contract")
    if not isinstance(source, str):
        raise KeyError("source_contract")
    data = _read_json(_safe_relative(repo, source))
    slug = (data or {}).get("fonte_slug")
    if not isinstance(slug, str) or not slug:
        raise KeyError("fonte_slug")
    return slug


def atomize_text(
    *,
    text: str,
    file_id: str,
    policy: dict[str, Any],
    wo_id: str,
    repo: Path,
    now: str,
) -> dict[str, int]:
    """Aplica os validadores registrados na política. Fora do contrato, quarentena integral."""
    from packages.cli.utils import aplicar_mascara
    from packages.schemas.invariantes import AtomoBlindado

    text = aplicar_mascara(text)
    slug = _fonte_slug(repo, policy)
    atoms_dir = _safe_relative(repo, str(policy.get("atoms_output") or ""))
    quarantine_dir = _safe_relative(
        repo, str(policy.get("quarentena_output") or f"data/quarentena/{policy['id']}")
    )
    quarantine_file = quarantine_dir / "validacao_invalida.jsonl"
    registered = _load_validators()
    missing = [name for name in policy.get("validators") or [] if name not in registered]
    if missing:
        raise RuntimeError("validador ausente: " + ", ".join(missing))

    year = int(now[:4])
    counts = {"aprovados": 0, "quarentena": 0}
    for index, raw_line in enumerate(text.splitlines() or [text], start=1):
        line = raw_line.strip()
        if not line:
            continue
        sha = hashlib.sha256(line.encode("utf-8")).hexdigest()
        motivo = None
        if len(line) < 10 or len(line) > 800:
            motivo = "texto_curto" if len(line) < 10 else "acima_contrato"
        elif any(term in line.lower() for term in OPINATIVE):
            motivo = "termo_opinativo"
        elif not LEGAL_RE.search(line):
            motivo = "sem_dispositivo"
        url = _official_url(line) if motivo is None else None
        if motivo is None and not url:
            motivo = "sem_url_oficial"
        if motivo:
            _quarantine(quarantine_file, {
                "arquivo": file_id,
                "motivo": motivo,
                "sha256_original": sha,
                "texto_regra_inteiro": line,
                "wo_id": wo_id,
            })
            counts["quarentena"] += 1
            continue
        legacy_id = f"{file_id}:{index}"
        atom = {
            "dispositivo_legal": line[:100],
            "fonte_slug": slug,
            "hash_status": "CONFERIDO",
            "id_atomo": _canonical_id(legacy_id, year),
            "idioma": "pt-BR",
            "link_fonte": url,
            "sha256_original": sha,
            "sha256_texto": sha,
            "texto_regra": line,
            "versao_contrato": "1.2.0",
            "vigencia": "NAO_VERIFICADO",
            "wo_id": wo_id,
        }
        rejected = None
        for name in policy.get("validators") or []:
            ok, error = registered[name].validate(atom)
            if not ok:
                rejected = error or name
                break
        if rejected:
            _quarantine(quarantine_file, {
                "arquivo": file_id,
                "motivo": "rejeitado_kernel",
                "sha256_original": sha,
                "texto_regra_inteiro": line,
                "wo_id": wo_id,
            })
            counts["quarentena"] += 1
            continue
        try:
            validated = AtomoBlindado.model_validate(atom)
        except Exception:
            _quarantine(quarantine_file, {
                "arquivo": file_id,
                "motivo": "contrato",
                "sha256_original": sha,
                "texto_regra_inteiro": line,
                "wo_id": wo_id,
            })
            counts["quarentena"] += 1
            continue
        atoms_dir.mkdir(parents=True, exist_ok=True)
        target = atoms_dir / f"{validated.id_atomo}.json"
        if target.exists():
            current = _read_json(target) or {}
            if current.get("sha256_texto") != sha:
                _quarantine(quarantine_file, {
                    "arquivo": file_id,
                    "motivo": "conflito_duplicata",
                    "sha256_original": sha,
                    "texto_regra_inteiro": line,
                    "wo_id": wo_id,
                })
                counts["quarentena"] += 1
            continue
        _dump(target, validated.model_dump(mode="json"))
        counts["aprovados"] += 1
    return counts


def _download_bytes(file_id: str, mime: str, token: Callable[[], str], size: int | None) -> bytes | None:
    if size is not None and size > MAX_FILE_BYTES:
        raise ValueError("arquivo acima de 50MB")
    export = TEXT_EXPORTS.get(mime)
    if export:
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}/export?mimeType={export}"
    elif mime.startswith("text/") or mime in {"application/json", "text/csv"}:
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"
    else:
        return None
    request = Request(url, headers={"Authorization": "Bearer " + token(), "Accept": "application/octet-stream"})
    with urlopen(request, timeout=45) as response:
        payload = response.read(MAX_FILE_BYTES + 1)
    if len(payload) > MAX_FILE_BYTES:
        raise ValueError("arquivo acima de 50MB")
    if payload.lstrip().lower().startswith(HTML_PREFIXES):
        raise ValueError("resposta HTML em vez de arquivo")
    return payload


def _default_acquire(folder_id: str) -> list[dict[str, Any]]:
    from packages.cli.drive_recursive_inventory import crawl, load_token

    token = load_token()
    crawled = crawl([{"id": folder_id, "name": folder_id}], token)
    files: list[dict[str, Any]] = []
    for item in crawled["items"]:
        if item["kind"] != "file":
            continue
        try:
            payload = _download_bytes(item["id"], item["mime_type"], token, item.get("size_bytes"))
        except Exception as exc:
            files.append({
                "id": item["id"],
                "name": item["path"],
                "mime_type": item["mime_type"],
                "error": type(exc).__name__,
                "data": None,
            })
            continue
        files.append({
            "id": item["id"],
            "name": item["path"],
            "mime_type": item["mime_type"],
            "error": None if payload is not None else "mime_nao_textual",
            "data": payload,
        })
    return files


def execute_authorized(
    assessment: dict[str, Any],
    *,
    acquire: Callable[[str], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Executa somente a WO que ficou SUBMETIDA. BLOQUEADO não chama o Drive."""
    obter = next(order for order in assessment["orders"] if order["tarefa"] == "obter")
    atomizar = next(order for order in assessment["orders"] if order["tarefa"] == "atomizar")
    if obter["estado"] != "SUBMETIDA":
        return assessment

    repo: Path = assessment["repo"]
    folder_id = assessment["folder_id"]
    files = (acquire or _default_acquire)(folder_id)
    usable = [item for item in files if item.get("data")]
    manifest = [
        {"id": item["id"], "name": item["name"], "sha256": hashlib.sha256(item["data"]).hexdigest()}
        for item in usable
    ]
    manifest_sha = hashlib.sha256(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest() if manifest else None
    obter["bytes_acquired"] = bool(usable)
    obter["sha256_fonte"] = manifest_sha
    if usable and manifest_sha:
        obter["estado"] = "PASS"
        obter["status"] = "PASS"
        obter["motivo"] = ""
        obter["conditions_failed"] = []
        obter["kernel_decision"] = "APPROVED"
    else:
        obter["estado"] = "BLOQUEADO"
        obter["status"] = "BLOQUEADO"
        obter["motivo"] = "nenhum arquivo textual adquirido"
        obter["kernel_decision"] = "REJECTED"

    counts = {"aprovados": 0, "quarentena": 0}
    if atomizar["estado"] == "SUBMETIDA" and usable and assessment.get("policy_id") and manifest_sha:
        policy = next(item for item in _policies(repo) if item["id"] == assessment["policy_id"])
        try:
            for item in usable:
                text = item["data"].decode("utf-8")
                part = atomize_text(
                    text=text,
                    file_id=item["id"],
                    policy=policy,
                    wo_id=atomizar["wo_id"],
                    repo=repo,
                    now=assessment["now"],
                )
                counts["aprovados"] += part["aprovados"]
                counts["quarentena"] += part["quarentena"]
        except (RuntimeError, KeyError, UnicodeDecodeError, ValueError) as exc:
            atomizar["estado"] = "BLOQUEADO"
            atomizar["status"] = "BLOQUEADO"
            atomizar["motivo"] = f"atomização interrompida: {type(exc).__name__}"
            atomizar["kernel_decision"] = "REJECTED"
        else:
            atomizar["atoms_written"] = counts["aprovados"]
            atomizar["sha256_fonte"] = manifest_sha
            atomizar["bytes_acquired"] = True
            if counts["aprovados"] or counts["quarentena"]:
                atomizar["estado"] = "PASS"
                atomizar["status"] = "PASS"
                atomizar["motivo"] = ""
                atomizar["conditions_failed"] = []
                atomizar["kernel_decision"] = "APPROVED"
            else:
                atomizar["estado"] = "BLOQUEADO"
                atomizar["status"] = "BLOQUEADO"
                atomizar["motivo"] = "nenhum texto normativo para atomizar"
                atomizar["kernel_decision"] = "REJECTED"
    elif atomizar["estado"] == "SUBMETIDA":
        atomizar["estado"] = "BLOQUEADO"
        atomizar["status"] = "BLOQUEADO"
        atomizar["motivo"] = "obter não produziu sha256_fonte"
        atomizar["kernel_decision"] = "REJECTED"

    assessment["bytes_acquired"] = bool(usable)
    assessment["atoms_written"] = counts["aprovados"]
    assessment["exit_code"] = 0 if all(order["estado"] == "PASS" for order in assessment["orders"]) else 2
    return assessment


def run_drive_folder(
    folder_id: str,
    *,
    repo: Path | None = None,
    policy_id: str | None = None,
    credential_present_flag: bool | None = None,
    now: str | None = None,
    acquire: Callable[[str], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Submete as WO pelo Kernel e só então obtém ou atomiza."""
    assessment = assess_drive_folder(
        folder_id,
        repo=repo,
        policy_id=policy_id,
        credential_present_flag=credential_present_flag,
        now=now,
    )
    if any(order["estado"] == "SUBMETIDA" and order["tarefa"] == "obter" for order in assessment["orders"]):
        assessment = execute_authorized(assessment, acquire=acquire)
    return _persist(assessment)
