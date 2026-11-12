"""Submissão de WO pelo Kernel e execução condicionada.

Nada é baixado nem atomizado sem WO submetida pelo Kernel.
Política que não passa no gate, ou que não contém o alvo, não autoriza a atividade.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
from contextlib import redirect_stdout
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

_CLI_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = _CLI_DIR.parents[1]
for _entry in (str(_REPO_ROOT), str(_CLI_DIR)):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from kernel.core import load_validators
from kernel.policy_registry import KernelPolicy
from packages.cli.utils import aplicar_mascara, calcular_hash
from packages.schemas.invariantes import AtomoBlindado

FOLDER_RE = re.compile(r"^[A-Za-z0-9_-]{10,128}$")
TEXT_SUFFIXES = {".txt", ".md", ".csv", ".json", ".html", ".htm", ".xml"}
MAX_BYTES = 50 * 1024 * 1024
GOOGLE_DOC = "application/vnd.google-apps.document"
GOOGLE_SHEET = "application/vnd.google-apps.spreadsheet"
FOLDER_MIME = "application/vnd.google-apps.folder"
DRIVE_ROOTS = Path("config/drive_inventory_roots_20261016.json")


@dataclass
class DriveProbes:
    """Fatos externos já resolvidos. Testes injetam os três campos."""

    credential_state: str
    public_access: str
    download: Callable[[str, Path], list[dict[str, Any]]] | None = None


def assess_policy(policy: KernelPolicy) -> tuple[bool, list[str]]:
    """Gate sem efeito colateral: validadores presentes e test_suite aprovada."""
    validators = load_validators()
    missing = [name for name in policy.validators if name not in validators]
    if missing:
        return False, [f"validador ausente: {name}" for name in missing]
    reasons: list[str] = []
    for name in policy.validators:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            passed = validators[name].run_tests()
        if not passed:
            reasons.append(f"test_suite falhou: {name}")
    return not reasons, reasons


def policy_authorizes(policy: KernelPolicy, alvo: str, contract_root: Path) -> bool:
    """O alvo precisa estar escrito na política ou no contrato de fonte."""
    if alvo in json.dumps(policy.to_dict(), ensure_ascii=False):
        return True
    contract = contract_root / policy.source_contract
    if contract.is_file() and alvo in contract.read_text(encoding="utf-8"):
        return True
    return False


def load_policy_files(policies_dir: Path) -> list[KernelPolicy]:
    policies: list[KernelPolicy] = []
    for path in sorted(policies_dir.glob("KERNEL-POLICY-*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        policies.append(KernelPolicy.from_dict(data))
    return policies


def probe_credential() -> str:
    """Não registra o valor da credencial."""
    if not os.environ.get("GDRIVE_SA_KEY") and not os.environ.get("DRIVE_ACCESS_TOKEN"):
        return "AUSENTE"
    try:
        from drive_recursive_inventory import CredentialError, load_token
    except ImportError:
        from packages.cli.drive_recursive_inventory import CredentialError, load_token
    try:
        load_token()
    except CredentialError:
        return "REJEITADA"
    return "PRESENTE"


def probe_public(url: str) -> str:
    """Classifica o acesso anônimo sem seguir o login do Google."""

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)

    opener = urllib.request.build_opener(_NoRedirect)
    request = urllib.request.Request(url, method="GET", headers={"User-Agent": "CE-Kernel/1.0"})
    try:
        with opener.open(request, timeout=20) as response:
            return "ABERTO" if response.status == 200 else f"HTTP_{response.status}"
    except urllib.error.HTTPError as exc:
        location = ""
        if exc.headers is not None:
            location = exc.headers.get("Location", "")
        if exc.code in {301, 302, 303, 307, 308} and "accounts.google.com" in location:
            return "NEGADO"
        if exc.code in {401, 403}:
            return "NEGADO"
        return f"HTTP_{exc.code}"
    except Exception:
        return "NAO_VERIFICADO"


def _wo_identity(tarefa: str, alvo: str) -> tuple[str, str]:
    slug = f"KERNEL-{tarefa.upper()}-{alvo}"
    return f"CE-WO-{slug}", f"WO-{slug}"


def _drive_roots_note(contract_root: Path, alvo: str) -> str:
    path = contract_root / DRIVE_ROOTS
    if not path.is_file():
        return "Configuração de raízes Drive ausente neste recorte."
    raw = path.read_text(encoding="utf-8")
    if alvo in raw:
        return "A pasta consta em config/drive_inventory_roots_20261016.json."
    note = "A pasta não consta em config/drive_inventory_roots_20261016.json."
    if "NO_CANONICAL_PROMOTION" in raw:
        note += " Essa configuração declara NO_CANONICAL_PROMOTION."
    return note


def _motivo(
    *,
    tarefa: str,
    alvo: str,
    status: str,
    valid_ids: list[str],
    authorizing_ids: list[str],
    credential_state: str,
    public_access: str,
    roots_note: str,
    obter_status: str | None,
) -> str:
    validos = ", ".join(valid_ids) if valid_ids else "nenhuma"
    if status == "REJEITADO":
        return (
            f"Nenhuma política passou no gate do kernel para a atividade {tarefa} "
            f"sobre {alvo}."
        )
    if not authorizing_ids:
        base = (
            f"Nenhuma política com gate aprovado autoriza o alvo {alvo}. "
            f"Políticas válidas consultadas: {validos}. "
            f"O identificador não ocorre nessas políticas nem nos contratos de fonte vinculados. "
            f"Credencial Drive: {credential_state}. Acesso público: {public_access}. {roots_note}"
        )
    elif tarefa == "obter" and credential_state != "PRESENTE":
        base = (
            f"A política {', '.join(authorizing_ids)} autoriza o alvo, "
            f"mas a credencial Drive está {credential_state}."
        )
    elif tarefa == "atomizar" and obter_status != "AUTHORIZED" and obter_status != "PASS":
        base = (
            f"Atomizar exige WO de obter AUTHORIZED submetida pelo kernel. "
            f"A WO de obter está {obter_status}."
        )
    else:
        base = (
            f"Política {', '.join(authorizing_ids)} autoriza {tarefa} de {alvo}. "
            f"Credencial Drive: {credential_state}."
        )
    if tarefa == "atomizar" and not authorizing_ids:
        base += " Atomização não executada."
    elif tarefa == "obter" and status != "AUTHORIZED":
        base += " Download não executado."
    return " ".join(base.split())


def _build_wo(
    *,
    tarefa: str,
    alvo: str,
    folder_url: str,
    status: str,
    valid: list[KernelPolicy],
    rejected: list[dict[str, str]],
    authorizing: list[KernelPolicy],
    credential_state: str,
    public_access: str,
    roots_note: str,
    obter_status: str | None,
    policy_id: str | None,
) -> dict[str, Any]:
    wo_id, short_id = _wo_identity(tarefa, alvo)
    valid_ids = [policy.id for policy in valid]
    authorizing_ids = [policy.id for policy in authorizing]
    return {
        "schema": "CE-WO-AUTHORIZATION-1.0.0",
        "id": short_id,
        "wo_id": wo_id,
        "tarefa": tarefa,
        "alvo": alvo,
        "alvo_url": folder_url,
        "slug": f"{tarefa}-{alvo}",
        "status": status,
        "estado": status,
        "submitted_by": "kernel",
        "authorized_by": "kernel",
        "policy_id": policy_id,
        "politicas_validas": valid_ids,
        "politicas_que_autorizam": authorizing_ids,
        "politicas_rejeitadas": rejected,
        "credencial_drive": credential_state,
        "acesso_publico": public_access,
        "motivo": _motivo(
            tarefa=tarefa,
            alvo=alvo,
            status=status,
            valid_ids=valid_ids,
            authorizing_ids=authorizing_ids,
            credential_state=credential_state,
            public_access=public_access,
            roots_note=roots_note,
            obter_status=obter_status,
        ),
        "conditions": [
            "Execução somente com status AUTHORIZED ou PASS e submitted_by=kernel",
            "O alvo deve constar na política válida ou no contrato de fonte",
            "Vigência permanece NAO_VERIFICADO até revisão humana",
            "Sem publicação e sem exclusão no Drive",
        ],
    }


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fresh = dict(payload)
    if path.is_file():
        try:
            current = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            current = None
        if isinstance(current, dict):
            preserved = current.get("timestamp")
            comparable_current = {k: v for k, v in current.items() if k != "timestamp"}
            comparable_fresh = {k: v for k, v in fresh.items() if k != "timestamp"}
            if comparable_current == comparable_fresh and isinstance(preserved, str):
                fresh["timestamp"] = preserved
                serialized = json.dumps(fresh, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
                if path.read_text(encoding="utf-8") == serialized:
                    return
    if "timestamp" not in fresh:
        fresh["timestamp"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    path.write_text(
        json.dumps(fresh, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _segmentar(texto: str) -> list[str]:
    texto = texto.strip()
    if not texto:
        return []
    if len(texto) <= 800:
        return [texto]
    partes = [parte.strip() for parte in re.split(r"\n+", texto) if parte.strip()]
    if len(partes) == 1:
        return partes
    return partes


def _normalizar(texto: str) -> str:
    limpo = aplicar_mascara(texto).replace("\r\n", "\n").replace("\r", "\n")
    linhas = [" ".join(linha.split()) for linha in limpo.split("\n")]
    return "\n".join(linha for linha in linhas if linha).strip()


def _dispositivo(texto: str) -> str | None:
    match = re.match(r"^(Art\.?\s*\d+\S*|§\s*\d+\S*)", texto)
    if not match:
        return None
    return match.group(1)[:120]


def _atom_id(policy_id: str, texto: str, ano: int) -> str:
    legacy = f"{policy_id}:{calcular_hash(texto)}"
    numero = int(hashlib.sha256(legacy.encode("utf-8")).hexdigest()[:12], 16)
    return f"NORM-{ano}-{numero}"


def _fonte_slug(policy: KernelPolicy, contract_root: Path) -> str | None:
    contract = contract_root / policy.source_contract
    if not contract.is_file():
        return None
    data = json.loads(contract.read_text(encoding="utf-8"))
    slug = data.get("fonte_slug")
    return slug if isinstance(slug, str) else None


def _quarentenar(path: Path, registro: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    linha = json.dumps(registro, ensure_ascii=False, sort_keys=True)
    existentes = set()
    if path.is_file():
        existentes = {item.strip() for item in path.read_text(encoding="utf-8").splitlines() if item.strip()}
    if linha in existentes:
        return
    with path.open("a", encoding="utf-8") as handle:
        handle.write(linha + "\n")


def atomizar_arquivo(
    *,
    record: dict[str, Any],
    policy: KernelPolicy,
    wo_id: str,
    contract_root: Path,
    ano: int,
) -> dict[str, int]:
    """Atomiza um arquivo já obtido. Trechos inválidos vão inteiros para a quarentena."""
    counts = {"atomos": 0, "quarentena": 0}
    nome = str(record.get("name") or record.get("path") or "arquivo")
    bruto_path = Path(str(record["path"]))
    quarentena = contract_root / policy.cuarentena_output / "validacao_invalida.jsonl"
    atoms_dir = contract_root / policy.atoms_output
    suffix = bruto_path.suffix.lower()
    sha_bytes = str(record.get("sha256") or "")
    if suffix not in TEXT_SUFFIXES:
        _quarentenar(quarentena, {
            "arquivo": nome,
            "motivo": "extracao_indisponivel",
            "sha256_original": sha_bytes,
            "texto_regra": "",
            "policy_id": policy.id,
            "wo_id": wo_id,
        })
        counts["quarentena"] += 1
        return counts

    original = bruto_path.read_text(encoding="utf-8")
    normalizado = _normalizar(original)
    sha_original = calcular_hash(original)
    if not normalizado:
        _quarentenar(quarentena, {
            "arquivo": nome,
            "motivo": "sem_texto",
            "sha256_original": sha_original,
            "texto_regra": original,
            "policy_id": policy.id,
            "wo_id": wo_id,
        })
        counts["quarentena"] += 1
        return counts

    validators = load_validators()
    fonte_slug = _fonte_slug(policy, contract_root)
    for texto in _segmentar(normalizado):
        sha_texto = calcular_hash(texto)
        candidato = {
            "id_atomo": _atom_id(policy.id, texto, ano),
            "versao_contrato": "1.2.0",
            "texto_regra": texto,
            "idioma": "pt-BR",
            "sha256_texto": sha_texto,
            "sha256_original": sha_original,
            "hash_status": "CONFERIDO",
            "vigencia": "NAO_VERIFICADO",
            "wo_id": wo_id,
        }
        if fonte_slug:
            candidato["fonte_slug"] = fonte_slug
        dispositivo = _dispositivo(texto)
        if dispositivo:
            candidato["dispositivo_legal"] = dispositivo

        erros: list[str] = []
        for nome_validador in policy.validators:
            validador = validators[nome_validador]
            ok, erro = validador.validate(candidato)
            if not ok:
                erros.append(erro or nome_validador)
        if not erros:
            try:
                modelo = AtomoBlindado.model_validate(candidato)
            except Exception as exc:
                erros.append(" ".join(str(exc).split())[:300])
        if erros:
            _quarentenar(quarentena, {
                "arquivo": nome,
                "motivo": "; ".join(erros),
                "sha256_original": sha_original,
                "texto_regra": texto,
                "policy_id": policy.id,
                "wo_id": wo_id,
            })
            counts["quarentena"] += 1
            continue

        atoms_dir.mkdir(parents=True, exist_ok=True)
        destino = atoms_dir / f"{candidato['id_atomo']}.json"
        corpo = modelo.model_dump(mode="json", exclude_none=True)
        if destino.is_file():
            anterior = json.loads(destino.read_text(encoding="utf-8"))
            if anterior.get("sha256_texto") != corpo["sha256_texto"]:
                _quarentenar(quarentena, {
                    "arquivo": nome,
                    "motivo": "conflito_duplicata",
                    "sha256_original": sha_original,
                    "texto_regra": texto,
                    "policy_id": policy.id,
                    "wo_id": wo_id,
                })
                counts["quarentena"] += 1
            continue
        destino.write_text(
            json.dumps(corpo, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        counts["atomos"] += 1
    return counts


def exigir_wo_do_kernel(payload: dict[str, Any]) -> None:
    """Toda execução exige WO submetida pelo Kernel e ainda autorizada."""
    if payload.get("submitted_by") != "kernel":
        raise PermissionError("WO não submetida pelo kernel")
    if payload.get("status") not in {"AUTHORIZED", "PASS"}:
        raise PermissionError("WO sem autorização de execução")


def download_drive_folder(folder_id: str, dest: Path) -> list[dict[str, Any]]:
    """Baixa bytes somente quando o chamador já verificou a WO AUTHORIZED."""
    try:
        from drive_recursive_inventory import crawl, load_token
    except ImportError:
        from packages.cli.drive_recursive_inventory import crawl, load_token

    token = load_token()
    inventory = crawl([{"id": folder_id, "name": folder_id}], token)
    dest.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for item in inventory["items"]:
        if item["kind"] != "file":
            continue
        target = dest / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        size = item.get("size_bytes")
        if isinstance(size, int) and size > MAX_BYTES:
            records.append({**item, "path": str(target), "baixado": False, "motivo": "acima_50mb"})
            continue
        mime = item["mime_type"]
        if mime == GOOGLE_DOC:
            url = (
                "https://www.googleapis.com/drive/v3/files/"
                f"{item['id']}/export?mimeType=text/plain"
            )
            if target.suffix.lower() not in TEXT_SUFFIXES:
                target = target.with_suffix(".txt")
        elif mime == GOOGLE_SHEET:
            url = (
                "https://www.googleapis.com/drive/v3/files/"
                f"{item['id']}/export?mimeType=text/csv"
            )
            if target.suffix.lower() not in TEXT_SUFFIXES:
                target = target.with_suffix(".csv")
        elif mime == FOLDER_MIME:
            continue
        else:
            url = f"https://www.googleapis.com/drive/v3/files/{item['id']}?alt=media"
        request = urllib.request.Request(url, headers={"Authorization": "Bearer " + token()})
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read(MAX_BYTES + 1)
        if len(payload) > MAX_BYTES:
            records.append({**item, "path": str(target), "baixado": False, "motivo": "acima_50mb"})
            continue
        target.write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        records.append({
            **item,
            "name": target.name,
            "path": str(target),
            "sha256": digest,
            "baixado": True,
        })
    return records


def run_drive_folder(
    folder_id: str,
    *,
    folder_url: str = "",
    repo_root: Path | None = None,
    policies_dir: Path | None = None,
    probes: DriveProbes | None = None,
    ano: int | None = None,
) -> int:
    """Submete as WOs de obter e atomizar e executa só o que elas autorizam."""
    if not FOLDER_RE.fullmatch(folder_id):
        return 2
    repo_root = (repo_root or _REPO_ROOT).resolve()
    policies_dir = (policies_dir or (repo_root / "contracts" / "policies")).resolve()
    contract_root = policies_dir.parents[1]
    wo_dir = repo_root / "data" / "legado"
    evidence_dir = repo_root / "evidence" / f"CE-WO-KERNEL-DRIVE-{folder_id}"
    if not folder_url:
        folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
    if probes is None:
        probes = DriveProbes(
            credential_state=probe_credential(),
            public_access=probe_public(folder_url),
            download=download_drive_folder,
        )

    policies = load_policy_files(policies_dir)
    valid: list[KernelPolicy] = []
    rejected: list[dict[str, str]] = []
    authorizing: list[KernelPolicy] = []
    for policy in policies:
        ok, reasons = assess_policy(policy)
        if not ok:
            rejected.append({"id": policy.id, "motivo": "; ".join(reasons)})
            continue
        valid.append(policy)
        if policy_authorizes(policy, folder_id, contract_root):
            authorizing.append(policy)

    roots_note = _drive_roots_note(contract_root, folder_id)
    ano = ano or datetime.now(timezone.utc).year

    if not valid:
        obter_status = "REJEITADO"
    elif not authorizing or probes.credential_state != "PRESENTE":
        obter_status = "BLOQUEADO"
    else:
        obter_status = "AUTHORIZED"

    obter = _build_wo(
        tarefa="obter",
        alvo=folder_id,
        folder_url=folder_url,
        status=obter_status,
        valid=valid,
        rejected=rejected,
        authorizing=authorizing,
        credential_state=probes.credential_state,
        public_access=probes.public_access,
        roots_note=roots_note,
        obter_status=None,
        policy_id=authorizing[0].id if len(authorizing) == 1 else None,
    )
    atom_status = "REJEITADO" if obter_status == "REJEITADO" else (
        "AUTHORIZED" if obter_status == "AUTHORIZED" else "BLOQUEADO"
    )
    atomizar = _build_wo(
        tarefa="atomizar",
        alvo=folder_id,
        folder_url=folder_url,
        status=atom_status,
        valid=valid,
        rejected=rejected,
        authorizing=authorizing,
        credential_state=probes.credential_state,
        public_access=probes.public_access,
        roots_note=roots_note,
        obter_status=obter_status,
        policy_id=authorizing[0].id if len(authorizing) == 1 else None,
    )

    obter_path = wo_dir / f"autorizacao_{obter['id']}.json"
    atom_path = wo_dir / f"autorizacao_{atomizar['id']}.json"
    _write_json(obter_path, obter)
    _write_json(atom_path, atomizar)

    resumo: dict[str, Any] = {
        "schema": "CE-KERNEL-DRIVE-DECISAO-1.0.0",
        "alvo": folder_id,
        "submitted_by": "kernel",
        "wo_obter": obter["wo_id"],
        "wo_atomizar": atomizar["wo_id"],
        "status_obter": obter_status,
        "status_atomizar": atom_status,
        "politicas_validas": [policy.id for policy in valid],
        "politicas_rejeitadas": [item["id"] for item in rejected],
        "atomos": 0,
        "quarentena": 0,
    }

    if obter_status != "AUTHORIZED":
        resumo["resultado"] = "BLOQUEADO"
        _write_json(evidence_dir / "decisao.json", resumo)
        return 2

    exigir_wo_do_kernel(obter)
    exigir_wo_do_kernel(atomizar)

    destino = repo_root / "data" / "raw" / "drive" / folder_id
    try:
        baixar = probes.download or download_drive_folder
        records = baixar(folder_id, destino)
    except Exception as exc:
        obter["status"] = "BLOQUEADO"
        obter["estado"] = "BLOQUEADO"
        obter["motivo"] = f"Download falhou: {type(exc).__name__}"
        atomizar["status"] = "BLOQUEADO"
        atomizar["estado"] = "BLOQUEADO"
        atomizar["motivo"] = "Atomizar não executada porque o download falhou."
        _write_json(obter_path, obter)
        _write_json(atom_path, atomizar)
        resumo["resultado"] = "BLOQUEADO"
        resumo["erro"] = type(exc).__name__
        _write_json(evidence_dir / "decisao.json", resumo)
        return 2

    manifest = {
        "schema": "CE-DRIVE-OBTER-1.0.0",
        "wo_id": obter["wo_id"],
        "alvo": folder_id,
        "arquivos": [
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "sha256": item.get("sha256"),
                "baixado": item.get("baixado", True),
            }
            for item in records
        ],
    }
    _write_json(destino / "MANIFESTO.json", manifest)

    totais = {"atomos": 0, "quarentena": 0}
    for policy in authorizing:
        for record in records:
            if record.get("baixado") is False:
                continue
            parte = atomizar_arquivo(
                record=record,
                policy=policy,
                wo_id=atomizar["wo_id"],
                contract_root=contract_root,
                ano=ano,
            )
            totais["atomos"] += parte["atomos"]
            totais["quarentena"] += parte["quarentena"]

    obter["status"] = "PASS"
    obter["estado"] = "PASS"
    atomizar["status"] = "PASS"
    atomizar["estado"] = "PASS"
    atomizar["motivo"] = (
        f"Atomização executada sob {atomizar['wo_id']}. "
        f"Átomos gravados: {totais['atomos']}. Quarentena: {totais['quarentena']}. "
        "Vigência NAO_VERIFICADO."
    )
    _write_json(obter_path, obter)
    _write_json(atom_path, atomizar)
    resumo["status_obter"] = "PASS"
    resumo["status_atomizar"] = "PASS"
    resumo["resultado"] = "PASS"
    resumo["atomos"] = totais["atomos"]
    resumo["quarentena"] = totais["quarentena"]
    _write_json(evidence_dir / "decisao.json", resumo)
    return 0
