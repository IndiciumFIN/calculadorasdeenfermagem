"""Submissão de WO pelo Kernel.

O Kernel registra a atividade e aplica a política já versionada.
Não cria política, não se designa aprovador humano e não baixa bytes
quando a política recusa.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

FOLDER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{16,}$")
FOLDER_URL_RE = re.compile(r"/folders/([A-Za-z0-9_-]{16,})")
ATIVIDADES = ("obter", "atomizar")
SCHEMA = "CE-WO-AUTHORIZATION-1.0.0"
ROOTS_RELATIVE = Path("config/drive_inventory_roots_20261016.json")
POLICIES_RELATIVE = Path("contracts/policies")
WO_DIR_RELATIVE = Path("data/legado")


def parse_folder_id(value: str) -> str:
    """Aceita o id cru ou a URL da pasta. Recusa qualquer outro formato."""
    raw = value.strip()
    found = FOLDER_URL_RE.search(raw)
    folder_id = found.group(1) if found else raw
    if not FOLDER_ID_RE.fullmatch(folder_id):
        raise ValueError("identificador de pasta Drive inválido")
    return folder_id


def load_json_object(path: Path) -> dict[str, Any] | None:
    """Lê o primeiro objeto JSON. Arquivos legados trazem comentários depois dele."""
    try:
        text = path.read_text(encoding="utf-8")
        data, _ = json.JSONDecoder().raw_decode(text.lstrip())
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def load_policy_documents(policies_dir: Path) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    if not policies_dir.is_dir():
        return documents
    for path in sorted(policies_dir.glob("KERNEL-POLICY-*.json")):
        data = load_json_object(path)
        if data and isinstance(data.get("id"), str):
            documents.append(data)
    return documents


def load_registered_root_ids(path: Path) -> set[str]:
    data = load_json_object(path)
    if not data:
        return set()
    roots = data.get("roots")
    if not isinstance(roots, list):
        return set()
    return {
        item["id"]
        for item in roots
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def policy_authorizes_folder(policy: dict[str, Any], folder_id: str) -> bool:
    """Só um campo explícito da política autoriza a pasta. Texto livre não autoriza."""
    if policy.get("drive_folder_id") == folder_id:
        return True
    listed = policy.get("drive_folder_ids")
    return isinstance(listed, list) and folder_id in listed


def human_authorization_present(legado_dir: Path, folder_id: str) -> bool:
    """WO humana preexistente, nomeando esta pasta e um aprovador que não é o Kernel."""
    if not legado_dir.is_dir():
        return False
    for path in sorted(legado_dir.glob("autorizacao_WO-*.json")):
        data = load_json_object(path)
        if not data:
            continue
        named = data.get("folder_id") == folder_id or data.get("lote") == f"drive:{folder_id}"
        estado = data.get("estado") or data.get("status")
        approver = data.get("authorized_by")
        if (
            named
            and estado == "PREAUTHORIZED"
            and isinstance(approver, str)
            and approver.strip()
            and approver.strip().lower() != "kernel"
        ):
            return True
    return False


def build_work_order(
    *,
    folder_id: str,
    tarefa: str,
    policies: list[dict[str, Any]],
    registered_root_ids: set[str],
    credential_present: bool,
    drive_api_http_status: int | None,
    human_authorization: bool,
) -> dict[str, Any]:
    """Monta a WO. Estado PREAUTHORIZED não é emitido por este caminho."""
    motivos: list[str] = []
    if tarefa not in ATIVIDADES:
        motivos.append(f"tarefa '{tarefa}' fora de obter/atomizar")
    if folder_id not in registered_root_ids:
        motivos.append(
            "pasta fora das raízes registradas; escopo registered_roots_metadata_only"
        )
    if not credential_present:
        motivos.append(
            "credencial ausente (GDRIVE_SA_KEY e DRIVE_ACCESS_TOKEN); fail-closed"
        )
    if drive_api_http_status != 200:
        motivos.append(
            f"API Drive files.get respondeu HTTP {drive_api_http_status}; "
            "página HTML não é arquivo de fonte"
        )
    authorizing = [
        policy["id"]
        for policy in policies
        if isinstance(policy.get("id"), str) and policy_authorizes_folder(policy, folder_id)
    ]
    if not authorizing:
        motivos.append("nenhuma política versionada autoriza esta pasta")
    if not human_authorization:
        motivos.append("não há autorização humana prévia para esta pasta")
    if tarefa == "obter":
        motivos.append("obtenção de bytes recusada; inventário permanece BYTES_NOT_ACQUIRED")
    if tarefa == "atomizar":
        motivos.append("sha256_fonte ausente")
        motivos.append("restrição NO_CANONICAL_PROMOTION; átomos não nascem do Drive")

    wo_id = f"DRIVE-{folder_id}-{tarefa}"
    blocked = bool(motivos)
    return {
        "schema": SCHEMA,
        "wo_id": f"CE-WO-{wo_id}",
        "id": f"WO-{wo_id}",
        "tarefa": tarefa,
        "lote": f"drive:{folder_id}",
        "folder_id": folder_id,
        "folder_url": f"https://drive.google.com/drive/folders/{folder_id}",
        "estado": "BLOQUEADO" if blocked else "SUBMETIDA",
        "status": "BLOQUEADO" if blocked else "SUBMETIDA",
        "submitted_by": "kernel",
        "authorized_by": None,
        "sha256_fonte": None,
        "bytes_acquired": False,
        "atoms_emitted": 0,
        "credential_present": credential_present,
        "registered_root": folder_id in registered_root_ids,
        "drive_api_http_status": drive_api_http_status,
        "policies_consulted": [policy["id"] for policy in policies if isinstance(policy.get("id"), str)],
        "policies_authorizing_folder": authorizing,
        "motivo": motivos[0] if motivos else "submetida; este comando não executa bytes",
        "motivos": motivos,
        "acao_necessaria": (
            "Incluir a pasta numa política versionada e nas raízes registradas, "
            "fornecer credencial de leitura e gravar autorização humana. "
            "O Kernel não baixa nem atomiza antes disso."
            if blocked
            else "WO submetida sem execução de bytes."
        ),
        "restrictions": [
            "NO_DELETE",
            "NO_PUBLICATION",
            "NO_CANONICAL_PROMOTION",
            "BYTES_NOT_ACQUIRED",
        ],
    }


def execution_exit_code(orders: list[dict[str, Any]]) -> int:
    """Exit 0 só com bytes adquiridos. Submissão bloqueada encerra em 2."""
    if not orders:
        return 2
    if any(order.get("bytes_acquired") is not True or order.get("estado") == "BLOQUEADO" for order in orders):
        return 2
    return 0


def write_work_order(directory: Path, order: dict[str, Any]) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"autorizacao_{order['id']}.json"
    payload = json.dumps(order, ensure_ascii=False, indent=2) + "\n"
    if not path.exists() or path.read_text(encoding="utf-8") != payload:
        path.write_text(payload, encoding="utf-8")
    return path


def credential_present() -> bool:
    try:
        from packages.cli.drive_recursive_inventory import CredentialError, load_token
    except ImportError:
        from drive_recursive_inventory import CredentialError, load_token
    try:
        load_token()
    except CredentialError:
        return False
    return True


def probe_drive_metadata_status(folder_id: str) -> int | None:
    """Consulta só o status de metadados. Não grava corpo nem trata HTML como arquivo."""
    url = "https://www.googleapis.com/drive/v3/files/" + folder_id + "?fields=id,name,mimeType"
    request = Request(
        url,
        method="GET",
        headers={"Accept": "application/json", "User-Agent": "CE-Kernel/1.0"},
    )
    try:
        with urlopen(request, timeout=20) as response:
            response.read(64)
            return int(response.status)
    except HTTPError as exc:
        return int(exc.code)
    except (URLError, TimeoutError, OSError):
        return None


def submit_drive_activities(
    *,
    folder: str,
    tarefas: list[str],
    repo_root: Path,
    drive_api_http_status: int | None | object = ...,
) -> list[dict[str, Any]]:
    """Submete uma WO por atividade e devolve os documentos gravados."""
    folder_id = parse_folder_id(folder)
    if not tarefas:
        raise ValueError("nenhuma atividade informada")
    unknown = [item for item in tarefas if item not in ATIVIDADES]
    if unknown:
        raise ValueError(f"tarefa desconhecida: {', '.join(unknown)}")

    policies = load_policy_documents(repo_root / POLICIES_RELATIVE)
    if not policies:
        raise ValueError("nenhuma política KERNEL-POLICY carregada; fail-closed")
    roots = load_registered_root_ids(repo_root / ROOTS_RELATIVE)
    legado = repo_root / WO_DIR_RELATIVE
    has_credential = credential_present()
    has_human = human_authorization_present(legado, folder_id)
    status = probe_drive_metadata_status(folder_id) if drive_api_http_status is ... else drive_api_http_status

    orders: list[dict[str, Any]] = []
    for tarefa in tarefas:
        order = build_work_order(
            folder_id=folder_id,
            tarefa=tarefa,
            policies=policies,
            registered_root_ids=roots,
            credential_present=has_credential,
            drive_api_http_status=status if isinstance(status, int) or status is None else None,
            human_authorization=has_human,
        )
        write_work_order(legado, order)
        orders.append(order)
    return orders
