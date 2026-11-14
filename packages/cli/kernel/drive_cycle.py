"""Obter e atomizar uma pasta do Drive só depois da WO do Kernel.

O Kernel não escolhe a política e não cria autorização. Cada atividade
grava a WO antes de qualquer rede. Sem política com gate aprovado, sem
raiz autorizada e sem credencial, o estado fica BLOQUEADO e nenhum
byte entra no corpus.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from packages.cli.utils import aplicar_mascara
from packages.schemas.invariantes import AtomoBlindado

from .core import VALIDATORS, assess_validators

FOLDER_RE = re.compile(r"^[A-Za-z0-9_-]{10,128}$")
FOLDER_IN_URL = re.compile(r"/folders/([A-Za-z0-9_-]{10,128})")
AUTH_KEYS = ("drive_folder_ids", "authorized_drive_folder_ids", "folder_ids")
TEXT_MIMES = {
    "text/plain",
    "text/csv",
    "application/json",
    "text/markdown",
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.spreadsheet",
}
MAX_BYTES = 50 * 1024 * 1024
REPO_ROOT = Path(__file__).resolve().parents[3]


def normalize_folder_id(value: str) -> str:
    found = FOLDER_IN_URL.search(value or "")
    if found:
        return found.group(1)
    return (value or "").strip()


def policy_lists_folder(raw: dict, folder_id: str) -> bool:
    """Aceita só campos explícitos de autorização, não o texto livre da política."""
    if raw.get("drive_folder_id") == folder_id or raw.get("folder_id") == folder_id:
        return True
    for key in AUTH_KEYS:
        value = raw.get(key)
        if value == folder_id:
            return True
        if isinstance(value, list) and folder_id in value:
            return True
    return False


def load_policies(directory: Path) -> list[dict]:
    policies = []
    for path in sorted(directory.glob("KERNEL-POLICY-*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            policies.append({"id": path.stem, "_erro": type(exc).__name__})
            continue
        if isinstance(data, dict):
            policies.append(data)
    return policies


def classify_policies(policies: list[dict]) -> tuple[list[dict], list[dict]]:
    passed: list[dict] = []
    failed: list[dict] = []
    for raw in policies:
        identifier = str(raw.get("id") or "")
        if raw.get("_erro"):
            failed.append({"id": identifier, "motivo": f"json inválido: {raw['_erro']}"})
            continue
        names = raw.get("validators")
        if not isinstance(names, list):
            failed.append({"id": identifier, "motivo": "sem validadores"})
            continue
        ok, reason = assess_validators([name for name in names if isinstance(name, str)])
        if ok:
            passed.append(raw)
        else:
            failed.append({"id": identifier, "motivo": reason})
    return passed, failed


def roots_document(path: Path) -> dict:
    if not path.is_file():
        return {"missing": True, "roots": [], "restrictions": [], "scope": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"missing": True, "roots": [], "restrictions": [], "scope": None}
    if not isinstance(data, dict):
        return {"missing": True, "roots": [], "restrictions": [], "scope": None}
    return data


def obter_blocks(folder_id: str, doc: dict, passed: list[dict], env: dict) -> list[str]:
    reasons: list[str] = []
    if doc.get("missing"):
        reasons.append("Arquivo de raízes Drive ausente.")
    ids = {item.get("id") for item in doc.get("roots") or [] if isinstance(item, dict)}
    if folder_id not in ids:
        reasons.append(
            "Pasta ausente das raízes registradas em config/drive_inventory_roots_20261016.json."
        )
    if doc.get("scope") == "registered_roots_metadata_only":
        reasons.append(
            "Escopo das raízes é registered_roots_metadata_only (bytes não autorizados)."
        )
    authorized = [policy for policy in passed if policy_lists_folder(policy, folder_id)]
    if len(authorized) == 0:
        reasons.append("Nenhuma política com gate aprovado declara esta pasta.")
    elif len(authorized) > 1:
        ids = ", ".join(str(policy.get("id")) for policy in authorized)
        reasons.append(f"Mais de uma política autoriza a pasta: {ids}.")
    if not (env.get("GDRIVE_SA_KEY") or env.get("DRIVE_ACCESS_TOKEN")):
        reasons.append("Credencial ausente: nem GDRIVE_SA_KEY nem DRIVE_ACCESS_TOKEN.")
    return reasons


def atomizar_blocks(
    folder_id: str,
    doc: dict,
    passed: list[dict],
    obter_estado: str,
) -> list[str]:
    reasons: list[str] = []
    if obter_estado != "EXECUTADA":
        reasons.append("WO de obter não está EXECUTADA; não há sha256_fonte.")
    if "NO_CANONICAL_PROMOTION" in (doc.get("restrictions") or []):
        reasons.append("Restrição NO_CANONICAL_PROMOTION no contrato das raízes Drive.")
    authorized = [policy for policy in passed if policy_lists_folder(policy, folder_id)]
    if len(authorized) == 0:
        reasons.append("Nenhuma política com gate aprovado autoriza a pasta.")
    elif len(authorized) > 1:
        ids = ", ".join(str(policy.get("id")) for policy in authorized)
        reasons.append(f"Mais de uma política autoriza a pasta: {ids}.")
    return reasons


def probe_drive_anonymous(folder_id: str) -> dict:
    """Registra só o status HTTP. Não grava corpo nem baixa arquivo."""
    result: dict[str, Any] = {"list_http": None, "page_http": None, "page_host": None}
    list_url = (
        "https://www.googleapis.com/drive/v3/files"
        f"?q=%27{folder_id}%27+in+parents+and+trashed=false"
        "&fields=files(id)&pageSize=1&supportsAllDrives=true"
    )
    try:
        with urllib.request.urlopen(list_url, timeout=20) as response:
            result["list_http"] = response.status
    except urllib.error.HTTPError as exc:
        result["list_http"] = exc.code
    except Exception as exc:
        result["list_erro"] = type(exc).__name__
    page = f"https://drive.google.com/drive/folders/{folder_id}"
    request = urllib.request.Request(page, headers={"User-Agent": "CE-Kernel/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            result["page_http"] = response.status
            result["page_host"] = urlparse(response.geturl()).netloc
    except urllib.error.HTTPError as exc:
        result["page_http"] = exc.code
    except Exception as exc:
        result["page_erro"] = type(exc).__name__
    return result


def media_url(file_id: str, mime: str) -> str:
    if mime == "application/vnd.google-apps.document":
        return (
            "https://www.googleapis.com/drive/v3/files/"
            f"{file_id}/export?mimeType=text/plain&supportsAllDrives=true"
        )
    if mime == "application/vnd.google-apps.spreadsheet":
        return (
            "https://www.googleapis.com/drive/v3/files/"
            f"{file_id}/export?mimeType=text/csv&supportsAllDrives=true"
        )
    return (
        "https://www.googleapis.com/drive/v3/files/"
        f"{file_id}?alt=media&supportsAllDrives=true"
    )


def _mime(item: dict) -> str:
    return str(item.get("mimeType") or item.get("mime_type") or "")


def _size(item: dict) -> Any:
    if item.get("size") is not None:
        return item.get("size")
    return item.get("size_bytes")


def _token(env: dict) -> str:
    bearer = env.get("DRIVE_ACCESS_TOKEN")
    if isinstance(bearer, str) and bearer:
        return bearer
    from packages.cli.drive_recursive_inventory import load_token

    return load_token()()


def default_list_children(folder_id: str, env: dict) -> list[dict]:
    from packages.cli.drive_recursive_inventory import crawl

    result = crawl([{"id": folder_id, "name": "WO"}], _token(env))
    listed = []
    for item in result["items"]:
        if item.get("kind") == "folder":
            continue
        listed.append(
            {
                "id": item["id"],
                "name": item["path"],
                "mimeType": item["mime_type"],
                "size": item["size_bytes"],
            }
        )
    return listed


def default_download(item: dict, env: dict) -> bytes:
    url = media_url(str(item["id"]), _mime(item))
    request = urllib.request.Request(
        url,
        headers={"Authorization": "Bearer " + _token(env), "Accept": "*/*"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"download HTTP {exc.code}") from None


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _wo_base(wo_id: str, activity: str, folder_id: str, when: str) -> dict:
    return {
        "schema": "CE-WO-AUTHORIZATION-1.0.0",
        "wo_id": wo_id,
        "activity": activity,
        "folder_id": folder_id,
        "estado": "EM_AVALIACAO",
        "submitted_by": "kernel",
        "timestamp": when,
        "bytes_baixados": 0,
        "atomos_escritos": 0,
        "motivos": [],
    }


def _secret_values(env: dict) -> list[str]:
    found = []
    for key in ("GDRIVE_SA_KEY", "DRIVE_ACCESS_TOKEN"):
        value = env.get(key)
        if isinstance(value, str) and len(value) >= 8:
            found.append(value)
    return found


def _refuse_secrets(paths: list[Path], env: dict) -> None:
    secrets = _secret_values(env)
    if not secrets:
        return
    for path in paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for secret in secrets:
            if secret in text:
                raise RuntimeError(f"credencial gravada em {path.name}")


def _fonte_slug(policy: dict) -> str | None:
    link = policy.get("source_contract")
    if isinstance(link, str) and link.endswith(".json"):
        return Path(link).stem
    return None


def atomize_text(
    text: str,
    *,
    file_id: str,
    wo_id: str,
    policy: dict,
    year: int,
) -> tuple[list[dict], list[dict]]:
    masked = aplicar_mascara(text)
    atoms: list[dict] = []
    quarantine: list[dict] = []
    names = [name for name in policy.get("validators") or [] if isinstance(name, str)]
    fonte = _fonte_slug(policy)
    for index, raw_line in enumerate(masked.splitlines()):
        line = raw_line.strip()
        if not line:
            continue
        legacy = f"{file_id}:{index}"
        number = int(hashlib.sha256(legacy.encode("utf-8")).hexdigest()[:12], 16)
        item: dict[str, Any] = {
            "id_atomo": f"NORM-{year}-{number}",
            "versao_contrato": "1.2.0",
            "texto_regra": line,
            "vigencia": "NAO_VERIFICADO",
            "sha256_texto": hashlib.sha256(line.encode("utf-8")).hexdigest(),
            "wo_id": wo_id,
        }
        if fonte:
            item["fonte_slug"] = fonte
        try:
            model = AtomoBlindado(**item)
        except Exception as exc:
            quarantine.append(
                {"file_id": file_id, "motivo": str(exc), "texto": line, "wo_id": wo_id}
            )
            continue
        payload = model.model_dump(mode="json")
        errors = []
        for name in names:
            validator = VALIDATORS.get(name)
            if validator is None:
                errors.append(f"{name} ausente")
                continue
            valid, error = validator.validate(payload)
            if not valid:
                errors.append(error or name)
        if errors:
            quarantine.append(
                {
                    "file_id": file_id,
                    "motivo": "; ".join(errors),
                    "texto": line,
                    "wo_id": wo_id,
                }
            )
            continue
        atoms.append(payload)
    return atoms, quarantine


def _eligible(item: dict) -> str | None:
    mime = _mime(item)
    if mime not in TEXT_MIMES:
        return f"mime sem parser de atomização: {mime or 'ausente'}"
    size = _size(item)
    if size is None:
        return "tamanho ausente"
    try:
        nbytes = int(size)
    except (TypeError, ValueError):
        return "tamanho inválido"
    if nbytes < 0 or nbytes > MAX_BYTES:
        return f"tamanho fora do limite operacional: {nbytes}"
    return None


def _append_quarantine(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _write_evidence(
    path: Path,
    folder_id: str,
    passed: list[dict],
    failed: list[dict],
    obter: dict,
    atom: dict,
    probe_result: dict | None,
) -> None:
    _write_json(
        path,
        {
            "schema": "CE-DRIVE-WO-EVIDENCE-1.0.0",
            "folder_id": folder_id,
            "bytes_baixados": obter.get("bytes_baixados", 0),
            "atomos_escritos": atom.get("atomos_escritos", 0),
            "politicas_gate_aprovado": [policy.get("id") for policy in passed],
            "politicas_gate_reprovado": failed,
            "probe": probe_result,
            "work_orders": [
                {"wo_id": obter.get("wo_id"), "estado": obter.get("estado")},
                {"wo_id": atom.get("wo_id"), "estado": atom.get("estado")},
            ],
        },
    )


def _close_blocked(
    *,
    folder_id: str,
    when: str,
    passed: list[dict],
    failed: list[dict],
    doc: dict,
    obter: dict,
    obter_path: Path,
    atom_id: str,
    atom_path: Path,
    evidence_path: Path,
    env: dict,
    blocks: list[str],
    probe_result: dict | None,
) -> int:
    obter["estado"] = "BLOQUEADO"
    obter["motivos"] = blocks
    obter["politicas_gate_aprovado"] = [policy.get("id") for policy in passed]
    obter["politicas_gate_reprovado"] = failed
    _write_json(obter_path, obter)
    atom = _wo_base(atom_id, "atomizar", folder_id, when)
    atom["depends_on"] = obter["wo_id"]
    atom["estado"] = "BLOQUEADO"
    atom["motivos"] = atomizar_blocks(folder_id, doc, passed, "BLOQUEADO")
    atom["politicas_gate_aprovado"] = obter["politicas_gate_aprovado"]
    _write_json(atom_path, atom)
    _write_evidence(evidence_path, folder_id, passed, failed, obter, atom, probe_result)
    _refuse_secrets([obter_path, atom_path, evidence_path], env)
    return 2


def run_drive_folder(
    folder: str,
    *,
    root: Path | None = None,
    policies_dir: Path | None = None,
    roots_path: Path | None = None,
    wo_dir: Path | None = None,
    evidence_path: Path | None = None,
    env: dict | None = None,
    clock: Callable[[], str] | None = None,
    probe: Callable[[str], dict] | None = None,
    list_children: Callable[[str, dict], list[dict]] | None = None,
    download_bytes: Callable[[dict, dict], bytes] | None = None,
) -> int:
    """Submete a WO de obter e a de atomizar. Retorna 0 ou 2."""
    base = root or REPO_ROOT
    folder_id = normalize_folder_id(folder)
    policies_dir = policies_dir or (base / "contracts" / "policies")
    roots_path = roots_path or (base / "config" / "drive_inventory_roots_20261016.json")
    wo_dir = wo_dir or (base / "data" / "legado")
    evidence_path = evidence_path or (
        base / "data" / "grc" / "evidencias" / f"drive_{folder_id or 'invalido'}.json"
    )
    runtime_env = dict(os.environ if env is None else env)
    when = clock() if clock else datetime.now(timezone.utc).isoformat()
    year = int(when[:4]) if when[:4].isdigit() else datetime.now(timezone.utc).year
    label = folder_id or "INVALIDO"
    obter_id = f"CE-WO-OBTER-{label}"
    atom_id = f"CE-WO-ATOMIZAR-{label}"
    obter_path = wo_dir / f"autorizacao_WO-OBTER-{label}.json"
    atom_path = wo_dir / f"autorizacao_WO-ATOMIZAR-{label}.json"

    obter = _wo_base(obter_id, "obter", folder_id, when)
    _write_json(obter_path, obter)

    if not FOLDER_RE.fullmatch(folder_id):
        return _close_blocked(
            folder_id=folder_id,
            when=when,
            passed=[],
            failed=[],
            doc={},
            obter=obter,
            obter_path=obter_path,
            atom_id=atom_id,
            atom_path=atom_path,
            evidence_path=evidence_path,
            env=runtime_env,
            blocks=["Identificador de pasta inválido."],
            probe_result=None,
        )

    passed, failed = classify_policies(load_policies(policies_dir))
    doc = roots_document(roots_path)
    blocks = obter_blocks(folder_id, doc, passed, runtime_env)
    if blocks:
        observed = probe(folder_id) if probe else probe_drive_anonymous(folder_id)
        host = observed.get("page_host") or "desconhecido"
        blocks = [
            *blocks,
            f"Consulta anônima: API HTTP {observed.get('list_http')}; página em {host}.",
        ]
        return _close_blocked(
            folder_id=folder_id,
            when=when,
            passed=passed,
            failed=failed,
            doc=doc,
            obter=obter,
            obter_path=obter_path,
            atom_id=atom_id,
            atom_path=atom_path,
            evidence_path=evidence_path,
            env=runtime_env,
            blocks=blocks,
            probe_result=observed,
        )

    lister = list_children or default_list_children
    fetcher = download_bytes or default_download
    try:
        children = lister(folder_id, runtime_env)
    except Exception as exc:
        return _close_blocked(
            folder_id=folder_id,
            when=when,
            passed=passed,
            failed=failed,
            doc=doc,
            obter=obter,
            obter_path=obter_path,
            atom_id=atom_id,
            atom_path=atom_path,
            evidence_path=evidence_path,
            env=runtime_env,
            blocks=[f"Falha ao listar a pasta: {type(exc).__name__}"],
            probe_result=None,
        )

    skipped: list[dict] = []
    payloads: list[tuple[dict, bytes]] = []
    arquivos: list[dict] = []
    total = 0
    for item in children:
        reason = _eligible(item)
        if reason:
            skipped.append({"id": item.get("id"), "name": item.get("name"), "motivo": reason})
            continue
        blob = fetcher(item, runtime_env)
        total += len(blob)
        arquivos.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "mimeType": _mime(item),
                "size": int(_size(item)),
                "sha256": hashlib.sha256(blob).hexdigest(),
            }
        )
        payloads.append((item, blob))

    obter["estado"] = "EXECUTADA"
    obter["bytes_baixados"] = total
    obter["arquivos"] = arquivos
    obter["ignorados"] = skipped
    obter["politicas_gate_aprovado"] = [policy.get("id") for policy in passed]
    obter["motivos"] = []
    _write_json(obter_path, obter)

    atom = _wo_base(atom_id, "atomizar", folder_id, when)
    _write_json(atom_path, atom)
    atom_blocks = atomizar_blocks(folder_id, doc, passed, obter["estado"])
    if atom_blocks:
        atom["estado"] = "BLOQUEADO"
        atom["motivos"] = atom_blocks
        atom["depends_on"] = obter_id
        atom["bytes_baixados"] = total
        _write_json(atom_path, atom)
        _write_evidence(evidence_path, folder_id, passed, failed, obter, atom, None)
        _refuse_secrets([obter_path, atom_path, evidence_path], runtime_env)
        return 2

    policy = next(item for item in passed if policy_lists_folder(item, folder_id))
    written = 0
    rejected = 0
    atoms_dir = base / str(policy.get("atoms_output") or "data/canonical/atoms/drive")
    quarantine_path = base / str(
        policy.get("quarentena_output") or f"data/quarentena/drive/{folder_id}"
    )
    if quarantine_path.suffix == "":
        quarantine_path = quarantine_path / "rejeitados.jsonl"
    for item, blob in payloads:
        try:
            text = blob.decode("utf-8")
        except UnicodeDecodeError:
            rejected += 1
            _append_quarantine(
                quarantine_path,
                {
                    "file_id": item.get("id"),
                    "motivo": "bytes não são UTF-8",
                    "texto": "",
                    "wo_id": atom_id,
                },
            )
            continue
        atoms, quarantine = atomize_text(
            text,
            file_id=str(item.get("id")),
            wo_id=atom_id,
            policy=policy,
            year=year,
        )
        for record in atoms:
            _write_json(atoms_dir / f"{record['id_atomo']}.json", record)
            written += 1
        for record in quarantine:
            _append_quarantine(quarantine_path, record)
            rejected += 1

    atom["depends_on"] = obter_id
    atom["policy_id"] = policy.get("id")
    atom["bytes_baixados"] = total
    atom["atomos_escritos"] = written
    atom["quarentena"] = rejected
    if written == 0:
        atom["estado"] = "BLOQUEADO"
        atom["motivos"] = ["Nenhum átomo válido. O texto fora do contrato foi para quarentena."]
        code = 2
    else:
        atom["estado"] = "EXECUTADA"
        atom["motivos"] = []
        code = 0
    _write_json(atom_path, atom)
    _write_evidence(evidence_path, folder_id, passed, failed, obter, atom, None)
    _refuse_secrets([obter_path, atom_path, evidence_path], runtime_env)
    return code
