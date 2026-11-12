"""Baixa uma pasta do Drive e atomiza só o que a política validada cobre.

Toda atividade (obter e atomizar) recebe WO submetida pelo Kernel antes
de qualquer leitura. Sem credencial, a WO fica BLOQUEADO e nenhum átomo
é inventado.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

from kernel.atomize import atomize_documents, build_needles, classify_name
from kernel.core import Kernel
from kernel.work_orders import (
    WorkOrderRejected,
    repo_root,
    require_open,
    update_work_order,
)

try:
    from drive_recursive_inventory import CredentialError, crawl, list_page, load_token
except ImportError:  # pragma: no cover
    from packages.cli.drive_recursive_inventory import (
        CredentialError,
        crawl,
        list_page,
        load_token,
    )

_FOLDER_ID = re.compile(r"^[A-Za-z0-9_-]{10,80}$")
_MAX_BYTES = 50 * 1024 * 1024
_TEXT_MIME_PREFIXES = ("text/",)
_TEXT_MIMES = {
    "application/json",
    "application/xml",
    "application/xhtml+xml",
}
_EXPORTS = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}
_FOLDER = "application/vnd.google-apps.folder"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root()).as_posix()
    except ValueError:
        return str(path)


def _evidence_path(folder_id: str, evidence_path: Path | None) -> Path:
    if evidence_path is not None:
        return Path(evidence_path)
    return repo_root() / "data" / "grc" / "evidencias" / f"drive_atomize_{folder_id}.json"


def _write_evidence(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def download_bytes(file_id: str, mime: str, token_getter: Callable[[], str]) -> bytes:
    """Baixa bytes de um arquivo do Drive. Recusa id fora do alfabeto do Drive."""
    from urllib.error import HTTPError, URLError
    from urllib.parse import urlencode
    from urllib.request import Request, urlopen

    if not _FOLDER_ID.fullmatch(file_id):
        raise ValueError(f"id de arquivo inválido: {file_id}")
    if mime in _EXPORTS:
        query = urlencode({"mimeType": _EXPORTS[mime], "supportsAllDrives": "true"})
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}/export?{query}"
    else:
        query = urlencode({"alt": "media", "supportsAllDrives": "true"})
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?{query}"
    request = Request(
        url,
        headers={"Authorization": "Bearer " + token_getter(), "Accept": "*/*"},
    )
    try:
        with urlopen(request, timeout=60) as response:
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = response.read(256 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if total > _MAX_BYTES:
                    raise ValueError(f"arquivo acima de {_MAX_BYTES} bytes")
                chunks.append(chunk)
            return b"".join(chunks)
    except HTTPError as exc:
        raise RuntimeError(f"Drive HTTP {exc.code} ao baixar {file_id}") from exc
    except URLError as exc:
        raise RuntimeError(f"Falha de rede ao baixar {file_id}: {exc.reason}") from exc


def _is_text(mime: str, payload: bytes) -> bool:
    if payload.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        return False
    if mime in _EXPORTS or mime in _TEXT_MIMES or mime.startswith(_TEXT_MIME_PREFIXES):
        return True
    return False


def _block(wo: dict[str, Any], motivo: str) -> dict[str, Any]:
    if wo.get("status") == "BLOQUEADO" and wo.get("motivo") == motivo:
        return wo
    if wo.get("status") != "SUBMITTED":
        wo = update_work_order(wo["_path"], status="SUBMITTED", motivo=None)
        require_open(wo, wo["policy_id"], wo["activity"])
    return update_work_order(wo["_path"], status="BLOQUEADO", motivo=motivo)


def _pass(wo: dict[str, Any], resultado: str) -> dict[str, Any]:
    if wo.get("status") != "SUBMITTED":
        wo = update_work_order(wo["_path"], status="SUBMITTED", motivo=None)
    return update_work_order(wo["_path"], status="PASS", motivo=None, resultado=resultado)


def _validated_policies(kernel: Kernel) -> tuple[list[str], list[dict[str, str]]]:
    valid: list[str] = []
    rejected: list[dict[str, str]] = []
    for policy in kernel.registry.list_policies():
        code = kernel.gate(policy.id)
        if code == 0:
            valid.append(policy.id)
        else:
            rejected.append({"id": policy.id, "reason": f"gate exit {code}"})
    return valid, rejected


def execute_drive_folder(
    folder_id: str,
    *,
    wo_dir: Path | None = None,
    evidence_path: Path | None = None,
    dest_root: Path | None = None,
    token_loader: Callable[[], Any] | None = None,
    fetcher: Callable[..., dict] | None = None,
    downloader: Callable[[str, str, Callable[[], str]], bytes] | None = None,
) -> int:
    """Executa obter + atomizar. Exit 2 se a obtenção não ocorrer."""
    if not _FOLDER_ID.fullmatch(folder_id):
        raise WorkOrderRejected(f"Id de pasta inválido: {folder_id}")

    kernel = Kernel()
    destination = Path(dest_root) if dest_root is not None else repo_root()
    evidence = _evidence_path(folder_id, evidence_path)
    evidence_ref = _rel(evidence)
    valid, rejected = _validated_policies(kernel)
    if not valid:
        _write_evidence(
            evidence,
            {
                "schema": "CE-DRIVE-ATOMIZE-RUN-1.0.0",
                "folder_id": folder_id,
                "policies_validated": [],
                "policies_rejected": rejected,
                "work_orders": [],
                "download": {"status": "BLOQUEADO", "motivo": "Nenhuma política validada pelo Kernel."},
                "atoms_written": 0,
            },
        )
        return 2

    obter_wos = []
    atom_wos = []
    for policy_id in valid:
        obter_wos.append(
            kernel.submit_work_order(
                policy_id,
                "obter",
                folder_id,
                rationale=f"Obter arquivos da pasta Drive {folder_id} para {policy_id}.",
                wo_dir=wo_dir,
                evidence_reference=evidence_ref,
            )
        )
        atom_wos.append(
            kernel.submit_work_order(
                policy_id,
                "atomizar",
                folder_id,
                rationale=f"Atomizar arquivos classificados em {policy_id} a partir da pasta {folder_id}.",
                wo_dir=wo_dir,
                evidence_reference=evidence_ref,
            )
        )

    loader = token_loader or load_token

    files: list[dict[str, Any]] = []
    obtain_motivo = None
    try:
        token = loader()
        inventory = crawl(
            [{"id": folder_id, "name": folder_id}],
            token,
            fetch=fetcher or list_page,
        )
    except CredentialError as exc:
        obtain_motivo = str(exc)
        token = None
        inventory = None
    except Exception as exc:
        obtain_motivo = f"Falha ao listar a pasta: {exc}"
        token = None
        inventory = None

    needles = build_needles(kernel.registry.list_policies())
    valid_ids = set(valid)
    per_policy_docs: dict[str, list[dict[str, str]]] = {policy_id: [] for policy_id in valid}
    per_policy_block: dict[str, str] = {}

    if obtain_motivo:
        for wo in obter_wos:
            _block(wo, obtain_motivo)
        for wo in atom_wos:
            _block(wo, f"obter BLOQUEADO: {obtain_motivo}")
    else:
        assert inventory is not None and token is not None
        try:
            from utils import aplicar_mascara
        except ImportError:  # pragma: no cover
            from packages.cli.utils import aplicar_mascara
        reader = downloader or download_bytes
        getter = token if callable(token) else (lambda: token)
        for item in inventory["items"]:
            if item["kind"] == "folder" or item["mime_type"] == _FOLDER:
                continue
            policy_id, reason = classify_name(item["path"], needles, valid_ids)
            record: dict[str, Any] = {
                "id": item["id"],
                "name": item["path"],
                "mime_type": item["mime_type"],
                "classification": reason,
                "policy_id": policy_id,
            }
            if policy_id is None:
                record["disposition"] = reason
                files.append(record)
                continue
            size = item.get("size_bytes")
            if isinstance(size, int) and size > _MAX_BYTES:
                record["disposition"] = "acima_50mb"
                per_policy_block.setdefault(policy_id, "arquivo acima de 50MB")
                files.append(record)
                continue
            try:
                payload = reader(item["id"], item["mime_type"], getter)
            except Exception as exc:
                record["disposition"] = "download_falhou"
                record["motivo"] = str(exc)
                per_policy_block.setdefault(policy_id, str(exc))
                files.append(record)
                continue
            record["sha256"] = hashlib.sha256(payload).hexdigest()
            if item["path"].lower().endswith(".zip"):
                record["disposition"] = "ZIP_CONTENTS_NOT_INSPECTED"
                per_policy_block.setdefault(policy_id, "ZIP_CONTENTS_NOT_INSPECTED")
                files.append(record)
                continue
            if not _is_text(item["mime_type"], payload):
                record["disposition"] = "formato_sem_parser"
                per_policy_block.setdefault(policy_id, "formato_sem_parser")
                files.append(record)
                continue
            text = aplicar_mascara(payload.decode("utf-8", errors="replace"))
            record["disposition"] = "TEXTO_PARA_ATOMIZAR"
            files.append(record)
            per_policy_docs[policy_id].append(
                {"id": item["id"], "name": item["path"], "text": text}
            )
            raw_dir = destination / "data" / "raw" / "drive" / folder_id
            raw_dir.mkdir(parents=True, exist_ok=True)
            (raw_dir / f"{item['id']}.txt").write_text(text, encoding="utf-8")

        for wo in obter_wos:
            _pass(wo, f"listados={inventory['items_count']}")

    atoms_written = 0
    if obtain_motivo is None:
        for wo in atom_wos:
            policy_id = wo["policy_id"]
            documents = per_policy_docs.get(policy_id) or []
            summary = None
            if documents:
                if wo.get("status") != "SUBMITTED":
                    wo = update_work_order(wo["_path"], status="SUBMITTED", motivo=None)
                summary = atomize_documents(kernel, policy_id, wo, documents, destination)
                atoms_written += summary["atoms_written"]
            if policy_id in per_policy_block:
                _block(wo, per_policy_block[policy_id])
                continue
            if summary is None:
                _pass(wo, "SEM_ARQUIVOS_DA_POLITICA")
            else:
                _pass(
                    wo,
                    f"atoms={summary['atoms_written']};quarentena={summary['quarantined']}",
                )

    final_wos = []
    for wo in [*obter_wos, *atom_wos]:
        refreshed = json.loads(Path(wo["_path"]).read_text(encoding="utf-8"))
        final_wos.append(
            {
                "wo_id": refreshed.get("wo_id"),
                "policy_id": refreshed.get("policy_id"),
                "activity": refreshed.get("activity"),
                "status": refreshed.get("status"),
                "motivo": refreshed.get("motivo"),
                "resultado": refreshed.get("resultado"),
                "path": _rel(Path(wo["_path"])),
            }
        )

    exit_code = 2 if obtain_motivo or any(item["status"] == "BLOQUEADO" for item in final_wos) else 0
    _write_evidence(
        evidence,
        {
            "schema": "CE-DRIVE-ATOMIZE-RUN-1.0.0",
            "folder_id": folder_id,
            "policies_validated": valid,
            "policies_rejected": rejected,
            "work_orders": final_wos,
            "download": {
                "status": "BLOQUEADO" if obtain_motivo else "PASS",
                "motivo": obtain_motivo,
                "files": files,
            },
            "atoms_written": atoms_written,
            "restrictions": ["NO_PUBLICATION", "NO_DELETE", "NO_INVENT_ATOMS"],
        },
    )
    return exit_code
