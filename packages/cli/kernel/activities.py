"""Atividades de obter e atomizar uma pasta Drive.

Toda atividade submetida uma WO pelo Kernel antes de produzir efeito.
Sem política cujo gate passe, sem credencial ou sem sha256_fonte, o
registro fica BLOQUEADO e o processo termina com exit 2.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from packages.cli.utils import aplicar_mascara, calcular_hash
from packages.schemas.invariantes import AtomoBlindado

from kernel.core import VALIDATORS, Decision, Kernel, _ensure_validators
from kernel.policy_registry import get_policy, list_policies
from kernel.work_order import load_work_order, submit_work_order, work_order_id

REPO_ROOT = Path(__file__).resolve().parents[3]
FOLDER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{20,80}$")
FILE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,}$")
DEVICE_RE = re.compile(
    r"^(art\.?|artigo|§|inciso|par[aá]grafo)\b",
    re.IGNORECASE,
)
YEAR_RE = re.compile(r"(?:19|20)\d{2}")
SLUG_EDGE = r"(?:^|[^a-z0-9]){slug}(?:[^a-z0-9]|$)"
MAX_BYTES = 50 * 1024 * 1024
TEXT_MIMES = frozenset(
    {
        "text/plain",
        "text/csv",
        "text/markdown",
        "text/xml",
        "text/tab-separated-values",
        "application/json",
        "application/xml",
        "application/csv",
        "text/html",
    }
)
GOOGLE_DOC = "application/vnd.google-apps.document"
GOOGLE_SHEET = "application/vnd.google-apps.spreadsheet"
BLOCKING_STATUS = frozenset(
    {"too_large", "html_interstitial", "decode_error", "download_error"}
)


def _repo_root(root: Path | None) -> Path:
    return (root or REPO_ROOT).resolve()


def _safe_motivo(exc: BaseException) -> str:
    text = str(exc).strip() or exc.__class__.__name__
    if "PRIVATE KEY" in text or "private_key" in text:
        return f"{exc.__class__.__name__}: credencial rejeitada"
    return text[:500]


def valid_policy_ids() -> list[str]:
    """Políticas cujo conjunto de validadores passa no test_suite do Kernel."""
    _ensure_validators()
    approved: list[str] = []
    for policy in list_policies():
        names = list(policy.validators)
        if not names or any(name not in VALIDATORS for name in names):
            continue
        passed = True
        for name in names:
            validator = VALIDATORS[name]
            with redirect_stdout(io.StringIO()):
                if not hasattr(validator, "run_tests") or not validator.run_tests():
                    passed = False
                    break
        if passed:
            approved.append(policy.id)
    return approved


def _fonte_slug(policy_id: str) -> str:
    policy = get_policy(policy_id)
    source = REPO_ROOT / policy.source_contract
    data = json.loads(source.read_text(encoding="utf-8"))
    slug = data.get("fonte_slug")
    if not isinstance(slug, str) or not slug:
        raise ValueError(f"fonte_slug ausente em {policy.source_contract}")
    return slug


def policy_maps() -> tuple[dict[str, str], dict[str, str]]:
    valid_ids = set(valid_policy_ids())
    valid: dict[str, str] = {}
    invalid: dict[str, str] = {}
    seen: dict[str, str] = {}
    for policy in list_policies():
        slug = _fonte_slug(policy.id)
        if slug in seen:
            raise ValueError(f"fonte_slug duplicado: {slug}")
        seen[slug] = policy.id
        target = valid if policy.id in valid_ids else invalid
        target[slug] = policy.id
    return valid, invalid


def _slug_hits(path: str, mapping: dict[str, str]) -> list[str]:
    normalized = path.lower().replace("-", "_")
    hits: list[str] = []
    for slug, policy_id in mapping.items():
        pattern = SLUG_EDGE.format(slug=re.escape(slug.lower()))
        if re.search(pattern, normalized):
            hits.append(policy_id)
    return hits


def classificar_caminho(
    path: str,
    valid_map: dict[str, str],
    invalid_map: dict[str, str],
) -> tuple[str, str | None]:
    valid_hits = _slug_hits(path, valid_map)
    invalid_hits = _slug_hits(path, invalid_map)
    if len(valid_hits) == 1 and not invalid_hits:
        return "ok", valid_hits[0]
    if len(valid_hits) > 1 or (valid_hits and invalid_hits):
        return "politica_ambigua", None
    if invalid_hits:
        return "politica_invalida", None
    return "politica_ausente", None


def split_candidates(text: str) -> list[str]:
    chunks: list[list[str]] = []
    current: list[str] = []
    for line in text.splitlines():
        if DEVICE_RE.match(line.strip()) and any(part.strip() for part in current):
            chunks.append(current)
            current = [line]
        else:
            current.append(line)
    if any(part.strip() for part in current):
        chunks.append(current)
    return ["\n".join(chunk).strip() for chunk in chunks if "\n".join(chunk).strip()]


def atom_id(legacy_id: str, year: str) -> str:
    digest = hashlib.sha256(legacy_id.encode("utf-8")).hexdigest()[:12]
    return f"NORM-{year}-{int(digest, 16)}"


def fonte_sha256(items: list[dict[str, Any]]) -> str:
    projection = [
        {
            "id": item["id"],
            "path": item["path"],
            "sha256": item["sha256"],
            "status": item["status"],
        }
        for item in sorted(items, key=lambda row: (row["path"], row["id"]))
    ]
    blob = json.dumps(projection, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _credential_error_type() -> type[BaseException]:
    from packages.cli.drive_recursive_inventory import CredentialError

    return CredentialError


def _default_token() -> Callable[[], str]:
    from packages.cli.drive_recursive_inventory import load_token

    return load_token()


def _default_crawl(roots: list[dict[str, str]], token: Any) -> dict[str, Any]:
    from packages.cli.drive_recursive_inventory import crawl

    return crawl(roots, token)


def _default_download(file_id: str, mime: str, token: Any) -> bytes:
    from packages.cli.drive_recursive_inventory import _resolve

    if not FILE_ID_RE.fullmatch(file_id):
        raise ValueError("id de arquivo Drive inválido")
    getter = _resolve(token)
    if mime == GOOGLE_DOC:
        query = urlencode({"mimeType": "text/plain", "supportsAllDrives": "true"})
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}/export?{query}"
    elif mime == GOOGLE_SHEET:
        query = urlencode({"mimeType": "text/csv", "supportsAllDrives": "true"})
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}/export?{query}"
    else:
        query = urlencode({"alt": "media", "supportsAllDrives": "true"})
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}?{query}"
    request = Request(
        url,
        headers={"Authorization": "Bearer " + getter(), "Accept": "*/*"},
    )
    with urlopen(request, timeout=60) as response:
        return response.read(MAX_BYTES + 1)


def _looks_like_html(data: bytes) -> bool:
    head = data[:1500].lstrip().lower()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html")


def _interpret(mime: str, data: bytes) -> tuple[str, str | None]:
    if len(data) > MAX_BYTES:
        return "too_large", None
    if _looks_like_html(data) and mime != "text/html":
        return "html_interstitial", None
    textual = mime in TEXT_MIMES or mime in {GOOGLE_DOC, GOOGLE_SHEET}
    if not textual:
        return "parser_ausente", None
    try:
        decoded = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return "decode_error", None
    if mime == "text/html":
        if "accounts.google.com" in decoded or "ServiceLogin" in decoded:
            return "html_interstitial", None
        from bs4 import BeautifulSoup

        decoded = BeautifulSoup(decoded, "html.parser").get_text(separator="\n", strip=True)
    return "acquired_text", aplicar_mascara(decoded)


def _drive_dir(root: Path, folder_id: str) -> Path:
    path = (root / "data" / "raw" / "drive" / folder_id).resolve()
    base = (root / "data" / "raw" / "drive").resolve()
    if base not in path.parents:
        raise ValueError("destino de download inválido")
    return path


def _submit(kernel: Kernel, **kwargs: Any) -> dict[str, Any]:
    return kernel.submit_wo(**kwargs)


def _block_obter(
    kernel: Kernel,
    *,
    root: Path,
    folder_id: str,
    motivo: str,
    politicas: list[str],
    acao: str | None = None,
    clock: Callable[[], str] | None = None,
) -> int:
    _submit(
        kernel,
        root=root,
        tarefa="obter",
        folder_id=folder_id,
        estado="BLOQUEADO",
        motivo=motivo,
        politicas_validas=politicas,
        acao_necessaria=acao,
        clock=clock,
    )
    print(f"WO obter BLOQUEADO: {motivo}")
    return 2


def executar_obter(
    folder_id: str,
    *,
    root: Path | None = None,
    token_loader: Callable[[], Any] | None = None,
    crawl_fn: Callable[..., dict[str, Any]] | None = None,
    download_fn: Callable[[str, str, Any], bytes] | None = None,
    clock: Callable[[], str] | None = None,
) -> int:
    if not FOLDER_ID_RE.fullmatch(folder_id):
        print("ID de pasta inválido. Fail-closed.")
        return 2
    root = _repo_root(root)
    kernel = Kernel()
    politicas: list[str] = []
    _submit(
        kernel,
        root=root,
        tarefa="obter",
        folder_id=folder_id,
        estado="SUBMITTED",
        motivo="coleta iniciada",
        clock=clock,
    )
    try:
        politicas = valid_policy_ids()
    except Exception as exc:
        return _block_obter(
            kernel,
            root=root,
            folder_id=folder_id,
            motivo=_safe_motivo(exc),
            politicas=[],
            clock=clock,
        )
    if not politicas:
        return _block_obter(
            kernel,
            root=root,
            folder_id=folder_id,
            motivo="Nenhuma política passou no gate do kernel.",
            politicas=[],
            clock=clock,
        )

    loader = token_loader or _default_token
    try:
        token = loader()
    except _credential_error_type() as exc:
        return _block_obter(
            kernel,
            root=root,
            folder_id=folder_id,
            motivo=str(exc),
            politicas=politicas,
            acao="Configurar GDRIVE_SA_KEY ou DRIVE_ACCESS_TOKEN com leitura da pasta.",
            clock=clock,
        )
    except Exception as exc:
        return _block_obter(
            kernel,
            root=root,
            folder_id=folder_id,
            motivo=_safe_motivo(exc),
            politicas=politicas,
            clock=clock,
        )

    try:
        inventory = (crawl_fn or _default_crawl)([{"id": folder_id}], token)
        records = _collect_files(
            inventory,
            token,
            download_fn or _default_download,
        )
    except Exception as exc:
        return _block_obter(
            kernel,
            root=root,
            folder_id=folder_id,
            motivo=_safe_motivo(exc),
            politicas=politicas,
            clock=clock,
        )

    files = [row for row in records if row["kind"] == "file"]
    if not files:
        return _block_obter(
            kernel,
            root=root,
            folder_id=folder_id,
            motivo="Pasta sem arquivos; inventário vazio.",
            politicas=politicas,
            clock=clock,
        )

    texts = {row["id"]: row.pop("_text") for row in files if "_text" in row}
    blocked = [row for row in files if row["status"] in BLOCKING_STATUS]
    destination = _drive_dir(root, folder_id)
    manifest = {
        "schema": "CE-DRIVE-OBTER-1.0.0",
        "pasta_drive_id": folder_id,
        "wo_id": work_order_id("obter", folder_id),
        "sha256_fonte": fonte_sha256(files),
        "items": files,
    }
    if blocked:
        summary = "; ".join(f"{row['id']}={row['status']}" for row in blocked[:20])
        _write_manifest(destination, manifest)
        return _block_obter(
            kernel,
            root=root,
            folder_id=folder_id,
            motivo=f"Coleta incompleta: {summary}",
            politicas=politicas,
            clock=clock,
        )

    text_dir = destination / "text"
    if text_dir.exists():
        shutil.rmtree(text_dir)
    text_dir.mkdir(parents=True)
    for row in files:
        if row["status"] != "acquired_text":
            continue
        (text_dir / f"{row['id']}.txt").write_text(texts[row["id"]], encoding="utf-8")
        row["text_relpath"] = f"text/{row['id']}.txt"
    manifest["sha256_fonte"] = fonte_sha256(files)
    _write_manifest(destination, manifest)
    _submit(
        kernel,
        root=root,
        tarefa="obter",
        folder_id=folder_id,
        estado="EXECUTADO",
        motivo=f"{len(files)} arquivo(s) com sha256.",
        sha256_fonte=manifest["sha256_fonte"],
        politicas_validas=politicas,
        contagens={"arquivos": len(files)},
        clock=clock,
    )
    print(f"WO obter EXECUTADO sha256_fonte={manifest['sha256_fonte']}")
    return 0


def _collect_files(
    inventory: dict[str, Any],
    token: Any,
    download_fn: Callable[[str, str, Any], bytes],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in inventory.get("items") or []:
        if item.get("kind") == "folder":
            continue
        file_id = item.get("id")
        path = item.get("path")
        mime = item.get("mime_type")
        if not isinstance(file_id, str) or not FILE_ID_RE.fullmatch(file_id):
            raise ValueError("id de arquivo Drive inválido")
        if not isinstance(path, str) or not path or ".." in Path(path).parts:
            raise ValueError("caminho Drive inválido")
        if not isinstance(mime, str) or not mime:
            raise ValueError("mime ausente")
        size = item.get("size_bytes")
        if isinstance(size, int) and size > MAX_BYTES:
            rows.append(_file_row(file_id, path, mime, "too_large", None, size))
            continue
        try:
            payload = download_fn(file_id, mime, token)
        except Exception as exc:
            rows.append(
                _file_row(file_id, path, mime, "download_error", None, None, _safe_motivo(exc))
            )
            continue
        status, text = _interpret(mime, payload)
        digest = (
            calcular_hash(text)
            if text is not None
            else hashlib.sha256(payload).hexdigest()
        )
        row = _file_row(file_id, path, mime, status, digest, len(payload))
        if text is not None:
            row["_text"] = text
        rows.append(row)
    return rows


def _file_row(
    file_id: str,
    path: str,
    mime: str,
    status: str,
    digest: str | None,
    size: int | None,
    detalhe: str | None = None,
) -> dict[str, Any]:
    return {
        "id": file_id,
        "path": path,
        "mime_type": mime,
        "status": status,
        "sha256": digest,
        "size_bytes": size,
        "detalhe": detalhe,
        "kind": "file",
    }


def _write_manifest(destination: Path, manifest: dict[str, Any]) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / "MANIFESTO.json"
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(target)


def _append_quarentena(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    signature = (
        record.get("sha256_original"),
        record.get("motivo"),
        record.get("fonte"),
    )
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            current = json.loads(line)
            if (
                current.get("sha256_original"),
                current.get("motivo"),
                current.get("fonte"),
            ) == signature:
                return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def _quarentena_path(root: Path, policy_id: str | None) -> Path:
    if policy_id:
        policy = get_policy(policy_id)
        relative = policy.cuarentena_output or "data/quarentena/sem_politica/"
    else:
        relative = "data/quarentena/sem_politica/"
    base = root / relative
    if base.suffix:
        return base
    return base / "quarentena.jsonl"


def _official_url(text: str) -> str | None:
    validator = VALIDATORS.get("url_validator")
    if validator is None:
        return None
    for raw in re.findall(r"https://[^\s<>'\"]+", text):
        candidate = raw.rstrip(".,;)")
        ok, _error = validator.validate({"link_fonte": candidate})
        if ok:
            return candidate
    return None


def _quarantine_record(
    *,
    text: str,
    motivo: str,
    fonte: str,
    file_id: str,
    wo_id: str,
    policy_id: str | None,
) -> dict[str, Any]:
    masked = text if text == aplicar_mascara(text) else aplicar_mascara(text)
    return {
        "texto_regra_inteiro": masked,
        "motivo": motivo,
        "fonte": fonte,
        "sha256_original": calcular_hash(masked),
        "sha256_transformado": calcular_hash(masked),
        "drive_file_id": file_id,
        "wo_id": wo_id,
        "policy_id": policy_id,
    }


def executar_atomizar(
    folder_id: str,
    *,
    root: Path | None = None,
    clock: Callable[[], str] | None = None,
) -> int:
    if not FOLDER_ID_RE.fullmatch(folder_id):
        print("ID de pasta inválido. Fail-closed.")
        return 2
    root = _repo_root(root)
    kernel = Kernel()
    obter_id = work_order_id("obter", folder_id)
    politicas: list[str] = []
    _submit(
        kernel,
        root=root,
        tarefa="atomizar",
        folder_id=folder_id,
        estado="SUBMITTED",
        motivo="atomização iniciada",
        depends_on=obter_id,
        clock=clock,
    )
    try:
        politicas = valid_policy_ids()
        valid_map, invalid_map = policy_maps()
    except Exception as exc:
        _submit(
            kernel,
            root=root,
            tarefa="atomizar",
            folder_id=folder_id,
            estado="BLOQUEADO",
            motivo=_safe_motivo(exc),
            depends_on=obter_id,
            clock=clock,
        )
        print(f"WO atomizar BLOQUEADO: {_safe_motivo(exc)}")
        return 2

    obter = load_work_order(root, obter_id)
    if (
        obter is None
        or obter.get("submitted_by") != "kernel"
        or obter.get("estado") != "EXECUTADO"
        or not obter.get("sha256_fonte")
    ):
        motivo = "WO de obter sem sha256_fonte executado pelo kernel."
        _submit(
            kernel,
            root=root,
            tarefa="atomizar",
            folder_id=folder_id,
            estado="BLOQUEADO",
            motivo=motivo,
            politicas_validas=politicas,
            depends_on=obter_id,
            acao_necessaria="Concluir a atividade obter com sha256_fonte antes de atomizar.",
            clock=clock,
        )
        print(f"WO atomizar BLOQUEADO: {motivo}")
        return 2

    manifest_path = _drive_dir(root, folder_id) / "MANIFESTO.json"
    if not manifest_path.is_file():
        _submit(
            kernel,
            root=root,
            tarefa="atomizar",
            folder_id=folder_id,
            estado="BLOQUEADO",
            motivo="Manifesto da coleta ausente.",
            politicas_validas=politicas,
            depends_on=obter_id,
            clock=clock,
        )
        return 2
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    items = list(manifest.get("items") or [])
    digest = fonte_sha256(items)
    if digest != obter.get("sha256_fonte"):
        _submit(
            kernel,
            root=root,
            tarefa="atomizar",
            folder_id=folder_id,
            estado="BLOQUEADO",
            motivo="sha256_fonte não confere com o manifesto.",
            politicas_validas=politicas,
            depends_on=obter_id,
            clock=clock,
        )
        return 2

    wo_id = work_order_id("atomizar", folder_id)
    counts: dict[str, Any] = {"atomos": 0, "quarentena": 0, "dedup": 0, "por_motivo": {}}
    try:
        for item in items:
            _atomizar_item(
                kernel,
                root=root,
                item=item,
                folder_id=folder_id,
                wo_id=wo_id,
                valid_map=valid_map,
                invalid_map=invalid_map,
                counts=counts,
            )
    except Exception as exc:
        _submit(
            kernel,
            root=root,
            tarefa="atomizar",
            folder_id=folder_id,
            estado="BLOQUEADO",
            motivo=_safe_motivo(exc),
            sha256_fonte=digest,
            politicas_validas=politicas,
            depends_on=obter_id,
            contagens=counts,
            clock=clock,
        )
        print(f"WO atomizar BLOQUEADO: {_safe_motivo(exc)}")
        return 2

    _submit(
        kernel,
        root=root,
        tarefa="atomizar",
        folder_id=folder_id,
        estado="EXECUTADO",
        motivo="atomização concluída sob as políticas válidas do kernel",
        sha256_fonte=digest,
        politicas_validas=politicas,
        depends_on=obter_id,
        contagens=counts,
        clock=clock,
    )
    print(
        "WO atomizar EXECUTADO "
        f"atomos={counts['atomos']} quarentena={counts['quarentena']}"
    )
    return 0


def _bump(counts: dict[str, Any], motivo: str) -> None:
    counts["quarentena"] += 1
    motivos = counts["por_motivo"]
    motivos[motivo] = int(motivos.get(motivo, 0)) + 1


def _atomizar_item(
    kernel: Kernel,
    *,
    root: Path,
    item: dict[str, Any],
    folder_id: str,
    wo_id: str,
    valid_map: dict[str, str],
    invalid_map: dict[str, str],
    counts: dict[str, Any],
) -> None:
    file_id = item["id"]
    path = item["path"]
    status = item["status"]
    if status == "parser_ausente":
        _store_quarentena(
            root,
            None,
            _quarantine_record(
                text="",
                motivo="parser_ausente",
                fonte=path,
                file_id=file_id,
                wo_id=wo_id,
                policy_id=None,
            )
            | {"sha256_original": item.get("sha256"), "sha256_transformado": item.get("sha256")},
        )
        _bump(counts, "parser_ausente")
        return
    if status != "acquired_text":
        raise ValueError(f"status de coleta não atomizável: {status}")

    text_path = _drive_dir(root, folder_id) / "text" / f"{file_id}.txt"
    if not text_path.is_file():
        raise ValueError(f"texto adquirido ausente: {file_id}")
    if calcular_hash(text_path.read_text(encoding="utf-8")) != item.get("sha256"):
        raise ValueError(f"sha256 do texto diverge do manifesto: {file_id}")
    masked = text_path.read_text(encoding="utf-8")
    classificacao, policy_id = classificar_caminho(path, valid_map, invalid_map)
    if classificacao != "ok":
        _store_quarentena(
            root,
            policy_id,
            _quarantine_record(
                text=masked,
                motivo=classificacao,
                fonte=path,
                file_id=file_id,
                wo_id=wo_id,
                policy_id=policy_id,
            ),
        )
        _bump(counts, classificacao)
        return

    policy = get_policy(policy_id or "")
    slug = _fonte_slug(policy.id)
    for index, candidate in enumerate(split_candidates(masked)):
        motivo = _candidate_motivo(candidate)
        if motivo:
            _store_quarentena(
                root,
                policy.id,
                _quarantine_record(
                    text=candidate,
                    motivo=motivo,
                    fonte=path,
                    file_id=file_id,
                    wo_id=wo_id,
                    policy_id=policy.id,
                ),
            )
            _bump(counts, motivo)
            continue
        year = YEAR_RE.search(candidate)
        assert year is not None
        legacy = f"{slug}:{file_id}:{index:04d}"
        payload: dict[str, Any] = {
            "id_atomo": atom_id(legacy, year.group(0)),
            "versao_contrato": "1.2.0",
            "fonte_slug": slug,
            "norma_origem": legacy,
            "texto_regra": candidate,
            "idioma": "pt-BR",
            "sha256_texto": calcular_hash(candidate),
            "sha256_original": calcular_hash(candidate),
            "hash_status": "CONFERIDO",
            "vigencia": "NAO_VERIFICADO",
            "wo_id": wo_id,
        }
        first = candidate.splitlines()[0].strip()
        if DEVICE_RE.match(first):
            payload["dispositivo_legal"] = first[:240]
        link = _official_url(candidate)
        if link:
            payload["link_fonte"] = link
        try:
            model = AtomoBlindado(**payload)
        except Exception as exc:
            message = str(exc)
            reason = "termo_opinativo" if "opinativo" in message else "acima_contrato"
            _store_quarentena(
                root,
                policy.id,
                _quarantine_record(
                    text=candidate,
                    motivo=reason,
                    fonte=path,
                    file_id=file_id,
                    wo_id=wo_id,
                    policy_id=policy.id,
                ),
            )
            _bump(counts, reason)
            continue
        data = model.model_dump(mode="json")
        decision = kernel.evaluate(data, policy.id)
        if decision.decision != Decision.APPROVED:
            _store_quarentena(
                root,
                policy.id,
                _quarantine_record(
                    text=candidate,
                    motivo="acima_contrato",
                    fonte=path,
                    file_id=file_id,
                    wo_id=wo_id,
                    policy_id=policy.id,
                ),
            )
            _bump(counts, "acima_contrato")
            continue
        written = _write_atom(root, policy.atoms_output, data)
        if written == "written":
            counts["atomos"] += 1
        elif written == "dedup":
            counts["dedup"] += 1
        else:
            _store_quarentena(
                root,
                policy.id,
                _quarantine_record(
                    text=candidate,
                    motivo="conflito_duplicata",
                    fonte=path,
                    file_id=file_id,
                    wo_id=wo_id,
                    policy_id=policy.id,
                ),
            )
            _bump(counts, "conflito_duplicata")


def _candidate_motivo(candidate: str) -> str | None:
    first = candidate.splitlines()[0].strip()
    if not DEVICE_RE.match(first):
        return "sem_dispositivo"
    if len(candidate) < 10:
        return "texto_curto"
    if len(candidate) > 800:
        return "acima_contrato"
    if YEAR_RE.search(candidate) is None:
        return "ano_ausente"
    return None


def _store_quarentena(root: Path, policy_id: str | None, record: dict[str, Any]) -> None:
    _append_quarentena(_quarentena_path(root, policy_id), record)


def _write_atom(root: Path, relative_output: str, data: dict[str, Any]) -> str:
    """Grava o átomo. conflito_duplicata não substitui o arquivo existente."""
    if data.get("vigencia") != "NAO_VERIFICADO":
        raise ValueError("átomo não pode nascer vigente")
    destination = root / relative_output / f"{data['id_atomo']}.json"
    base = (root / relative_output).resolve()
    resolved = destination.resolve()
    if base not in resolved.parents:
        raise ValueError("destino de átomo inválido")
    if destination.is_file():
        current = json.loads(destination.read_text(encoding="utf-8"))
        if current.get("sha256_texto") == data.get("sha256_texto"):
            return "dedup"
        return "conflict"
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(destination)
    return "written"


def executar_pasta(
    folder_id: str,
    *,
    root: Path | None = None,
    token_loader: Callable[[], Any] | None = None,
    crawl_fn: Callable[..., dict[str, Any]] | None = None,
    download_fn: Callable[[str, str, Any], bytes] | None = None,
    clock: Callable[[], str] | None = None,
) -> int:
    obter_code = executar_obter(
        folder_id,
        root=root,
        token_loader=token_loader,
        crawl_fn=crawl_fn,
        download_fn=download_fn,
        clock=clock,
    )
    atom_code = executar_atomizar(folder_id, root=root, clock=clock)
    if obter_code != 0 or atom_code != 0:
        return 2
    return 0
