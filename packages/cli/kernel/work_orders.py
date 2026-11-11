"""Submissão de WO pelo Kernel antes de obter ou atomizar uma pasta do Drive.

O Kernel não cria raiz, não escolhe política e não baixa sem os gates.
Credencial ausente, pasta fora do registry ou política rejeitada → WO BLOQUEADO e exit 2.
"""
from __future__ import annotations

import hashlib
import importlib
import json
import re
from pathlib import Path
from typing import Any, Callable
from urllib.request import Request, urlopen

PACKAGE_REPO = Path(__file__).resolve().parents[3]
ROOTS_RELATIVE = Path("config/drive_inventory_roots_20261016.json")
AUTHORITY_RELATIVE = Path("data/legado/drive_raizes.json")
FOLDER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,80}$")
LEGAL_RE = re.compile(r"(art\.|artigo|§|inciso|parágrafo|paragrafo)", re.IGNORECASE)
URL_RE = re.compile(r"https://[^\s<>\"]+")
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
RESTRICTIONS = [
    "NO_DELETE",
    "NO_PUBLICATION",
    "NO_CANONICAL_PROMOTION",
    "RIGHTS_GATE_REQUIRED",
]


def _modules():
    cli_dir = Path(__file__).resolve().parents[1]
    for entry in (str(PACKAGE_REPO), str(cli_dir)):
        if entry not in __import__("sys").path:
            __import__("sys").path.insert(0, entry)
    return importlib.import_module("drive_recursive_inventory"), importlib.import_module("kernel.core")


def credentials_present() -> bool:
    """True somente quando o carregador fail-closed devolve um token. O token não é retornado."""
    inventory, _core = _modules()
    try:
        inventory.load_token()
    except inventory.CredentialError:
        return False
    return True


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


def _wo_paths(repo: Path, folder_id: str, tarefa: str) -> tuple[str, Path]:
    wo_id = f"CE-WO-{tarefa.upper()}-{folder_id}"
    path = repo / "data" / "legado" / f"autorizacao_WO-{tarefa.upper()}-{folder_id}.json"
    return wo_id, path


def _evidence_path(repo: Path, folder_id: str) -> Path:
    return repo / "data" / "grc" / "evidencias" / f"drive_{folder_id}.json"


def _dump(path: Path, payload: dict[str, Any]) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        old = _read_json(path) or {}
        if old.get("submitted_at"):
            payload["submitted_at"] = old["submitted_at"]
            payload["data"] = old["submitted_at"]
        same = old.get("estado") == payload.get("estado") and old.get("motivo") == payload.get("motivo")
        payload["tentativas"] = old.get("tentativas", 1) if same else int(old.get("tentativas") or 0) + 1
    else:
        payload["tentativas"] = 1
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def _safe_relative(repo: Path, relative: str) -> Path:
    if not relative or relative.startswith(("/", "\\")) or ".." in Path(relative).parts:
        raise ValueError("caminho de saída da política rejeitado")
    destination = (repo / relative).resolve()
    if not str(destination).startswith(str(repo.resolve())):
        raise ValueError("caminho de saída escapa o repositório")
    return destination


def _policy_document(policy_id: str) -> dict[str, Any]:
    path = PACKAGE_REPO / "contracts" / "policies" / f"{policy_id}.json"
    data = _read_json(path)
    if not data or data.get("id") != policy_id:
        raise KeyError(policy_id)
    return data


def _fonte_slug(policy: dict[str, Any]) -> str:
    source = policy.get("source_contract")
    if not isinstance(source, str):
        raise KeyError("source_contract")
    data = _read_json(PACKAGE_REPO / source)
    slug = (data or {}).get("fonte_slug")
    if not isinstance(slug, str) or not slug:
        raise KeyError("fonte_slug")
    return slug


def wo_required_policy_ids() -> list[str]:
    directory = PACKAGE_REPO / "contracts" / "policies"
    selected = []
    for path in sorted(directory.glob("KERNEL-POLICY-*.json")):
        data = _read_json(path)
        if data and data.get("wo_required") is True and data.get("id") == path.stem:
            selected.append(path.stem)
    return selected


