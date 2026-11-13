"""Baixa uma pasta do Drive e atomiza só sob política que o Kernel aprovou.

Cada atividade (obter, atomizar) exige WO submetida pelo Kernel antes de
qualquer escrita. Sem credencial ou sem política válida o processo para
em BLOQUEADO (exit 2) e não promove átomo.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote
from urllib.request import Request, urlopen

from packages.cli.drive_recursive_inventory import (
    CredentialError,
    crawl,
    load_token,
)
from packages.cli.kernel.core import VALIDATORS, Kernel, _ensure_validators
from packages.cli.kernel.work_orders import (
    assess_all_policies,
    record_execution,
    submit_work_order,
)
from packages.cli.utils import aplicar_mascara
from packages.schemas.invariantes import AtomoBlindado

REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_BYTES = 50 * 1024 * 1024
FOLDER_RE = re.compile(r"^[A-Za-z0-9_-]{20,80}$")
EXPORT_MIME = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return stripped.lower()


def _safe_error(exc: BaseException) -> str:
    text = f"{type(exc).__name__}: {exc}"
    text = re.sub(r"ya29\.[0-9A-Za-z\-_]+", "[REDACTED]", text)
    text = re.sub(r"Bearer\s+\S+", "Bearer [REDACTED]", text, flags=re.IGNORECASE)
    return text[:500]


def wo_id_for(folder_id: str, task: str) -> str:
    if not FOLDER_RE.fullmatch(folder_id):
        raise ValueError("folder_id inválido")
    if task not in {"obter", "atomizar"}:
        raise ValueError("tarefa inválida")
    return f"CE-WO-DRIVE-{folder_id}-{task.upper()}"


def matching_policies(text: str, filename: str) -> list[str]:
    """Famílias normativas reconhecidas. Mais de uma família é ambíguo."""
    hay = _fold(f"{filename}\n{text}")
    found: list[str] = []
    if re.search(r"\bcofen\b", hay):
        found.append("KERNEL-POLICY-001")
    if re.search(r"\banvisa\b", hay):
        found.append("KERNEL-POLICY-002")
    lei = "lei federal" in hay or re.search(r"\blei\s+n[.o]?\s*\d", hay)
    autoridade = any(token in hay for token in ("presidencia da republica", "planalto", "congresso nacional"))
    if lei and autoridade:
        found.append("KERNEL-POLICY-020")
    if "portaria" in hay and ("ministerio da saude" in hay or "gabinete do ministro" in hay):
        found.append("KERNEL-POLICY-019")
    return found


def select_policy(text: str, filename: str, valid_ids: set[str]) -> str | None:
    found = matching_policies(text, filename)
    if len(found) != 1:
        return None
    policy_id = found[0]
    if policy_id not in valid_ids:
        return None
    return policy_id


def normalize_text(text: str) -> str:
    compacted = re.sub(r"\s+", " ", text).strip()
    return unicodedata.normalize("NFC", compacted)


def split_segments(text: str) -> list[str]:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    pieces: list[str] = []
    for chunk in re.split(r"\n\s*\n", text):
        parts = re.split(r"(?=\bArt\.?\s+\d+)", chunk)
        for part in parts:
            cleaned = part.strip()
            if cleaned:
                pieces.append(cleaned)
    return pieces


def _year_of(text: str, fallback: int) -> int:
    match = re.search(r"\b((?:19|20)\d{2})\b", text)
    if not match:
        return fallback
    return int(match.group(1))


def canonical_id(legacy_id: str, year: int) -> str:
    digest = hashlib.sha256(legacy_id.encode("utf-8")).hexdigest()
    number = int(digest[:12], 16)
    return f"NORM-{year}-{number}"


def find_allowed_link(text: str) -> str | None:
    _ensure_validators()
    validator = VALIDATORS.get("url_validator")
    if validator is None:
        return None
    for match in re.finditer(r"https://[^\s<>'\"]+", text):
        candidate = match.group(0).rstrip(".,;)")
        ok, _error = validator.validate({"link_fonte": candidate})
        if ok:
            return candidate
    return None


def _quarantine_item(
    *,
    motivo: str,
    arquivo: str,
    texto: str,
    wo_id: str,
    policy_id: str | None,
    file_id: str,
) -> dict[str, Any]:
    masked = aplicar_mascara(texto)
    material = masked if masked else f"{file_id}:{motivo}"
    return {
        "motivo": motivo,
        "sha256_original": _sha256(material.encode("utf-8")),
        "arquivo": arquivo,
        "file_id": file_id,
        "policy_id": policy_id,
        "wo_id": wo_id,
        "texto_regra_inteiro": masked,
    }


def atomize_document(
    *,
    text: str,
    file_id: str,
    file_name: str,
    policy_id: str,
    fonte_slug: str,
    wo_id: str,
    link_fonte: str | None,
    year_fallback: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Transforma texto mascarado em átomos ou registros de quarentena."""
    kernel = Kernel()
    atoms: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    segments = split_segments(aplicar_mascara(text))
    if not segments:
        rejected.append(
            _quarantine_item(
                motivo="texto_vazio",
                arquivo=file_name,
                texto="",
                wo_id=wo_id,
                policy_id=policy_id,
                file_id=file_id,
            )
        )
        return atoms, rejected

    for index, segment in enumerate(segments):
        masked = aplicar_mascara(segment)
        normalized = normalize_text(masked)
        length = len(normalized)
        if length < 10 or length > 800:
            rejected.append(
                _quarantine_item(
                    motivo="texto_curto" if length < 10 else "acima_contrato",
                    arquivo=file_name,
                    texto=masked,
                    wo_id=wo_id,
                    policy_id=policy_id,
                    file_id=file_id,
                )
            )
            continue

        legacy_id = f"DRIVE:{file_id}:SEG:{index:04d}"
        year = _year_of(normalized, year_fallback)
        marker = re.match(r"(Art\.?\s+\d+[A-Za-zºo°.\-]*)", normalized)
        atom = {
            "id_atomo": canonical_id(legacy_id, year),
            "versao_contrato": "1.2.0",
            "fonte_slug": fonte_slug,
            "norma_origem": f"DRIVE_{file_id}",
            "dispositivo_legal": marker.group(1) if marker else "trecho",
            "texto_regra": normalized,
            "idioma": "pt-BR",
            "sha256_texto": _sha256(normalized.encode("utf-8")),
            "sha256_original": _sha256(masked.encode("utf-8")),
            "hash_status": "CONFERIDO",
            "vigencia": "NAO_VERIFICADO",
            "data_verificacao": date.today().isoformat(),
            "wo_id": wo_id,
        }
        if link_fonte:
            atom["link_fonte"] = link_fonte

        try:
            checked = AtomoBlindado.model_validate(atom).model_dump(mode="json")
        except Exception as exc:
            motivo = "termo_opinativo" if "opinativo" in str(exc).lower() else "acima_contrato"
            rejected.append(
                _quarantine_item(
                    motivo=motivo,
                    arquivo=file_name,
                    texto=masked,
                    wo_id=wo_id,
                    policy_id=policy_id,
                    file_id=file_id,
                )
            )
            continue

        decision = kernel.evaluate(checked, policy_id)
        if decision.decision.value != "APPROVED":
            detail = "; ".join(item.error or item.validator_name for item in decision.results if not item.is_valid)
            rejected.append(
                _quarantine_item(
                    motivo=f"kernel_rejeitou:{detail[:180] or decision.decision.value}",
                    arquivo=file_name,
                    texto=masked,
                    wo_id=wo_id,
                    policy_id=policy_id,
                    file_id=file_id,
                )
            )
            continue
        atoms.append(checked)
    return atoms, rejected


