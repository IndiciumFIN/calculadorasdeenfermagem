"""WO submetida pelo Kernel antes de obter ou atomizar.

O Kernel não escolhe política nova e não marca PREAUTHORIZED.
Sem credencial, sem sha256_fonte ou sem política válida única, a WO fica BLOQUEADO.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from packages.cli.drive_recursive_inventory import (
    FOLDER,
    CredentialError,
    crawl,
    load_token,
)
from packages.cli.kernel.core import REPO_ROOT, Decision, Kernel
from packages.cli.kernel.policy_registry import POLICIES_DIR, list_policies
from packages.cli.utils import aplicar_mascara
from packages.schemas.invariantes import AtomoBlindado

TAREFAS = ("obter", "atomizar")
MAX_BYTES = 50 * 1024 * 1024
LEGAL_MARKERS = ("art.", "artigo", "§", "inciso", "parágrafo", "paragrafo")
FOLDER_IN_URL = re.compile(r"/folders/([A-Za-z0-9_-]+)")
FOLDER_ID = re.compile(r"^[A-Za-z0-9_-]{10,}$")
EXPORTS = {
    "application/vnd.google-apps.document": "text/plain",
    "application/vnd.google-apps.spreadsheet": "text/csv",
    "application/vnd.google-apps.presentation": "text/plain",
}
VOLATILE = {"timestamp", "data"}


def parse_folder_id(value: str) -> str:
    raw = value.strip()
    found = FOLDER_IN_URL.search(raw)
    folder_id = found.group(1) if found else raw
    if not FOLDER_ID.fullmatch(folder_id):
        raise ValueError(f"ID de pasta Drive inválido: {value}")
    return folder_id


def canonical_id(legacy_id: str, ano: int) -> str:
    prefix = hashlib.sha256(legacy_id.encode("utf-8")).hexdigest()[:12]
    return f"NORM-{ano}-{int(prefix, 16)}"


def assemble_wo(
    *,
    folder_id: str,
    tarefa: str,
    estado: str,
    motivo: str | None,
    sha256_fonte: str | None,
    politicas_validas: list[str],
    politicas_rejeitadas: list[dict[str, str]],
    ultimo_http_code: int | None,
    entradas: int,
    ano_id: int,
    evidence_reference: str,
    acao_necessaria: str,
) -> dict[str, Any]:
    if tarefa not in TAREFAS:
        raise ValueError(f"Tarefa não permitida: {tarefa}")
    if estado == "PREAUTHORIZED":
        raise ValueError("Kernel não atribui PREAUTHORIZED; isso exige revisor humano.")
    if estado == "BLOQUEADO" and not motivo:
        raise ValueError("WO BLOQUEADO exige motivo.")
    if estado not in {"BLOQUEADO", "EXECUTADO"}:
        raise ValueError(f"Estado não emitido pelo Kernel: {estado}")
    now = datetime.now(timezone.utc).isoformat()
    wo_id = f"CE-WO-DRIVE-{folder_id}-{tarefa}"
    return {
        "schema": "CE-WO-AUTHORIZATION-1.0.0",
        "id": f"WO-DRIVE-{folder_id}-{tarefa}",
        "wo_id": wo_id,
        "slug": f"drive_{folder_id}_{tarefa}",
        "tarefa": tarefa,
        "lote": f"drive:{folder_id}",
        "folder_id": folder_id,
        "folder_url": f"https://drive.google.com/drive/folders/{folder_id}",
        "entradas": entradas,
        "estado": estado,
        "status": estado,
        "motivo": motivo,
        "sha256_fonte": sha256_fonte,
        "tentativas": 1,
        "ultimo_http_code": ultimo_http_code,
        "acao_necessaria": acao_necessaria,
        "authorized_by": "kernel",
        "autorizado_por": "kernel",
        "ano_id": ano_id,
        "politicas_validas": politicas_validas,
        "politicas_rejeitadas": politicas_rejeitadas,
        "timestamp": now,
        "data": now,
        "conditions": [
            "WO submetida pelo Kernel antes de baixar ou atomizar",
            "Sem credencial o download não ocorre (fail-closed)",
            "Sem sha256_fonte a atomização não ocorre",
            "Átomo canônico só com exatamente uma política válida",
            "Vigência inicial NAO_VERIFICADO",
        ],
        "evidence_reference": evidence_reference,
    }


def wo_path(root: Path, folder_id: str, tarefa: str) -> Path:
    return root / "data" / "legado" / f"autorizacao_WO-DRIVE-{folder_id}-{tarefa}.json"


def _stable(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key not in VOLATILE}


def write_wo(path: Path, payload: dict[str, Any]) -> bool:
    """Grava a WO. Devolve True quando o arquivo mudou."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            current = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"WO existente ilegível: {path}") from exc
        payload["ano_id"] = current.get("ano_id", payload["ano_id"])
        if _stable(current) == _stable(payload):
            return False
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    path.write_text(text, encoding="utf-8")
    return True