def assess_drive_folder(
    folder_id: str,
    *,
    repo: Path | None = None,
    policy_id: str | None = None,
    credential_present_flag: bool | None = None,
    now: str = "2026-11-11T12:43:49Z",
) -> dict[str, Any]:
    """Avalia os gates e devolve as WO. Não acessa a rede."""
    repo = repo or PACKAGE_REPO
    present = credentials_present() if credential_present_flag is None else credential_present_flag
    roots = _read_json(repo / ROOTS_RELATIVE)
    authority = _read_json(repo / AUTHORITY_RELATIVE)
    root_ids = _root_ids(roots)
    authority_ids = _root_ids(authority)
    common: list[str] = []
    if not FOLDER_ID_RE.fullmatch(folder_id or ""):
        common.append("folder_id inválido")
    if folder_id not in root_ids:
        common.append(f"pasta ausente nas raízes registradas {ROOTS_RELATIVE.as_posix()}")
    if authority is None:
        common.append(f"autoridade {AUTHORITY_RELATIVE.as_posix()} ausente")
    elif folder_id not in authority_ids:
        common.append(f"pasta ausente na autoridade {AUTHORITY_RELATIVE.as_posix()}")
    if not present:
        common.append("nem GDRIVE_SA_KEY nem DRIVE_ACCESS_TOKEN configurado")

    _inventory, core = _modules()
    kernel = core.Kernel()
    policy_gates = []
    for candidate in wo_required_policy_ids():
        policy_gates.append({
            "id": candidate,
            "wo_required": True,
            "exit_code": kernel.check_policy(candidate),
        })

    atom_reasons = list(common)
    if not policy_id:
        atom_reasons.append("política não informada; o Kernel não infere KERNEL-POLICY")
    else:
        gate = next((item["exit_code"] for item in policy_gates if item["id"] == policy_id), None)
        if gate is None:
            try:
                gate = kernel.check_policy(policy_id)
            except (KeyError, FileNotFoundError):
                gate = 2
            policy_gates.append({"id": policy_id, "wo_required": False, "exit_code": gate})
        if gate != 0:
            atom_reasons.append(f"política {policy_id} rejeitada pelo Kernel")

    def build(tarefa: str, reasons: list[str]) -> dict[str, Any]:
        wo_id, _path = _wo_paths(repo, folder_id, tarefa)
        blocked = bool(reasons)
        return {
            "acao_necessaria": (
                "Registrar a pasta na autoridade e nas raízes, configurar credencial de leitura "
                "e informar a KERNEL-POLICY aplicável. O Kernel não baixa nem atomiza antes disso."
            ),
            "atoms_written": 0,
            "autorizado_por": "kernel",
            "bytes_acquired": False,
            "data": now,
            "estado": "BLOQUEADO" if blocked else "SUBMETIDA",
            "folder_id": folder_id,
            "motivo": " | ".join(reasons) if reasons else "",
            "policy_id": policy_id if tarefa == "atomizar" else None,
            "restrictions": list(RESTRICTIONS),
            "schema": "CE-WO-AUTHORIZATION-1.0.0",
            "sha256_fonte": None,
            "submitted_at": now,
            "submitted_by": "kernel",
            "tarefa": tarefa,
            "wo_id": wo_id,
        }

    orders = [build("obter", common), build("atomizar", atom_reasons)]
    exit_code = 2 if any(order["estado"] == "BLOQUEADO" for order in orders) else 0
    return {
        "schema": "CE-WO-DRIVE-RUN-1.0.0",
        "atoms_written": 0,
        "authority_present": authority is not None,
        "bytes_acquired": False,
        "credential_present": present,
        "exit_code": exit_code,
        "folder_id": folder_id,
        "now": now,
        "orders": orders,
        "policy_gates": policy_gates,
        "policy_id": policy_id,
        "registered_root_ids": root_ids,
        "repo": repo,
        "restrictions": list(RESTRICTIONS),
        "submitted_by": "kernel",
    }


def _persist(assessment: dict[str, Any]) -> dict[str, Any]:
    repo: Path = assessment["repo"]
    written = []
    for order in assessment["orders"]:
        _wo_id, path = _wo_paths(repo, assessment["folder_id"], order["tarefa"])
        if _dump(path, order):
            written.append(path.relative_to(repo).as_posix())
    evidence = {
        key: value
        for key, value in assessment.items()
        if key not in {"repo", "now"}
    }
    evidence_path = _evidence_path(repo, assessment["folder_id"])
    if _dump(evidence_path, evidence):
        written.append(evidence_path.relative_to(repo).as_posix())
    public = dict(evidence)
    public["files_written"] = written
    return public


def _canonical_id(legacy_id: str, year: int) -> str:
    digest = hashlib.sha256(legacy_id.encode("utf-8")).hexdigest()
    return f"NORM-{year}-{int(digest[:12], 16)}"


def _official_url(text: str) -> str | None:
    _inventory, core = _modules()
    validator = core.VALIDATORS["url_validator"]
    for match in URL_RE.findall(text):
        candidate = match.rstrip(".,;)")
        ok, _error = validator.validate({"link_fonte": candidate})
        if ok:
            return candidate
    return None