def _output_path(repo_root: Path, relative: str, leaf: str) -> Path:
    if not relative or relative.startswith("/") or ".." in Path(relative).parts:
        raise ValueError(f"caminho de política recusado: {relative}")
    path = (repo_root / relative / leaf).resolve()
    root = repo_root.resolve()
    if root not in path.parents and path != root:
        raise ValueError("caminho de saída escapa o repositório")
    return path


def _append_quarantine(path: Path, rows: list[dict[str, Any]]) -> int:
    seen: set[str] = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                current = json.loads(line)
            except json.JSONDecodeError:
                continue
            sha = current.get("sha256_original")
            if isinstance(sha, str):
                seen.add(sha)
    fresh = [row for row in rows if row.get("sha256_original") not in seen]
    if not fresh:
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in fresh:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(fresh)


def _write_atoms(repo_root: Path, relative_dir: str, atoms: list[dict[str, Any]]) -> tuple[int, list[dict[str, Any]]]:
    written = 0
    conflicts: list[dict[str, Any]] = []
    for atom in atoms:
        path = _output_path(repo_root, relative_dir, f"{atom['id_atomo']}.json")
        if path.exists():
            current = json.loads(path.read_text(encoding="utf-8"))
            if current.get("sha256_texto") == atom.get("sha256_texto"):
                continue
            conflicts.append(atom)
            continue
        _atomic_write(path, json.dumps(atom, ensure_ascii=False, indent=2) + "\n")
        written += 1
    return written, conflicts


