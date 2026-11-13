"""Atividades de obter e atomizar uma pasta Drive.

Toda atividade recebe uma WO submetida pelo Kernel antes de qualquer efeito.
A pasta pedida só seguiria para coleta se estivesse na autoridade Drive,
nas raízes registradas e em drive_folder_ids de uma política com parser.
Nenhuma dessas condições vale para o pedido atual: o Kernel grava BLOQUEADO
e não abre a rede.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from kernel.core import Kernel
from kernel.work_order import load_work_order, work_order_id

REPO_ROOT = Path(__file__).resolve().parents[3]
FOLDER_ID_RE_MIN = 20
FOLDER_ID_RE_MAX = 80
ROOTS_RELATIVE = Path("config") / "drive_inventory_roots_20261016.json"
AUTHORITY_RELATIVE = Path("data") / "legado" / "drive_raizes.json"
OBTER_ACAO = (
    "Incluir a pasta na autoridade data/legado/drive_raizes.json e em "
    "drive_folder_ids de uma KERNEL-POLICY com parser versionado, e configurar "
    "GDRIVE_SA_KEY ou DRIVE_ACCESS_TOKEN. O contrato atual das raízes é "
    "metadata_only com NO_CANONICAL_PROMOTION."
)
ATOMIZAR_ACAO = (
    "Concluir a WO de obter com sha256_fonte executado pelo kernel antes de atomizar."
)


def _repo_root(root: Path | None) -> Path:
    return (root or REPO_ROOT).resolve()


def _valid_folder_id(folder_id: str) -> bool:
    if not FOLDER_ID_RE_MIN <= len(folder_id) <= FOLDER_ID_RE_MAX:
        return False
    return all(char.isalnum() or char in "_-" for char in folder_id)


def _policy_ids(root: Path, folder_id: str) -> list[str]:
    policies = root / "contracts" / "policies"
    if not policies.is_dir():
        return []
    found: list[str] = []
    for path in sorted(policies.glob("KERNEL-POLICY-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"política ilegível: {path.name}")
        declared = data.get("drive_folder_ids")
        if isinstance(declared, list) and folder_id in declared:
            policy_id = data.get("id")
            if not isinstance(policy_id, str) or not policy_id:
                raise ValueError(f"política sem id: {path.name}")
            parser = data.get("parser")
            if not isinstance(parser, str) or not (root / parser).is_file():
                continue
            found.append(policy_id)
    return found


def avaliar_admissao(
    root: Path,
    folder_id: str,
    environ: Mapping[str, str] | None = None,
) -> tuple[list[str], list[str]]:
    """Razões de bloqueio, em ordem estável, e políticas que declaram a pasta."""
    reasons: list[str] = []
    env = os.environ if environ is None else environ
    roots_path = root / ROOTS_RELATIVE
    if not roots_path.is_file():
        reasons.append(f"{ROOTS_RELATIVE.as_posix()} ausente")
    else:
        data = json.loads(roots_path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"{ROOTS_RELATIVE.as_posix()} ilegível")
        ids: set[str] = set()
        for row in data.get("roots") or []:
            if isinstance(row, dict) and isinstance(row.get("id"), str):
                ids.add(row["id"])
        if folder_id not in ids:
            reasons.append(
                f"pasta {folder_id} ausente das raízes registradas em {ROOTS_RELATIVE.as_posix()}"
            )
        restrictions = data.get("restrictions") or []
        if (
            "NO_CANONICAL_PROMOTION" in restrictions
            or data.get("scope") == "registered_roots_metadata_only"
        ):
            reasons.append(
                "contrato Drive restringe as raízes a metadata_only e NO_CANONICAL_PROMOTION"
            )
    authority = root / AUTHORITY_RELATIVE
    if not authority.is_file():
        reasons.append(f"autoridade {AUTHORITY_RELATIVE.as_posix()} inexistente")
    else:
        payload = json.loads(authority.read_text(encoding="utf-8"))
        listed = _authority_ids(payload)
        if folder_id not in listed:
            reasons.append(
                f"pasta {folder_id} ausente da autoridade {AUTHORITY_RELATIVE.as_posix()}"
            )
    policies = _policy_ids(root, folder_id)
    if not policies:
        reasons.append(
            "nenhuma política do kernel declara drive_folder_ids com parser para esta pasta"
        )
    if not env.get("GDRIVE_SA_KEY") and not env.get("DRIVE_ACCESS_TOKEN"):
        reasons.append(
            "Neither GDRIVE_SA_KEY nor DRIVE_ACCESS_TOKEN is configured; fail closed."
        )
    return reasons, policies


def _authority_ids(payload: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(payload, dict):
        if isinstance(payload.get("id"), str):
            found.add(payload["id"])
        for key in ("roots", "raizes", "folders", "pastas"):
            found.update(_authority_ids(payload.get(key)))
    elif isinstance(payload, list):
        for item in payload:
            found.update(_authority_ids(item))
    return found


def _submit(kernel: Kernel, **kwargs: Any) -> dict[str, Any]:
    return kernel.submit_wo(**kwargs)


def executar_obter(
    folder_id: str,
    *,
    root: Path | None = None,
    clock: Any = None,
    environ: Mapping[str, str] | None = None,
) -> int:
    if not _valid_folder_id(folder_id):
        print("ID de pasta inválido. Fail-closed.")
        return 2
    root = _repo_root(root)
    kernel = Kernel()
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
        reasons, policies = avaliar_admissao(root, folder_id, environ)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        reasons, policies = [str(exc)[:500]], []
    if not reasons:
        reasons = [
            "falha fechada: nenhuma política válida declara parser executável para baixar e atomizar esta pasta"
        ]
    motivo = "; ".join(reasons)
    _submit(
        kernel,
        root=root,
        tarefa="obter",
        folder_id=folder_id,
        estado="BLOQUEADO",
        motivo=motivo,
        politicas_validas=policies,
        contagens={"arquivos": 0, "bytes": 0},
        acao_necessaria=OBTER_ACAO,
        clock=clock,
    )
    print(f"WO obter BLOQUEADO: {motivo}")
    return 2


def executar_atomizar(
    folder_id: str,
    *,
    root: Path | None = None,
    clock: Any = None,
    environ: Mapping[str, str] | None = None,
) -> int:
    if not _valid_folder_id(folder_id):
        print("ID de pasta inválido. Fail-closed.")
        return 2
    root = _repo_root(root)
    kernel = Kernel()
    obter_id = work_order_id("obter", folder_id)
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
        _reasons, policies = avaliar_admissao(root, folder_id, environ)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        policies = []
        motivo = str(exc)[:500]
        _submit(
            kernel,
            root=root,
            tarefa="atomizar",
            folder_id=folder_id,
            estado="BLOQUEADO",
            motivo=motivo,
            depends_on=obter_id,
            contagens={"atomos": 0, "bytes": 0},
            acao_necessaria=ATOMIZAR_ACAO,
            clock=clock,
        )
        print(f"WO atomizar BLOQUEADO: {motivo}")
        return 2

    obter = load_work_order(root, obter_id)
    estado = obter.get("estado") if obter else "AUSENTE"
    submetida = bool(obter and obter.get("submitted_by") == "kernel")
    executada = bool(
        obter
        and submetida
        and estado == "EXECUTADO"
        and isinstance(obter.get("sha256_fonte"), str)
        and len(obter["sha256_fonte"]) == 64
    )
    if not executada:
        motivo = (
            f"WO de obter {obter_id} está {estado} e não possui sha256_fonte "
            "executado pelo kernel."
        )
        _submit(
            kernel,
            root=root,
            tarefa="atomizar",
            folder_id=folder_id,
            estado="BLOQUEADO",
            motivo=motivo,
            politicas_validas=policies,
            depends_on=obter_id,
            contagens={"atomos": 0, "bytes": 0},
            acao_necessaria=ATOMIZAR_ACAO,
            clock=clock,
        )
        print(f"WO atomizar BLOQUEADO: {motivo}")
        return 2

    motivo = (
        "falha fechada: WO de obter executada, mas nenhuma política válida "
        "declara parser executável para atomizar esta pasta"
    )
    _submit(
        kernel,
        root=root,
        tarefa="atomizar",
        folder_id=folder_id,
        estado="BLOQUEADO",
        motivo=motivo,
        politicas_validas=policies,
        depends_on=obter_id,
        sha256_fonte=obter.get("sha256_fonte") if obter else None,
        contagens={"atomos": 0, "bytes": 0},
        acao_necessaria=ATOMIZAR_ACAO,
        clock=clock,
    )
    print(f"WO atomizar BLOQUEADO: {motivo}")
    return 2


def executar_pasta(
    folder_id: str,
    *,
    root: Path | None = None,
    clock: Any = None,
    environ: Mapping[str, str] | None = None,
) -> int:
    """Submete obter e, em seguida, atomizar. Exit 2 se qualquer uma bloquear."""
    obter = executar_obter(folder_id, root=root, clock=clock, environ=environ)
    atomizar = executar_atomizar(folder_id, root=root, clock=clock, environ=environ)
    if obter == 0 and atomizar == 0:
        return 0
    return 2
