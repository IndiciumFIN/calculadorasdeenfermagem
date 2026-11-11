"""Submissão de Work Orders pelo Kernel.

Regra 8: nada é baixado, atomizado ou migrado sem WO formalizada.
Regra 3: acesso sem credencial falha fechado (exit 2).
Regra 9: WO BLOQUEADO registra o motivo técnico.

O Kernel não escolhe a política de um arquivo. Sem contrato que associe o
arquivo a uma política com gate PASS, os bytes não são baixados e nenhum
átomo é escrito.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

FOLDER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,128}$")
WO_FILE_RE = re.compile(r"^autorizacao_WO-(\d+)\.json$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _read_json_object(path: Path) -> dict[str, Any]:
    """Lê o primeiro objeto JSON. Arquivos legados têm comentários depois dele."""
    decoder = json.JSONDecoder()
    data, _ = decoder.raw_decode(path.read_text(encoding="utf-8").lstrip())
    if not isinstance(data, dict):
        raise ValueError(f"WO inválida: {path}")
    return data


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _load_token():
    try:
        from packages.cli.drive_recursive_inventory import load_token
    except ImportError:
        from drive_recursive_inventory import load_token
    return load_token()


def _credential_error_type():
    try:
        from packages.cli.drive_recursive_inventory import CredentialError
    except ImportError:
        from drive_recursive_inventory import CredentialError
    return CredentialError


def probe_drive_metadata(folder_id: str) -> int | None:
    """Consulta a API sem gravar corpo. Só o código HTTP entra na WO."""
    if not FOLDER_ID_RE.fullmatch(folder_id):
        raise ValueError("folder_id fora do formato aceito pelo Kernel")
    url = f"https://www.googleapis.com/drive/v3/files/{folder_id}?fields=id"
    request = Request(url, headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=20) as response:
            return int(response.status)
    except HTTPError as exc:
        return int(exc.code)
    except URLError:
        return None


def _gate_map() -> dict[str, dict[str, str]]:
    from kernel.core import Kernel
    from kernel.policy_registry import list_policies

    kernel = Kernel()
    report: dict[str, dict[str, str]] = {}
    for policy in list_policies():
        ok, detail = kernel.policy_gate_status(policy.id)
        report[policy.id] = {
            "resultado": "PASS" if ok else "FAIL",
            "detalhe": detail,
            "wo_required": str(bool(policy.wo_required)).lower(),
        }
    return report


def _next_seq(legado: Path) -> int:
    highest = 0
    if legado.is_dir():
        for path in legado.glob("autorizacao_WO-*.json"):
            match = WO_FILE_RE.match(path.name)
            if match:
                highest = max(highest, int(match.group(1)))
    return highest + 1


def _find_existing(legado: Path, folder_id: str, tarefa: str) -> dict[str, Any] | None:
    if not legado.is_dir():
        return None
    for path in sorted(legado.glob("autorizacao_WO-*.json")):
        try:
            data = _read_json_object(path)
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        if data.get("folder_id") == folder_id and data.get("tarefa") == tarefa:
            data["_path"] = str(path)
            return data
    return None


def _estado(data: dict[str, Any]) -> str:
    raw = data.get("estado") or data.get("status") or "DESCONHECIDO"
    return str(raw)


def rebuild_status(root: Path) -> Path:
    legado = root / "data" / "legado"
    orders: list[dict[str, Any]] = []
    if legado.is_dir():
        for path in sorted(legado.glob("autorizacao_WO-*.json")):
            try:
                data = _read_json_object(path)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            estado = _estado(data)
            entry: dict[str, Any] = {
                "arquivo": path.relative_to(root).as_posix(),
                "estado": estado,
                "id": data.get("id") or data.get("wo_id"),
                "lote": data.get("lote") or data.get("slug"),
                "tarefa": data.get("tarefa"),
                "wo_id": data.get("wo_id"),
            }
            motivo = data.get("motivo")
            if estado == "BLOQUEADO" and not motivo:
                motivo = data.get("rationale")
            if motivo:
                entry["motivo"] = motivo
            orders.append(entry)
    payload = {
        "schema": "CE-WO-STATUS-1.0.0",
        "updated_by": "kernel",
        "work_orders": orders,
    }
    destination = legado / "status_wo.json"
    _write_json(destination, payload)
    return destination


def submit_work_order(
    *,
    root: Path,
    folder_id: str,
    tarefa: str,
    gate: dict[str, dict[str, str]],
    estado: str,
    motivo: str,
    ultimo_http_code: int | None,
    depende_de: str | None = None,
    entradas: int = 0,
) -> dict[str, Any]:
    """Grava a WO se ainda não existe para (pasta, tarefa). Não reescreve histórico."""
    if tarefa not in {"obter", "atomizar", "migrar"}:
        raise ValueError(f"tarefa não permitida: {tarefa}")
    if estado not in {"BLOQUEADO", "AUTORIZADO"}:
        raise ValueError("o Kernel só submete BLOQUEADO ou AUTORIZADO")
    legado = root / "data" / "legado"
    existing = _find_existing(legado, folder_id, tarefa)
    if existing is not None:
        return existing

    seq = _next_seq(legado)
    stamp = datetime.now(timezone.utc)
    day = stamp.strftime("%Y%m%d")
    wo_id = f"CE-WO-{day}-WO-{seq:04d}"
    canonical_id = f"WO-{stamp.strftime('%Y_%m_%d')}_{seq:04d}"
    valid = sorted(pid for pid, row in gate.items() if row["resultado"] == "PASS")
    rejected = sorted(pid for pid, row in gate.items() if row["resultado"] != "PASS")
    payload: dict[str, Any] = {
        "acao_necessaria": (
            "Configurar GDRIVE_SA_KEY ou DRIVE_ACCESS_TOKEN e um contrato que "
            "associe cada arquivo a uma política com gate PASS antes de baixar bytes."
        ),
        "autorizado_por": "kernel",
        "conditions": [
            "Nada é baixado, atomizado ou migrado enquanto estado=BLOQUEADO",
            "Credencial GDRIVE_SA_KEY ou DRIVE_ACCESS_TOKEN é obrigatória",
            "Atomização só com política cujo gate PASS e vínculo contratual do arquivo",
            "Vigência permanece NAO_VERIFICADO até revisão humana",
        ],
        "entradas": entradas,
        "estado": estado,
        "evidence_reference": f"evidence/{wo_id}/bloqueio.json",
        "folder_id": folder_id,
        "id": canonical_id,
        "lote": f"drive_folder_{folder_id}",
        "motivo": motivo,
        "politicas_rejeitadas_no_gate": rejected,
        "politicas_validas_no_gate": valid,
        "policy_id": None,
        "rationale": motivo,
        "schema": "CE-WO-AUTHORIZATION-1.0.0",
        "slug": f"drive_{folder_id}_{tarefa}",
        "status": estado,
        "submitted_by": "kernel",
        "tarefa": tarefa,
        "tentativas": 1,
        "timestamp": stamp.replace(microsecond=0).isoformat(),
        "ultimo_http_code": ultimo_http_code,
        "wo_id": wo_id,
    }
    if depende_de:
        payload["depende_de"] = depende_de
    path = legado / f"autorizacao_WO-{seq:04d}.json"
    _write_json(path, payload)
    payload["_path"] = str(path)
    return payload


def atomize_authorized(wo: dict[str, Any]) -> int:
    """Recusa atomização sem WO AUTORIZADO, política vinculada e bytes classificados.

    Este módulo não escreve átomos. policy_id nulo ou estado BLOQUEADO → exit 2.
    """
    if wo.get("submitted_by") != "kernel":
        return 2
    if wo.get("tarefa") != "atomizar":
        return 2
    if _estado(wo) != "AUTORIZADO" or not wo.get("policy_id"):
        return 2
    print("Kernel REJECTED: não há bytes classificados. Nenhum átomo escrito.")
    return 2


def execute_drive_folder(
    folder_id: str,
    root: Path | None = None,
    *,
    token_loader: Callable[[], Any] | None = None,
    http_probe: Callable[[str], int | None] | None = None,
) -> int:
    """Submete as WOs de obter e atomizar e para sem baixar bytes."""
    if not FOLDER_ID_RE.fullmatch(folder_id):
        print("Kernel REJECTED: folder_id inválido. Nenhuma WO, nenhum download.")
        return 2

    root = root or repo_root()
    gate = _gate_map()
    valid = sorted(pid for pid, row in gate.items() if row["resultado"] == "PASS")
    loader = token_loader or _load_token
    probe = http_probe or probe_drive_metadata
    CredentialError = _credential_error_type()

    http_code: int | None = None
    entradas = 0
    try:
        loader()
        credencial = True
    except CredentialError:
        credencial = False
        http_code = probe(folder_id)

    if not credencial:
        motivo_obter = (
            "Acesso sem credencial. Nem GDRIVE_SA_KEY nem DRIVE_ACCESS_TOKEN "
            f"estão configurados. A API Drive respondeu HTTP {http_code}. "
            "Fail-closed: bytes não foram baixados."
        )
    elif not valid:
        motivo_obter = (
            "Credencial presente, mas nenhuma política passou no gate do Kernel. "
            "Fail-closed: bytes não foram baixados."
        )
    else:
        motivo_obter = (
            "Há políticas com gate PASS, mas nenhum contrato associa os arquivos "
            f"da pasta {folder_id} a uma delas. O Kernel não infere a política. "
            "Fail-closed: bytes não foram baixados."
        )

    obter = submit_work_order(
        root=root,
        folder_id=folder_id,
        tarefa="obter",
        gate=gate,
        estado="BLOQUEADO",
        motivo=motivo_obter,
        ultimo_http_code=http_code,
        entradas=entradas,
    )
    motivo_atom = (
        f"Atomização depende da WO {obter.get('wo_id')} ({_estado(obter)}). "
        "Sem bytes classificados por política válida, nenhum átomo foi escrito. "
        "policy_id permanece nulo."
    )
    atom = submit_work_order(
        root=root,
        folder_id=folder_id,
        tarefa="atomizar",
        gate=gate,
        estado="BLOQUEADO",
        motivo=motivo_atom,
        ultimo_http_code=http_code,
        depende_de=obter.get("wo_id"),
        entradas=0,
    )
    evidence = {
        "schema": "CE-WO-DRIVE-BLOCK-1.0.0",
        "folder_id": folder_id,
        "submitted_by": "kernel",
        "credencial_presente": credencial,
        "ultimo_http_code": http_code,
        "bytes_baixados": 0,
        "atomos_escritos": 0,
        "politicas_validas_no_gate": valid,
        "wo_obter": obter.get("wo_id"),
        "wo_atomizar": atom.get("wo_id"),
        "atomize_exit": atomize_authorized(atom),
        "timestamp": _now(),
    }
    for wo in (obter, atom):
        evidence_path = root / "evidence" / str(wo.get("wo_id")) / "bloqueio.json"
        if not evidence_path.exists():
            _write_json(evidence_path, evidence)
    rebuild_status(root)
    print(
        f"Kernel BLOQUEADO | obter={obter.get('wo_id')} | "
        f"atomizar={atom.get('wo_id')} | políticas PASS={len(valid)} | "
        f"HTTP={http_code} | bytes=0"
    )
    return 2