def extract_text(data: bytes, mime: str, name: str) -> str | None:
    """Devolve texto ou None quando o tipo não entra na atomização."""
    if mime in EXPORT_MIME or mime.startswith("text/") or name.lower().endswith((".txt", ".csv", ".json", ".md")):
        return data.decode("utf-8", errors="replace")
    if mime == "application/pdf" or name.lower().endswith(".pdf"):
        from pypdf import PdfReader

        reader = PdfReader(io.BytesIO(data))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return None


def download_bytes(file_id: str, mime: str, token: Callable[[], str], opener=urlopen) -> bytes:
    if mime in EXPORT_MIME:
        url = (
            "https://www.googleapis.com/drive/v3/files/"
            f"{quote(file_id, safe='')}/export?mimeType={quote(EXPORT_MIME[mime], safe='')}"
        )
    else:
        url = f"https://www.googleapis.com/drive/v3/files/{quote(file_id, safe='')}?alt=media"
    request = Request(url, headers={"Authorization": "Bearer " + token(), "Accept": "*/*"})
    with opener(request, timeout=60) as response:
        payload = response.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError("arquivo acima de 50MB")
    return payload


def _policy_index(gate: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["policy_id"]: item for item in gate["results"] if item.get("passed")}


def _persist_documents(
    *,
    repo_root: Path,
    documents: list[dict[str, Any]],
    gate: dict[str, Any],
    wo_id: str,
    year_fallback: int,
) -> dict[str, Any]:
    policies = _policy_index(gate)
    valid_ids = set(policies)
    atoms_by_policy: dict[str, list[dict[str, Any]]] = {}
    quarantine_by_policy: dict[str, list[dict[str, Any]]] = {}
    file_reports: list[dict[str, Any]] = []

    for document in documents:
        text = document.get("text") or ""
        file_name = document["name"]
        file_id = document["id"]
        if document.get("skip_reason"):
            row = _quarantine_item(
                motivo=document["skip_reason"],
                arquivo=file_name,
                texto=text,
                wo_id=wo_id,
                policy_id=None,
                file_id=file_id,
            )
            quarantine_by_policy.setdefault("_sem_politica", []).append(row)
            file_reports.append({"id": file_id, "name": file_name, "policy_id": None, "motivo": document["skip_reason"]})
            continue

        found = matching_policies(text, file_name)
        policy_id = select_policy(text, file_name, valid_ids)
        if policy_id is None:
            motivo = "politica_ambigua" if len(found) > 1 else "fonte_sem_politica_valida"
            row = _quarantine_item(
                motivo=motivo,
                arquivo=file_name,
                texto=text,
                wo_id=wo_id,
                policy_id=None,
                file_id=file_id,
            )
            quarantine_by_policy.setdefault("_sem_politica", []).append(row)
            file_reports.append({"id": file_id, "name": file_name, "policy_id": None, "motivo": motivo})
            continue

        info = policies[policy_id]
        link = find_allowed_link(text)
        atoms, rejected = atomize_document(
            text=text,
            file_id=file_id,
            file_name=file_name,
            policy_id=policy_id,
            fonte_slug=str(info.get("fonte_slug") or ""),
            wo_id=wo_id,
            link_fonte=link,
            year_fallback=year_fallback,
        )
        atoms_by_policy.setdefault(policy_id, []).extend(atoms)
        quarantine_by_policy.setdefault(policy_id, []).extend(rejected)
        file_reports.append(
            {
                "id": file_id,
                "name": file_name,
                "policy_id": policy_id,
                "atomos": len(atoms),
                "quarentena": len(rejected),
                "sha256_bytes": document.get("sha256_bytes"),
            }
        )

    written = 0
    for policy_id, atoms in atoms_by_policy.items():
        info = policies[policy_id]
        count, conflicts = _write_atoms(repo_root, info["atoms_output"], atoms)
        written += count
        for atom in conflicts:
            quarantine_by_policy.setdefault(policy_id, []).append(
                _quarantine_item(
                    motivo="conflito_duplicata",
                    arquivo=atom["id_atomo"],
                    texto=atom["texto_regra"],
                    wo_id=wo_id,
                    policy_id=policy_id,
                    file_id=atom.get("norma_origem") or policy_id,
                )
            )

    quarantined = 0
    for policy_id, rows in quarantine_by_policy.items():
        if policy_id == "_sem_politica":
            relative = "data/quarentena/sem_politica"
        else:
            relative = policies[policy_id]["quarentena_output"]
        quarantined += _append_quarantine(_output_path(repo_root, relative, "rejeicoes.jsonl"), rows)

    return {
        "arquivos": len(file_reports),
        "atomos_gravados": written,
        "quarentena_gravada": quarantined,
        "relatorio": file_reports,
    }