def probe_drive_api(folder_id: str) -> tuple[int | None, str]:
    params = urlencode(
        {
            "q": f"'{folder_id}' in parents and trashed = false",
            "fields": "files(id)",
            "pageSize": "1",
            "supportsAllDrives": "true",
        }
    )
    request = Request(
        "https://www.googleapis.com/drive/v3/files?" + params,
        headers={"Accept": "application/json", "User-Agent": "CE-Kernel/1.0"},
    )
    try:
        with urlopen(request, timeout=20) as response:
            body = response.read(300).decode("utf-8", "replace")
            return response.status, body
    except HTTPError as exc:
        body = exc.read(300).decode("utf-8", "replace")
        return exc.code, body
    except URLError as exc:
        return None, f"URLError: {exc.reason}"


def audit_policies(kernel: Kernel) -> tuple[list[str], list[dict[str, str]]]:
    valid: list[str] = []
    rejected: list[dict[str, str]] = []
    for policy in list_policies():
        code, message = kernel.check_policy(policy.id)
        if code == 0:
            valid.append(policy.id)
        else:
            rejected.append({"id": policy.id, "motivo": message})
    return valid, rejected


def select_policy(
    item: dict[str, Any],
    policy_ids: list[str],
    evaluate,
) -> str | None:
    matched = [policy_id for policy_id in policy_ids if evaluate(item, policy_id)]
    if len(matched) == 1:
        return matched[0]
    return None