def _quarantine(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def atomize_text(
    *,
    text: str,
    file_id: str,
    policy_id: str,
    wo_id: str,
    repo: Path,
    now: str,
) -> dict[str, int]:
    """Aplica a política já aprovada. Texto fora do contrato vai inteiro para a quarentena."""
    policy = _policy_document(policy_id)
    slug = _fonte_slug(policy)
    atoms_dir = _safe_relative(repo, policy["atoms_output"])
    quarantine_dir = _safe_relative(repo, policy.get("quarentena_output") or f"data/quarentena/{policy_id}")
    quarantine_file = quarantine_dir / "validacao_invalida.jsonl"
    _inventory, core = _modules()
    kernel = core.Kernel()
    from packages.schemas.invariantes import AtomoBlindado

    year = int(now[:4])
    counts = {"aprovados": 0, "quarentena": 0}
    lines = text.splitlines() or [text]
    for index, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line:
            continue
        legacy_id = f"{file_id}:{index}"
        sha = hashlib.sha256(line.encode("utf-8")).hexdigest()
        url = _official_url(line)
        motivo = None
        if len(line) < 10 or len(line) > 800:
            motivo = "texto_curto" if len(line) < 10 else "acima_contrato"
        elif any(term in line.lower() for term in OPINATIVE):
            motivo = "termo_opinativo"
        elif not LEGAL_RE.search(line):
            motivo = "sem_dispositivo"
        elif not url:
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
        decision = kernel.evaluate(atom, policy_id)
        if decision.decision != core.Decision.APPROVED:
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
            AtomoBlindado.model_validate(atom)
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
        target = atoms_dir / f"{atom['id_atomo']}.json"
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
        target.write_text(json.dumps(atom, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
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
    stripped = payload.lstrip().lower()
    if stripped.startswith(HTML_PREFIXES):
        raise ValueError("resposta HTML em vez de arquivo")
    return payload


def _default_acquire(folder_id: str) -> list[dict[str, Any]]:
    inventory, _core = _modules()
    token = inventory.load_token()
    crawled = inventory.crawl([{"id": folder_id, "name": folder_id}], token)
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
    """Executa somente a WO que o Kernel deixou SUBMETIDA. BLOQUEADO não chama o Drive."""
    obter = next(order for order in assessment["orders"] if order["tarefa"] == "obter")
    atomizar = next(order for order in assessment["orders"] if order["tarefa"] == "atomizar")
    if obter["estado"] != "SUBMETIDA":
        return _persist(assessment)

    repo: Path = assessment["repo"]
    folder_id = assessment["folder_id"]
    files = (acquire or _default_acquire)(folder_id)
    usable = [item for item in files if item.get("data")]
    rejected = len(files) - len(usable)
    manifest = [
        {
            "id": item["id"],
            "name": item["name"],
            "sha256": hashlib.sha256(item["data"]).hexdigest(),
        }
        for item in usable
    ]
    manifest_sha = hashlib.sha256(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest() if manifest else None
    obter["arquivos_rejeitados"] = rejected
    obter["bytes_acquired"] = bool(usable)
    obter["sha256_fonte"] = manifest_sha
    obter["estado"] = "PASS" if usable else "BLOQUEADO"
    if not usable:
        obter["motivo"] = "nenhum arquivo textual adquirido"

    counts = {"aprovados": 0, "quarentena": 0}
    if atomizar["estado"] == "SUBMETIDA" and usable and assessment.get("policy_id") and manifest_sha:
        for item in usable:
            try:
                text = item["data"].decode("utf-8")
            except UnicodeDecodeError:
                rejected += 1
                continue
            part = atomize_text(
                text=text,
                file_id=item["id"],
                policy_id=assessment["policy_id"],
                wo_id=atomizar["wo_id"],
                repo=repo,
                now=assessment["now"],
            )
            counts["aprovados"] += part["aprovados"]
            counts["quarentena"] += part["quarentena"]
        atomizar["arquivos_rejeitados"] = rejected
        atomizar["atoms_written"] = counts["aprovados"]
        atomizar["sha256_fonte"] = manifest_sha
        atomizar["bytes_acquired"] = True
        if counts["aprovados"] or counts["quarentena"]:
            atomizar["estado"] = "PASS"
            atomizar["motivo"] = ""
        else:
            atomizar["estado"] = "BLOQUEADO"
            atomizar["motivo"] = "nenhum texto normativo para atomizar"
    elif atomizar["estado"] == "SUBMETIDA":
        atomizar["estado"] = "BLOQUEADO"
        atomizar["motivo"] = "obter não produziu sha256_fonte"

    assessment["bytes_acquired"] = bool(usable)
    assessment["atoms_written"] = counts["aprovados"]
    assessment["exit_code"] = 0 if all(order["estado"] == "PASS" for order in assessment["orders"]) else 2
    return _persist(assessment)


def run_drive_folder(
    folder_id: str,
    *,
    repo: Path | None = None,
    policy_id: str | None = None,
    credential_present_flag: bool | None = None,
    now: str = "2026-11-11T12:43:49Z",
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
        return execute_authorized(assessment, acquire=acquire)
    return _persist(assessment)