def run_drive_job(
    *,
    folder_id: str,
    source: str,
    repo_root: Path | None = None,
    wo_dir: Path | None = None,
    evidence_dir: Path | None = None,
    token_loader: Callable[[], Any] | None = None,
    fetch: Callable | None = None,
    downloader: Callable[..., bytes] | None = None,
    year_fallback: int | None = None,
) -> int:
    """Executa obter e atomizar. Devolve 0 ou 2."""
    if not FOLDER_RE.fullmatch(folder_id):
        raise ValueError("folder_id inválido")
    if folder_id not in source:
        raise ValueError("source não contém o folder_id informado")

    root = repo_root or REPO_ROOT
    orders = wo_dir or (root / "data" / "legado")
    evidence_root = evidence_dir or (root / "evidence")
    year = year_fallback or datetime.now(timezone.utc).year
    gate = assess_all_policies()
    obter_id = wo_id_for(folder_id, "obter")
    atom_id = wo_id_for(folder_id, "atomizar")
    obter = submit_work_order(
        wo_dir=orders,
        wo_id=obter_id,
        task="obter",
        slug=f"drive_{folder_id}_obter",
        source=source,
        folder_id=folder_id,
        gate=gate,
    )
    atom = submit_work_order(
        wo_dir=orders,
        wo_id=atom_id,
        task="atomizar",
        slug=f"drive_{folder_id}_atomizar",
        source=source,
        folder_id=folder_id,
        gate=gate,
        depends_on=obter["wo_id"],
    )
    authorized = set(obter.get("policy_ids") or [])
    effective_results = []
    for item in gate["results"]:
        passed = bool(item["passed"]) and item["policy_id"] in authorized
        reason = item["reason"]
        if item["passed"] and item["policy_id"] not in authorized:
            reason = "fora da WO submetida"
        effective_results.append({**item, "passed": passed, "reason": reason})
    gate = {
        **gate,
        "results": effective_results,
        "valid_policy_ids": [item["policy_id"] for item in effective_results if item["passed"]],
    }

    def finish(code: int, obter_status: str, atom_status: str, motivo: str | None, resultado: dict[str, Any] | None) -> int:
        obter_row = record_execution(orders, obter["wo_id"], status=obter_status, motivo=motivo if obter_status != "PASS" else None, resultado=resultado)
        atom_motivo = motivo if atom_status != "PASS" else None
        if atom_status != "PASS" and obter_status != "PASS":
            atom_motivo = f"Dependência {obter['wo_id']} está {obter_status}."
        atom_row = record_execution(orders, atom["wo_id"], status=atom_status, motivo=atom_motivo, resultado=resultado if atom_status == "PASS" else None)
        payload = {
            "schema": "CE-DRIVE-ATOMIZE-RUN-1.0.0",
            "folder_id": folder_id,
            "source": source,
            "recorded_at": _now(),
            "exit_code": code,
            "valid_policy_ids": gate["valid_policy_ids"],
            "policy_gate": [
                {"policy_id": item["policy_id"], "passed": item["passed"], "reason": item["reason"]}
                for item in gate["results"]
            ],
            "work_orders": [
                {"wo_id": obter_row["wo_id"], "status": obter_row["status"], "motivo": obter_row.get("motivo")},
                {"wo_id": atom_row["wo_id"], "status": atom_row["status"], "motivo": atom_row.get("motivo")},
            ],
            "resultado": resultado,
        }
        _atomic_write(
            evidence_root / obter_id / "resultado.json",
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        )
        return code

    if not gate["valid_policy_ids"]:
        return finish(2, "BLOQUEADO", "BLOQUEADO", "Nenhuma política passou no gate do Kernel.", None)

    loader = token_loader or load_token
    try:
        token = loader()
    except CredentialError as exc:
        return finish(2, "BLOQUEADO", "BLOQUEADO", _safe_error(exc), None)

    try:
        inventory = crawl([{"id": folder_id, "name": folder_id}], token, fetch=fetch)
        documents: list[dict[str, Any]] = []
        getter = downloader or download_bytes
        for item in inventory["items"]:
            if item["kind"] != "file":
                continue
            name = item["path"]
            mime = item["mime_type"]
            size = item.get("size_bytes")
            if name.lower().endswith(".zip") or mime in {"application/zip", "application/x-zip-compressed"}:
                documents.append({"id": item["id"], "name": name, "text": "", "skip_reason": "zip_nao_inspecionado"})
                continue
            if isinstance(size, int) and size > MAX_BYTES:
                documents.append({"id": item["id"], "name": name, "text": "", "skip_reason": "acima_50mb"})
                continue
            payload = getter(item["id"], mime, token)
            digest = _sha256(payload)
            if mime.startswith("application/vnd.google-apps.") and mime not in EXPORT_MIME:
                documents.append({
                    "id": item["id"], "name": name, "text": "", "sha256_bytes": digest,
                    "skip_reason": "mime_nao_suportado",
                })
                continue
            try:
                text = extract_text(payload, mime, name)
            except Exception as exc:
                documents.append({
                    "id": item["id"], "name": name, "text": "", "sha256_bytes": digest,
                    "skip_reason": f"extracao_falhou:{_safe_error(exc)}",
                })
                continue
            if text is None:
                documents.append({
                    "id": item["id"], "name": name, "text": "", "sha256_bytes": digest,
                    "skip_reason": "mime_nao_suportado",
                })
                continue
            documents.append({"id": item["id"], "name": name, "text": text, "sha256_bytes": digest})
        resultado = _persist_documents(
            repo_root=root,
            documents=documents,
            gate=gate,
            wo_id=atom["wo_id"],
            year_fallback=year,
        )
        resultado["itens_inventario"] = inventory["items_count"]
        resultado["pastas"] = inventory["folders_traversed"]
    except Exception as exc:
        return finish(2, "BLOQUEADO", "BLOQUEADO", _safe_error(exc), None)

    return finish(0, "PASS", "PASS", None, resultado)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Baixar e atomizar uma pasta Drive sob o Kernel.")
    parser.add_argument("--folder-id", required=True)
    parser.add_argument("--source", required=True)
    args = parser.parse_args(argv)
    try:
        return run_drive_job(folder_id=args.folder_id, source=args.source)
    except ValueError as exc:
        print(_safe_error(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