def _policy_documents() -> dict[str, dict[str, Any]]:
    documents = {}
    for path in sorted(POLICIES_DIR.glob("KERNEL-POLICY-*.json")):
        documents[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return documents


def _fonte_slug(policy: dict[str, Any], root: Path) -> str | None:
    link = policy.get("source_contract")
    if not isinstance(link, str):
        return None
    path = root / link
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    slug = data.get("fonte_slug")
    return slug if isinstance(slug, str) else None


def _append_quarantine(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    key = (record.get("sha256_original"), record.get("motivo"), record.get("fonte"))
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            previous = json.loads(line)
            previous_key = (
                previous.get("sha256_original"),
                previous.get("motivo"),
                previous.get("fonte"),
            )
            if previous_key == key:
                return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _quarantine(
    root: Path,
    record: dict[str, Any],
    policy_id: str | None,
    documents: dict[str, dict[str, Any]],
) -> None:
    output = None
    if policy_id and isinstance(documents.get(policy_id, {}).get("quarentena_output"), str):
        output = root / documents[policy_id]["quarentena_output"]
    else:
        output = root / "data" / "quarentena" / "sem_politica_unica"
    _append_quarantine(output / "rejeicoes.jsonl", record)


def atomize_texts(
    root: Path,
    records: list[dict[str, Any]],
    *,
    wo_id: str,
    ano: int,
    policy_ids: list[str],
    kernel: Kernel,
) -> dict[str, int]:
    """Atomiza texto já obtido. Não promove quando mais de uma política aceita."""
    documents = _policy_documents()
    counts = {"canonical": 0, "quarentena": 0}

    def accept(item: dict[str, Any], policy_id: str) -> bool:
        decision = kernel.evaluate(item, policy_id)
        return decision.decision == Decision.APPROVED

    for record in records:
        fonte = record["fonte"]
        original_text = record.get("texto")
        if original_text is None:
            _quarantine(
                root,
                {
                    "texto_regra_inteiro": None,
                    "motivo": "nao_texto",
                    "fonte": fonte,
                    "sha256_original": record["sha256"],
                    "sha256_transformado": None,
                },
                None,
                documents,
            )
            counts["quarentena"] += 1
            continue

        lines = [line.strip() for line in original_text.splitlines() if line.strip()]
        candidates = [
            line for line in lines if any(marker in line.lower() for marker in LEGAL_MARKERS)
        ]
        if not candidates:
            _quarantine(
                root,
                {
                    "texto_regra_inteiro": original_text,
                    "motivo": "sem_dispositivo_legal",
                    "fonte": fonte,
                    "sha256_original": record["sha256"],
                    "sha256_transformado": hashlib.sha256(
                        aplicar_mascara(original_text).encode("utf-8")
                    ).hexdigest(),
                },
                None,
                documents,
            )
            counts["quarentena"] += 1
            continue

        for index, line in enumerate(candidates, start=1):
            transformed = aplicar_mascara(line)
            legacy_id = f"DRIVE-{record['file_id']}-SEG-{index:04d}"
            item = {
                "id_atomo": canonical_id(legacy_id, ano),
                "versao_contrato": "1.2.0",
                "texto_regra": transformed,
                "idioma": "pt-BR",
                "sha256_texto": hashlib.sha256(transformed.encode("utf-8")).hexdigest(),
                "sha256_original": hashlib.sha256(line.encode("utf-8")).hexdigest(),
                "hash_status": "PENDENTE",
                "vigencia": "NAO_VERIFICADO",
                "wo_id": wo_id,
            }
            base_record = {
                "texto_regra_inteiro": line,
                "fonte": fonte,
                "sha256_original": item["sha256_original"],
                "sha256_transformado": item["sha256_texto"],
            }
            if len(transformed) < 10 or len(transformed) > 800:
                base_record["motivo"] = (
                    "texto_curto" if len(transformed) < 10 else "acima_contrato"
                )
                _quarantine(root, base_record, None, documents)
                counts["quarentena"] += 1
                continue
            try:
                AtomoBlindado.model_validate(item)
            except Exception as exc:
                base_record["motivo"] = f"schema:{exc.__class__.__name__}"
                _quarantine(root, base_record, None, documents)
                counts["quarentena"] += 1
                continue
            chosen = select_policy(item, policy_ids, accept)
            if chosen is None:
                base_record["motivo"] = "politica_ambigua_ou_rejeitada"
                _quarantine(root, base_record, None, documents)
                counts["quarentena"] += 1
                continue
            slug = _fonte_slug(documents[chosen], REPO_ROOT)
            if slug:
                item["fonte_slug"] = slug
            output = root / documents[chosen]["atoms_output"] / f"{item['id_atomo']}.json"
            output.parent.mkdir(parents=True, exist_ok=True)
            encoded = json.dumps(item, ensure_ascii=False, indent=2) + "\n"
            if output.exists() and output.read_text(encoding="utf-8") != encoded:
                base_record["motivo"] = "conflito_duplicata"
                _quarantine(root, base_record, chosen, documents)
                counts["quarentena"] += 1
                continue
            if not output.exists():
                output.write_text(encoded, encoding="utf-8")
            counts["canonical"] += 1
    return counts


def _download(url: str, token: Callable[[], str], dest: Path) -> str:
    request = Request(
        url,
        headers={"Authorization": "Bearer " + token(), "User-Agent": "CE-Kernel/1.0"},
    )
    digest = hashlib.sha256()
    dest.parent.mkdir(parents=True, exist_ok=True)
    temporary = dest.with_suffix(dest.suffix + ".partial")
    written = 0
    try:
        with urlopen(request, timeout=60) as response, temporary.open("wb") as handle:
            while True:
                chunk = response.read(65536)
                if not chunk:
                    break
                written += len(chunk)
                if written > MAX_BYTES:
                    raise ValueError(f"arquivo acima de {MAX_BYTES} bytes")
                digest.update(chunk)
                handle.write(chunk)
        temporary.replace(dest)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return digest.hexdigest()


def _file_url(item: dict[str, Any]) -> str:
    mime = item["mime_type"]
    if mime in EXPORTS:
        return (
            "https://www.googleapis.com/drive/v3/files/"
            f"{item['id']}/export?"
            + urlencode({"mimeType": EXPORTS[mime], "supportsAllDrives": "true"})
        )
    return (
        "https://www.googleapis.com/drive/v3/files/"
        f"{item['id']}?alt=media&supportsAllDrives=true"
    )


def _sha256_fonte(rows: list[tuple[str, str]]) -> str:
    body = "\n".join(f"{file_id} {digest}" for file_id, digest in sorted(rows))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _submit_if_absent(
    root: Path,
    folder_id: str,
    tarefa: str,
    motivo: str,
    valid: list[str],
    rejected: list[dict[str, str]],
    ano: int,
    evidence: str,
    action: str,
) -> None:
    """Grava a WO antes de qualquer chamada ao Drive. Não rebaixa uma WO já submetida."""
    path = wo_path(root, folder_id, tarefa)
    if path.exists():
        return
    write_wo(
        path,
        assemble_wo(
            folder_id=folder_id,
            tarefa=tarefa,
            estado="BLOQUEADO",
            motivo=motivo,
            sha256_fonte=None,
            politicas_validas=valid,
            politicas_rejeitadas=rejected,
            ultimo_http_code=None,
            entradas=0,
            ano_id=ano,
            evidence_reference=evidence,
            acao_necessaria=action,
        ),
    )


def _write_evidence(
    path: Path,
    folder_id: str,
    valid: list[str],
    rejected: list[dict[str, str]],
    http_code: int | None,
    http_body: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "CE-KERNEL-DRIVE-DECISION-1.0.0",
        "folder_id": folder_id,
        "wo_submitted_before_drive": True,
        "wo_obter": f"data/legado/autorizacao_WO-DRIVE-{folder_id}-obter.json",
        "wo_atomizar": f"data/legado/autorizacao_WO-DRIVE-{folder_id}-atomizar.json",
        "politicas_validas": valid,
        "politicas_rejeitadas": rejected,
        "ultimo_http_code": http_code,
        "resposta_api": http_body[:300],
    }
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == encoded:
        return
    path.write_text(encoded, encoding="utf-8")


def run_obtain_drive(
    folder_id: str,
    root: Path | None = None,
    token_loader: Callable[[], Callable[[], str]] | None = None,
    probe: Callable[[str], tuple[int | None, str]] | None = None,
    inventory: Callable[..., dict[str, Any]] | None = None,
) -> int:
    """Submete as duas WO e só depois consulta o Drive. Exit 2 em fail-closed."""
    root = root or REPO_ROOT
    folder_id = parse_folder_id(folder_id)
    kernel = Kernel()
    valid, rejected = audit_policies(kernel)
    evidence = f"evidence/CE-WO-DRIVE-{folder_id}/kernel_decision.json"
    ano = datetime.now(timezone.utc).year
    action = (
        "Configurar GDRIVE_SA_KEY com leitura da pasta e reexecutar "
        "python -m packages.cli.main kernel obtain-drive "
        f"--folder-id {folder_id}"
    )
    loader = token_loader or load_token
    try:
        token = loader()
        credential_error = None
    except CredentialError as exc:
        token = None
        credential_error = str(exc)

    _submit_if_absent(
        root,
        folder_id,
        "obter",
        "WO submetida pelo Kernel antes de consultar o Drive. Download ainda não executado.",
        valid,
        rejected,
        ano,
        evidence,
        action,
    )
    _submit_if_absent(
        root,
        folder_id,
        "atomizar",
        "WO submetida pelo Kernel. Atomização ainda não executada.",
        valid,
        rejected,
        ano,
        evidence,
        action,
    )

    http_code: int | None = None
    http_body = ""
    obter_estado = "BLOQUEADO"
    obter_motivo = None
    sha = None
    entradas = 0
    records: list[dict[str, Any]] = []
    exit_code = 2

    if not valid:
        obter_motivo = (
            "Nenhuma política passou no gate do Kernel. Download não executado. "
            "sha256_fonte ausente."
        )
    elif credential_error:
        http_code, http_body = (probe or probe_drive_api)(folder_id)
        obter_motivo = (
            f"{credential_error} Drive API sem credencial respondeu HTTP {http_code}. "
            "sha256_fonte ausente. Download não executado."
        )
    else:
        try:
            collected = (inventory or crawl)(
                [{"id": folder_id, "name": folder_id}],
                token,
            )
            http_code = 200
            http_body = "inventario autenticado"
            files = [item for item in collected["items"] if item["kind"] == "file"]
            if not files:
                obter_motivo = "Pasta sem arquivos. sha256_fonte ausente."
            else:
                base = (root / "data" / "raw" / "drive" / folder_id).resolve()
                hashes: list[tuple[str, str]] = []
                for item in files:
                    if item["mime_type"] == FOLDER:
                        continue
                    relative = Path(item["path"])
                    dest = (base / relative).resolve()
                    if base not in dest.parents:
                        raise ValueError(f"caminho ambíguo: {item['path']}")
                    digest = _download(_file_url(item), token, dest)
                    hashes.append((item["id"], digest))
                    text = None
                    try:
                        text = dest.read_text(encoding="utf-8")
                    except UnicodeError:
                        text = None
                    records.append(
                        {
                            "file_id": item["id"],
                            "fonte": item["path"],
                            "sha256": digest,
                            "texto": text,
                        }
                    )
                sha = _sha256_fonte(hashes)
                entradas = len(hashes)
                obter_estado = "EXECUTADO"
                obter_motivo = None
        except HTTPError as exc:
            http_code = exc.code
            http_body = exc.read(300).decode("utf-8", "replace")
            obter_motivo = (
                f"Falha ao obter a pasta: HTTPError {http_code}. "
                "sha256_fonte ausente. Download não executado."
            )
            sha = None
            records = []
        except Exception as exc:
            obter_motivo = f"Falha ao obter a pasta: {exc.__class__.__name__}: {exc}"
            sha = None
            records = []

    _write_evidence(root / evidence, folder_id, valid, rejected, http_code, http_body)

    obter = assemble_wo(
        folder_id=folder_id,
        tarefa="obter",
        estado=obter_estado,
        motivo=obter_motivo,
        sha256_fonte=sha,
        politicas_validas=valid,
        politicas_rejeitadas=rejected,
        ultimo_http_code=http_code,
        entradas=entradas,
        ano_id=ano,
        evidence_reference=evidence,
        acao_necessaria=action if obter_estado == "BLOQUEADO" else "Nenhuma.",
    )
    write_wo(wo_path(root, folder_id, "obter"), obter)

    atom_estado = "BLOQUEADO"
    atom_motivo = "sha256_fonte ausente. Atomização não executada."
    atom_entradas = 0
    if sha and records:
        counts = atomize_texts(
            root,
            records,
            wo_id=f"CE-WO-DRIVE-{folder_id}-atomizar",
            ano=obter["ano_id"],
            policy_ids=valid,
            kernel=kernel,
        )
        atom_entradas = counts["canonical"]
        if counts["canonical"] > 0:
            atom_estado = "EXECUTADO"
            atom_motivo = None
            exit_code = 0
        else:
            atom_motivo = (
                "Nenhum átomo canônico. Política válida não isolou os segmentos "
                f"(quarentena={counts['quarentena']})."
            )
    elif sha and not records:
        atom_motivo = "sha256_fonte presente sem registros de texto. Fail-closed."

    atom = assemble_wo(
        folder_id=folder_id,
        tarefa="atomizar",
        estado=atom_estado,
        motivo=atom_motivo,
        sha256_fonte=sha,
        politicas_validas=valid,
        politicas_rejeitadas=rejected,
        ultimo_http_code=http_code,
        entradas=atom_entradas,
        ano_id=obter["ano_id"],
        evidence_reference=evidence,
        acao_necessaria=action if atom_estado == "BLOQUEADO" else "Nenhuma.",
    )
    write_wo(wo_path(root, folder_id, "atomizar"), atom)
    print(
        f"WO obter={obter['estado']} atomizar={atom['estado']} "
        f"politicas_validas={len(valid)} exit={exit_code}"
    )
    return exit_code
