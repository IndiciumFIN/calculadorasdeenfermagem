"""Baixa uma pasta do Drive e atomiza só o que uma política do Kernel aceita.

Toda atividade (`obter`, `atomizar`) grava uma WO submetida por este módulo
antes de tocar em bytes ou em átomos. Sem credencial, sem política única ou
sem validador executável, o ciclo fecha com exit 2.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from kernel.core import Kernel
from kernel.policy_registry import get_policy, list_policies
from kernel.wo import WorkOrderError, require_wo, submit_wo, update_wo
from packages.cli.drive_recursive_inventory import (
    CredentialError,
    crawl,
    list_page,
    load_token,
)
from packages.cli.utils import aplicar_mascara, calcular_hash
from packages.schemas.invariantes import AtomoBlindado
from pydantic import ValidationError
from validators.sha256_validator import UrlValidator

MAX_FILE_BYTES = 50_000_000
MAX_TEXT_CHARS = 1_000_000
PACKAGE_REPO = Path(__file__).resolve().parents[3]

# Termos específicos primeiro. Mais de um casamento na mesma rota é ambíguo.
_CLASSIFIERS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("KERNEL-POLICY-006", (r"\bmedicamentos?\b", r"\bbulario\b")),
    ("KERNEL-POLICY-009", (r"\bdispositivos?\b",)),
    ("KERNEL-POLICY-014", (r"\besavi\b", r"\beavi\b")),
    ("KERNEL-POLICY-004", (r"\bcid-?11\b", r"\bicd-?11\b")),
    ("KERNEL-POLICY-003", (r"\bcid-?10\b",)),
    ("KERNEL-POLICY-005", (r"\bmesh\b",)),
    ("KERNEL-POLICY-007", (r"\bcvx\b", r"\bvacinas? cdc\b")),
    ("KERNEL-POLICY-008", (r"\bfhir\b", r"\bloinc\b", r"\bsinais? vitais?\b")),
    ("KERNEL-POLICY-010", (r"\btaco\b", r"\bnutricional\b")),
    ("KERNEL-POLICY-011", (r"\bsinan\b",)),
    ("KERNEL-POLICY-012", (r"\bpni\b",)),
    ("KERNEL-POLICY-013", (r"\bcatmat\b",)),
    ("KERNEL-POLICY-015", (r"\bmedline\s*plus\b", r"\bmedlineplus\b")),
    ("KERNEL-POLICY-016", (r"\bsies\b",)),
    ("KERNEL-POLICY-017", (r"\bbodyparts(?:3d)?\b", r"\batlas\b")),
    ("KERNEL-POLICY-018", (r"\bcdsi\b",)),
    ("KERNEL-POLICY-001", (r"\bcofen\b",)),
    ("KERNEL-POLICY-002", (r"\banvisa\b", r"\brdc\b")),
    ("KERNEL-POLICY-019", (r"\bportarias?\b",)),
    ("KERNEL-POLICY-020", (r"\blei federal\b", r"\bplanalto\b")),
)

_OPINION = (
    "infelizmente",
    "importante destacar",
    "recomenda-se",
    "sugerimos",
    "a nosso ver",
    "consideramos que",
    "acreditamos que",
    "no nosso entendimento",
)

_TEXT_MIME_PREFIXES = ("text/",)
_TEXT_MIME_EXACT = frozenset({"application/json", "application/xml"})
_GOOGLE_EXPORT = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}


def _fold(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch)).lower()


def classify_path(path: str) -> list[str]:
    """Retorna as políticas cujo termo aparece no caminho. Vazio = sem política."""
    folded = _fold(path.replace("_", " ").replace("-", " "))
    # hífen já virou espaço; recompõe códigos cid 10 / cid 11 para o padrão cid-?
    folded = folded.replace("cid 10", "cid10").replace("cid 11", "cid11")
    folded = folded.replace("icd 11", "icd11")
    matched: list[str] = []
    known = {policy.id for policy in list_policies()}
    for policy_id, patterns in _CLASSIFIERS:
        if policy_id not in known:
            continue
        if any(re.search(pattern, folded) for pattern in patterns):
            matched.append(policy_id)
    return matched


def canonical_atom_id(legacy_id: str, year: int) -> str:
    digest = hashlib.sha256(legacy_id.encode("utf-8")).hexdigest()
    number = int(digest[:12], 16)
    return f"NORM-{year}-{number}"


def _year_for(path: str, modified: str | None, today_year: int) -> int:
    found = re.search(r"(?:19|20)\d{2}", path)
    if found:
        return int(found.group(0))
    if modified and len(modified) >= 4 and modified[:4].isdigit():
        year = int(modified[:4])
        if 1900 <= year <= 2099:
            return year
    return today_year


def _validator_enforces(validator: Any) -> bool:
    suite = validator.test_suite()
    if len(suite) < 10:
        return False
    for item, expected, _description in suite:
        try:
            actual, _error = validator.validate(item)
        except Exception:
            return False
        if actual != expected:
            return False
    return True


def policy_is_executable(policy_id: str) -> tuple[bool, str | None]:
    kernel = Kernel()
    policy = get_policy(policy_id)
    missing = [name for name in policy.validators if name not in kernel_validators(kernel)]
    if missing:
        return False, f"validadores ausentes: {missing}"
    for name in policy.validators:
        if not _validator_enforces(kernel_validators(kernel)[name]):
            return False, f"validador {name} não reproduz a própria suíte"
    return True, None


def kernel_validators(kernel: Kernel) -> dict[str, Any]:
    from kernel.core import VALIDATORS

    return VALIDATORS


def _paragraphs(text: str) -> list[str]:
    chunks = re.split(r"\n\s*\n", text)
    paragraphs: list[str] = []
    for chunk in chunks:
        line = " ".join(chunk.split())
        if line:
            paragraphs.append(line)
    return paragraphs


def _opinion_motivo(text: str) -> str | None:
    lowered = text.lower()
    for term in _OPINION:
        if term in lowered:
            return "termo_opinativo"
    return None


def _link_fonte(text: str) -> str | None:
    validator = UrlValidator()
    for match in re.finditer(r"https://[^\s<>\"]+", text):
        candidate = match.group(0).rstrip(".,;)")
        ok, _error = validator.validate({"link_fonte": candidate})
        if ok:
            return candidate
    return None


def _quarantine_record(
    *,
    text: str,
    motivo: str,
    source: str,
    policy_id: str | None,
    wo_id: str,
) -> dict[str, Any]:
    masked = aplicar_mascara(text) if text else ""
    preserved = len(masked) <= MAX_TEXT_CHARS
    return {
        "texto_regra_inteiro": masked if preserved else None,
        "preservado": preserved,
        "motivo": motivo if preserved else "excede_limite_repositorio",
        "motivo_original": motivo,
        "fonte": source,
        "policy_id": policy_id,
        "wo_id": wo_id,
        "sha256_original": calcular_hash(text) if text else None,
        "sha256_transformado": calcular_hash(masked) if masked else None,
        "tamanho_chars": len(text),
    }


def _append_quarantine(repo_root: Path, policy_id: str | None, record: dict[str, Any]) -> None:
    if policy_id:
        policy = get_policy(policy_id)
        if not policy.cuarentena_output:
            raise WorkOrderError(f"política {policy_id} sem quarentena_output")
        directory = repo_root / policy.cuarentena_output
    else:
        directory = repo_root / "data" / "quarentena" / "sem_politica"
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / "quarentena.jsonl"
    line = json.dumps(record, ensure_ascii=False)
    if target.exists():
        existing_lines = target.read_text(encoding="utf-8").splitlines()
        if line in existing_lines:
            return
    with target.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def _atomize_text(
    *,
    text: str,
    repo_root: Path,
    policy_id: str,
    wo_id: str,
    file_id: str,
    path: str,
    modified: str | None,
    year: int,
) -> dict[str, int]:
    policy = get_policy(policy_id)
    counts = {"canonical": 0, "quarentena": 0, "dedup": 0}
    fonte_slug = _fonte_slug(policy.source_contract)
    kernel = Kernel()
    output_dir = repo_root / policy.atoms_output
    output_dir.mkdir(parents=True, exist_ok=True)
    source = f"drive:{file_id}:{path}"

    for paragraph in _paragraphs(text):
        masked = aplicar_mascara(paragraph)
        if len(masked) < 10:
            motivo = "texto_curto"
        elif len(masked) > 800:
            motivo = "acima_contrato"
        else:
            motivo = _opinion_motivo(masked)
        if motivo:
            _append_quarantine(
                repo_root,
                policy_id,
                _quarantine_record(
                    text=paragraph,
                    motivo=motivo,
                    source=source,
                    policy_id=policy_id,
                    wo_id=wo_id,
                ),
            )
            counts["quarentena"] += 1
            continue

        digest = calcular_hash(masked)
        legacy_id = f"{file_id}:{digest}"
        atom_id = canonical_atom_id(legacy_id, _year_for(path, modified, year))
        payload: dict[str, Any] = {
            "id_atomo": atom_id,
            "versao_contrato": "1.2.0",
            "fonte_slug": fonte_slug,
            "norma_origem": f"DRIVE_{file_id}",
            "dispositivo_legal": None,
            "link_fonte": _link_fonte(masked),
            "texto_regra": masked,
            "idioma": "pt-BR",
            "sha256_texto": digest,
            "sha256_original": calcular_hash(paragraph),
            "hash_status": "CONFERIDO",
            "vigencia": "NAO_VERIFICADO",
            "wo_id": wo_id,
        }
        payload = {key: value for key, value in payload.items() if value is not None}
        try:
            atom = AtomoBlindado(**payload)
        except ValidationError:
            _append_quarantine(
                repo_root,
                policy_id,
                _quarantine_record(
                    text=paragraph,
                    motivo="kernel_rejeitou",
                    source=source,
                    policy_id=policy_id,
                    wo_id=wo_id,
                ),
            )
            counts["quarentena"] += 1
            continue

        stored = atom.model_dump(mode="json", exclude_none=True)
        decision = kernel.evaluate(stored, policy_id)
        if decision.has_failures():
            _append_quarantine(
                repo_root,
                policy_id,
                _quarantine_record(
                    text=paragraph,
                    motivo="kernel_rejeitou",
                    source=source,
                    policy_id=policy_id,
                    wo_id=wo_id,
                ),
            )
            counts["quarentena"] += 1
            continue

        destination = output_dir / f"{atom_id}.json"
        if destination.exists():
            previous = json.loads(destination.read_text(encoding="utf-8"))
            if previous.get("sha256_texto") == digest:
                counts["dedup"] += 1
                continue
            _append_quarantine(
                repo_root,
                policy_id,
                _quarantine_record(
                    text=paragraph,
                    motivo="conflito_duplicata",
                    source=source,
                    policy_id=policy_id,
                    wo_id=wo_id,
                ),
            )
            counts["quarentena"] += 1
            continue
        destination.write_text(
            json.dumps(stored, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        counts["canonical"] += 1
    return counts


def _fonte_slug(source_contract: str) -> str | None:
    path = PACKAGE_REPO / source_contract
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    slug = data.get("fonte_slug")
    return slug if isinstance(slug, str) and slug else None


def download_bytes(file_id: str, token: str, export_mime: str | None = None) -> bytes:
    if export_mime:
        url = "https://www.googleapis.com/drive/v3/files/" + file_id + "/export?" + urlencode(
            {"mimeType": export_mime, "supportsAllDrives": "true"}
        )
    else:
        url = "https://www.googleapis.com/drive/v3/files/" + file_id + "?" + urlencode(
            {"alt": "media", "supportsAllDrives": "true"}
        )
    request = Request(
        url,
        headers={"Authorization": "Bearer " + token, "Accept": "*/*"},
    )
    try:
        with urlopen(request, timeout=60) as response:
            chunks: list[bytes] = []
            total = 0
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                total += len(block)
                if total > MAX_FILE_BYTES:
                    raise WorkOrderError(f"arquivo {file_id} excede {MAX_FILE_BYTES} bytes")
                chunks.append(block)
            return b"".join(chunks)
    except HTTPError as exc:
        raise WorkOrderError(f"HTTP {exc.code} ao obter {file_id}") from exc
    except URLError as exc:
        raise WorkOrderError(f"falha de rede ao obter {file_id}") from exc


def _extract_text(name: str, mime: str, data: bytes) -> tuple[str | None, str | None]:
    if mime == "application/pdf" or name.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
        except ImportError:
            return None, "extracao_indisponivel"
        try:
            reader = PdfReader(io.BytesIO(data))
            pages = [(page.extract_text() or "") for page in reader.pages]
        except Exception:
            return None, "extracao_indisponivel"
        text = "\n\n".join(part for part in pages if part.strip())
        if not text.strip():
            return None, "extracao_vazia"
        return text, None
    if mime in _TEXT_MIME_EXACT or mime.startswith(_TEXT_MIME_PREFIXES) or name.lower().endswith(
        (".txt", ".md", ".csv", ".json")
    ):
        return data.decode("utf-8", errors="replace"), None
    return None, "formato_nao_atomizavel"


def _resolve_token(token: Any) -> str:
    if callable(token):
        token = token()
    if not isinstance(token, str) or not token:
        raise CredentialError("token Drive vazio; fail-closed")
    return token


def run_drive_cycle(
    folder_id: str,
    repo_root: Path,
    *,
    token_loader: Callable[[], Any] | None = None,
    fetch: Callable[..., dict] | None = None,
    download: Callable[..., bytes] | None = None,
    now: datetime | None = None,
) -> int:
    """Executa obter e, quando a política permite, atomizar. Retorna 0 ou 2."""
    clock = now or datetime.now(timezone.utc)
    year = clock.astimezone(timezone.utc).year
    try:
        obter = submit_wo(
            repo_root,
            activity="obter",
            folder_id=folder_id,
            policy_id=None,
            now=clock,
        )
    except WorkOrderError as exc:
        print(f"WO obter recusada: {exc}")
        return 2

    loader = token_loader or load_token
    try:
        token = loader()
    except CredentialError as exc:
        update_wo(
            repo_root,
            obter,
            status="BLOQUEADO",
            motivo=str(exc),
            exit_code=2,
        )
        print(f"WO {obter['wo_id']} BLOQUEADO: {exc}")
        return 2

    try:
        bearer = _resolve_token(token)
    except CredentialError as exc:
        update_wo(repo_root, obter, status="BLOQUEADO", motivo=str(exc), exit_code=2)
        print(f"WO {obter['wo_id']} BLOQUEADO: {exc}")
        return 2

    # A WO tem de estar no disco e válida antes de qualquer listagem ou byte.
    try:
        require_wo(repo_root, obter["wo_id"], activity="obter", folder_id=folder_id)
    except WorkOrderError as exc:
        print(f"WO obter inválida antes do download: {exc}")
        return 2

    fetch_page = fetch or list_page
    try:
        inventory = crawl(
            [{"id": folder_id, "name": folder_id}],
            bearer,
            fetch=fetch_page,
        )
    except ValueError as exc:
        update_wo(repo_root, obter, status="BLOQUEADO", motivo=str(exc), exit_code=2)
        print(f"WO {obter['wo_id']} BLOQUEADO: {exc}")
        return 2

    downloader = download or download_bytes
    manifest_items: list[dict[str, Any]] = []
    grouped: dict[str, list[dict[str, Any]]] = {}
    blocked = False

    for item in inventory["items"]:
        if item["kind"] != "file":
            continue
        policies = classify_path(item["path"])
        record: dict[str, Any] = {
            "id": item["id"],
            "path": item["path"],
            "mime_type": item["mime_type"],
            "size_bytes": item["size_bytes"],
            "policies": policies,
        }
        if item["size_bytes"] is not None and item["size_bytes"] > MAX_FILE_BYTES:
            record["status"] = "BLOQUEADO"
            record["motivo"] = "acima_50mb"
            manifest_items.append(record)
            blocked = True
            continue
        export_mime = _GOOGLE_EXPORT.get(item["mime_type"])
        is_zip = item["path"].lower().endswith(".zip") or item["mime_type"] in {
            "application/zip",
            "application/x-zip-compressed",
        }
        try:
            data = downloader(item["id"], bearer, export_mime)
        except WorkOrderError as exc:
            record["status"] = "BLOQUEADO"
            record["motivo"] = str(exc)
            manifest_items.append(record)
            blocked = True
            continue
        if len(data) > MAX_FILE_BYTES:
            record["status"] = "BLOQUEADO"
            record["motivo"] = "acima_50mb"
            manifest_items.append(record)
            blocked = True
            continue
        record["sha256"] = hashlib.sha256(data).hexdigest()
        if is_zip:
            record["status"] = "NAO_ATOMIZADO"
            record["motivo"] = "zip_nao_inspecionado"
            manifest_items.append(record)
            continue
        if len(policies) != 1:
            record["status"] = "SEM_POLITICA" if not policies else "AMBIGUO"
            record["motivo"] = (
                "nenhuma política do Kernel casa com o caminho"
                if not policies
                else "mais de uma política casa com o caminho"
            )
            manifest_items.append(record)
            continue
        record["status"] = "OBTIDO"
        manifest_items.append(record)
        grouped.setdefault(policies[0], []).append({**item, "data": data, "export_mime": export_mime})

    manifest = {
        "schema": "CE-DRIVE-OBTER-MANIFEST-1.0.0",
        "wo_id": obter["wo_id"],
        "folder_id": folder_id,
        "items": [{k: v for k, v in row.items() if k != "data"} for row in manifest_items],
    }
    manifest_path = repo_root / "data" / "kernel" / "drive" / folder_id / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if blocked or not manifest_items:
        motivo = "pasta sem arquivos" if not manifest_items else "obter incompleto"
        update_wo(repo_root, obter, status="BLOQUEADO", motivo=motivo, exit_code=2, manifest=str(manifest_path))
        print(f"WO {obter['wo_id']} BLOQUEADO: {motivo}")
        return 2

    update_wo(repo_root, obter, status="PASS", motivo=None, exit_code=0, manifest=str(manifest_path))

    if not grouped:
        atom_wo = submit_wo(
            repo_root,
            activity="atomizar",
            folder_id=folder_id,
            policy_id=None,
            now=clock,
            status="BLOQUEADO",
            motivo="nenhum arquivo classificado sob uma única política executável",
        )
        update_wo(
            repo_root,
            atom_wo,
            status="BLOQUEADO",
            motivo="nenhum arquivo classificado sob uma única política executável",
            exit_code=2,
        )
        print(f"WO {atom_wo['wo_id']} BLOQUEADO: sem política única")
        return 2

    exit_code = 0
    for policy_id, files in sorted(grouped.items()):
        atom_wo = submit_wo(
            repo_root,
            activity="atomizar",
            folder_id=folder_id,
            policy_id=policy_id,
            now=clock,
        )
        try:
            require_wo(
                repo_root,
                atom_wo["wo_id"],
                activity="atomizar",
                folder_id=folder_id,
                policy_id=policy_id,
            )
        except WorkOrderError as exc:
            print(f"WO atomizar inválida: {exc}")
            return 2
        executable, reason = policy_is_executable(policy_id)
        if not executable:
            for item in files:
                _append_quarantine(
                    repo_root,
                    policy_id,
                    _quarantine_record(
                        text="",
                        motivo="validador_nao_conforme",
                        source=f"drive:{item['id']}:{item['path']}:{reason}",
                        policy_id=policy_id,
                        wo_id=atom_wo["wo_id"],
                    ),
                )
            update_wo(
                repo_root,
                atom_wo,
                status="BLOQUEADO",
                motivo=reason,
                exit_code=2,
            )
            print(f"WO {atom_wo['wo_id']} BLOQUEADO: {reason}")
            exit_code = 2
            continue

        totals = {"canonical": 0, "quarentena": 0, "dedup": 0}
        for item in files:
            text, extract_motivo = _extract_text(item["path"], item["export_mime"] or item["mime_type"], item["data"])
            if extract_motivo or text is None:
                _append_quarantine(
                    repo_root,
                    policy_id,
                    _quarantine_record(
                        text="",
                        motivo=extract_motivo or "extracao_indisponivel",
                        source=f"drive:{item['id']}:{item['path']}",
                        policy_id=policy_id,
                        wo_id=atom_wo["wo_id"],
                    ),
                )
                totals["quarentena"] += 1
                continue
            if len(text) > MAX_TEXT_CHARS:
                _append_quarantine(
                    repo_root,
                    policy_id,
                    _quarantine_record(
                        text=text[:0],
                        motivo="excede_limite_repositorio",
                        source=f"drive:{item['id']}:{item['path']}",
                        policy_id=policy_id,
                        wo_id=atom_wo["wo_id"],
                    ),
                )
                totals["quarentena"] += 1
                continue
            part = _atomize_text(
                text=text,
                repo_root=repo_root,
                policy_id=policy_id,
                wo_id=atom_wo["wo_id"],
                file_id=item["id"],
                path=item["path"],
                modified=item.get("modified_time"),
                year=year,
            )
            for key, value in part.items():
                totals[key] += value
        status = "PASS" if totals["canonical"] or totals["dedup"] else "BLOQUEADO"
        if status != "PASS":
            exit_code = 2
        update_wo(
            repo_root,
            atom_wo,
            status=status,
            motivo=None if status == "PASS" else "nenhum átomo passou na política",
            exit_code=0 if status == "PASS" else 2,
            counts=totals,
        )
        print(f"WO {atom_wo['wo_id']} {status}: {totals}")

    return exit_code
