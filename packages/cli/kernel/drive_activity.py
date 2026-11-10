"""Atividade Drive submetida pelo Kernel.

Nada é listado, baixado ou atomizado antes de uma WO escrita por este módulo.
Sem `drive_folder_ids` na política vigente, a decisão é BLOQUEADO (exit 2).
O Kernel não cria política e não promove vigência.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

_REPO = Path(__file__).resolve().parents[3]
_CLI = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

FOLDER_MIME = "application/vnd.google-apps.folder"
TEXT_MIMES = {
    "text/plain",
    "text/csv",
    "text/markdown",
    "text/tab-separated-values",
    "application/json",
    "application/xml",
    "text/xml",
}
LEGAL_MARK = re.compile(r"(art\.|artigo|§|inciso|parágrafo|paragrafo)", re.IGNORECASE)
FOLDER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,80}$")
YEAR_RE = re.compile(r"(?:19|20)\d{2}")
OPINION = (
    "infelizmente",
    "importante destacar",
    "recomenda-se",
    "sugerimos",
    "a nosso ver",
    "consideramos que",
    "acreditamos que",
    "no nosso entendimento",
)
MAX_BYTES = 20_000_000
MAX_FILES = 500
MAX_FOLDERS = 50
ROOTS_REL = "config/drive_inventory_roots_20261016.json"
AUTHORITY_REL = "data/legado/drive_raizes.json"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def wo_id_for(folder_id: str) -> str:
    digest = hashlib.sha256(folder_id.encode("utf-8")).hexdigest()[:12]
    return f"CE-WO-DRIVE-{digest}"


def load_policies(root: Path) -> list[dict]:
    policies_dir = root / "contracts" / "policies"
    if not policies_dir.is_dir():
        raise FileNotFoundError(f"Registry de políticas ausente: {policies_dir}")
    policies = []
    for path in sorted(policies_dir.glob("KERNEL-POLICY-*.json")):
        data = _read_json(path)
        if not isinstance(data, dict) or data.get("id") != path.stem:
            raise ValueError(f"Política ilegível: {path}")
        policies.append(data)
    if not policies:
        raise ValueError("Nenhuma política KERNEL-POLICY registrada. Fail-closed.")
    return policies


def load_roots(root: Path) -> dict:
    path = root / ROOTS_REL
    if not path.is_file():
        raise FileNotFoundError(f"Contrato de raízes ausente: {ROOTS_REL}")
    data = _read_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("roots"), list):
        raise ValueError("Contrato de raízes Drive inválido.")
    return data


def credencial_presente(env: dict[str, str] | None = None) -> bool:
    source = os.environ if env is None else env
    return bool(source.get("GDRIVE_SA_KEY") or source.get("DRIVE_ACCESS_TOKEN"))


def politicas_autorizadoras(policies: list[dict], folder_id: str) -> list[dict]:
    found = []
    for policy in policies:
        ids = policy.get("drive_folder_ids")
        if isinstance(ids, list) and folder_id in ids:
            found.append(policy)
    return found


def avaliar(
    folder_id: str,
    policies: list[dict],
    roots: dict,
    credencial: bool,
    autoridade_presente: bool,
) -> dict:
    """Decisão determinística. Não acessa a rede e não grava arquivo."""
    motivos: list[str] = []
    if not FOLDER_ID_RE.fullmatch(folder_id):
        motivos.append("folder_id fora do formato aceito pelo Kernel.")
    if not policies:
        motivos.append("Nenhuma política KERNEL-POLICY registrada. Fail-closed.")
    autorizam = politicas_autorizadoras(policies, folder_id) if policies else []
    if len(autorizam) > 1:
        ids = ", ".join(p.get("id", "?") for p in autorizam)
        motivos.append(f"Mais de uma política autoriza o folder ({ids}). Fail-closed.")
    if len(autorizam) == 0:
        motivos.append(
            "Nenhuma política em contracts/policies lista este folder_id em drive_folder_ids."
        )
    else:
        policy = autorizam[0]
        if not policy.get("validators"):
            motivos.append(f"{policy.get('id')} não tem validadores. Fail-closed.")
        if not policy.get("atoms_output") or not policy.get("quarentena_output"):
            motivos.append(f"{policy.get('id')} não define atoms_output e quarentena_output.")
        if policy.get("wo_required") is False:
            motivos.append(f"{policy.get('id')} não exige WO; atividade Drive recusada.")
    root_ids = [r.get("id") for r in roots.get("roots", []) if isinstance(r, dict)]
    if folder_id not in root_ids:
        motivos.append(
            "folder_id ausente de config/drive_inventory_roots_20261016.json "
            "(escopo registered_roots_metadata_only)."
        )
    restrictions = roots.get("restrictions") or []
    if "NO_CANONICAL_PROMOTION" in restrictions and len(autorizam) != 1:
        motivos.append(
            "Contrato das raízes Drive impõe NO_CANONICAL_PROMOTION; "
            "atomização canônica sem política explícita é recusada."
        )
    if not credencial:
        motivos.append(
            "Nem GDRIVE_SA_KEY nem DRIVE_ACCESS_TOKEN estão configurados. Fail-closed."
        )
    authority_rel = roots.get("authority") or AUTHORITY_REL
    if not autoridade_presente:
        motivos.append(f"Autoridade declarada ausente no repositório: {authority_rel}")
    status = "BLOQUEADO" if motivos else "AUTORIZADO"
    return {
        "status": status,
        "decisao_kernel": "REJECTED" if motivos else "APPROVED_TO_EXECUTE",
        "exit_code": 2 if motivos else 0,
        "motivos": motivos,
        "politicas_autorizadoras": [p.get("id") for p in autorizam],
        "politica": autorizam[0] if len(autorizam) == 1 and not motivos else None,
    }


def _legacy_numeric_id(legacy_id: str, year: str) -> str:
    number = int(_sha256(legacy_id)[:12], 16)
    return f"NORM-{year}-{number}"


def _year_for(file_meta: dict, text: str) -> str | None:
    modified = str(file_meta.get("modifiedTime") or "")
    match = YEAR_RE.search(modified)
    if match:
        return match.group(0)
    name_years = YEAR_RE.findall(str(file_meta.get("name") or ""))
    if len(name_years) == 1:
        return name_years[0]
    text_years = YEAR_RE.findall(text)
    if len(set(text_years)) == 1:
        return text_years[0]
    return None


def _validators():
    if str(_CLI) not in sys.path:
        sys.path.insert(0, str(_CLI))
    from validators.sha256_validator import (  # noqa: WPS433
        AtomoSchemaValidator,
        NormAtomIdValidator,
        Sha256Validator,
        TextoLengthValidator,
        UrlValidator,
    )
    from packages.schemas.invariantes import AtomoBlindado

    return [
        AtomoSchemaValidator(),
        NormAtomIdValidator(),
        TextoLengthValidator(),
        UrlValidator(),
        Sha256Validator(),
    ], AtomoBlindado


def _mask(text: str) -> str:
    from packages.cli.utils import aplicar_mascara

    return aplicar_mascara(text)


def atomizar_arquivo(
    file_meta: dict,
    raw: bytes,
    policy: dict,
    wo_id: str,
    root: Path,
) -> dict:
    """Aplica máscara, invariantes e a política. Não publica vigência."""
    validators, atomo_model = _validators()
    wanted = list(policy.get("validators") or [])
    by_name = {v.name: v for v in validators}
    missing = [name for name in wanted if name not in by_name]
    if missing:
        raise RuntimeError(f"Validador referenciado e não implementado: {missing}")

    fonte_slug = None
    source_rel = policy.get("source_contract")
    if isinstance(source_rel, str):
        source_path = root / source_rel
        if source_path.is_file():
            fonte_slug = _read_json(source_path).get("fonte_slug")

    quarentena_dir = root / policy["quarentena_output"]
    atoms_dir = root / policy["atoms_output"]
    quarentena_dir.mkdir(parents=True, exist_ok=True)
    atoms_dir.mkdir(parents=True, exist_ok=True)
    quarantine_path = quarentena_dir / "rejeicoes.jsonl"

    mime = file_meta.get("mimeType") or ""
    file_id = file_meta["id"]
    summary = {"aceitos": 0, "quarentena": 0, "ignorados": 0}
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = None

    def reject(motivo: str, texto: str, extra: dict | None = None) -> None:
        record = {
            "motivo": motivo,
            "file_id": file_id,
            "wo_id": wo_id,
            "sha256": _sha256(texto) if texto else None,
            "texto_integral": texto,
            "policy_id": policy["id"],
        }
        if extra:
            record.update(extra)
        with quarantine_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        summary["quarentena"] += 1

    if mime not in TEXT_MIMES:
        reject("formato_sem_parser", "", {"mime": mime, "name": file_meta.get("name")})
        return summary
    if text is None:
        reject("utf8_invalido", "", {"mime": mime, "name": file_meta.get("name")})
        return summary

    year = _year_for(file_meta, text)
    masked = _mask(text)
    lines = [line.strip() for line in masked.splitlines()]
    produced = False
    for index, line in enumerate(lines):
        if not LEGAL_MARK.search(line):
            summary["ignorados"] += 1
            continue
        produced = True
        if any(term in line.lower() for term in OPINION):
            reject("termo_opinativo", line, {"linha": index})
            continue
        if len(line) < 10 or len(line) > 800:
            reject("texto_fora_contrato", line, {"linha": index, "tamanho": len(line)})
            continue
        if year is None:
            reject("ano_indeterminado", line, {"linha": index})
            continue
        legacy = f"{file_id}:{index}:{_sha256(line)}"
        atom = {
            "id_atomo": _legacy_numeric_id(legacy, year),
            "versao_contrato": "1.2.0",
            "fonte_slug": fonte_slug,
            "texto_regra": line,
            "idioma": "pt-BR",
            "sha256_texto": _sha256(line),
            "hash_status": "CONFERIDO",
            "vigencia": "NAO_VERIFICADO",
            "wo_id": wo_id,
        }
        errors = []
        for name in wanted:
            ok, err = by_name[name].validate(atom)
            if not ok:
                errors.append(f"{name}: {err}")
        if errors:
            reject("validador", line, {"erros": errors, "linha": index})
            continue
        try:
            atomo_model(**atom)
        except Exception as exc:  # noqa: BLE001 — fail-closed por item
            reject("acima_contrato", line, {"erro": str(exc), "linha": index})
            continue
        destination = atoms_dir / f"{atom['id_atomo']}.json"
        if destination.exists():
            previous = _read_json(destination)
            if previous.get("sha256_texto") != atom["sha256_texto"]:
                reject("conflito_duplicata", line, {"id_atomo": atom["id_atomo"], "linha": index})
                continue
            summary["aceitos"] += 1
            continue
        _write_json(destination, atom)
        summary["aceitos"] += 1
    if not produced and mime in TEXT_MIMES:
        reject("sem_dispositivo_legal", masked[:8000], {"name": file_meta.get("name")})
    return summary


def _default_list(folder_id: str, get_token: Callable[[], str]) -> list[dict]:
    from packages.cli.drive_recursive_inventory import list_page

    queue = [folder_id]
    seen = set()
    files: list[dict] = []
    while queue:
        current = queue.pop(0)
        if current in seen:
            continue
        seen.add(current)
        if len(seen) > MAX_FOLDERS:
            raise RuntimeError("folder limit exceeded")
        page_token = None
        while True:
            page = list_page(current, get_token, page_token)
            for item in page.get("files", []):
                if item.get("mimeType") == FOLDER_MIME:
                    queue.append(item["id"])
                else:
                    files.append(item)
                    if len(files) > MAX_FILES:
                        raise RuntimeError("item limit exceeded")
            page_token = page.get("nextPageToken")
            if not page_token:
                break
    return files


def _default_download(file_meta: dict, get_token: Callable[[], str]) -> bytes:
    file_id = file_meta["id"]
    if not FOLDER_ID_RE.fullmatch(file_id):
        raise ValueError("file id recusado")
    params = urlencode({"alt": "media", "supportsAllDrives": "true"})
    request = Request(
        f"https://www.googleapis.com/drive/v3/files/{file_id}?{params}",
        headers={"Authorization": "Bearer " + get_token(), "Accept": "*/*"},
    )
    with urlopen(request, timeout=60) as response:
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise RuntimeError("arquivo acima do limite de 20 MB")
    return data


def _token_getter(env: dict[str, str]):
    from packages.cli.drive_recursive_inventory import CredentialError, load_token

    previous = {key: os.environ.get(key) for key in ("GDRIVE_SA_KEY", "DRIVE_ACCESS_TOKEN")}
    try:
        for key in previous:
            if key in env and env[key]:
                os.environ[key] = env[key]
            elif key in os.environ and env is not os.environ:
                os.environ.pop(key, None)
        try:
            return load_token(), None
        except CredentialError as exc:
            return None, str(exc)
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def montar_wo(
    folder_id: str,
    tarefas: list[str],
    avaliacao: dict,
    policies: list[dict],
    roots: dict,
    execucao: dict,
    autoridade_presente: bool,
) -> dict:
    wo_id = wo_id_for(folder_id)
    return {
        "schema": "CE-WO-AUTHORIZATION-1.0.0",
        "wo_id": wo_id,
        "slug": f"drive_{folder_id}",
        "status": avaliacao["status"] if avaliacao["status"] == "BLOQUEADO" else execucao.get("status", avaliacao["status"]),
        "tarefa": tarefas,
        "alvo": {"tipo": "google_drive_folder", "folder_id": folder_id},
        "submetida_por": "kernel",
        "decisao_kernel": execucao.get("decisao_kernel", avaliacao["decisao_kernel"]),
        "exit_code": execucao.get("exit_code", avaliacao["exit_code"]),
        "motivos": execucao.get("motivos", avaliacao["motivos"]),
        "politicas_consultadas": [p["id"] for p in policies],
        "politicas_autorizadoras": avaliacao["politicas_autorizadoras"],
        "raizes_drive_registradas": [r.get("id") for r in roots.get("roots", [])],
        "autoridade_raizes": roots.get("authority") or AUTHORITY_REL,
        "autoridade_raizes_presente": autoridade_presente,
        "credencial": "PRESENTE" if execucao.get("credencial") else "AUSENTE",
        "restricoes": roots.get("restrictions") or [],
        "bytes_baixados": execucao.get("bytes_baixados", 0),
        "atomos_escritos": execucao.get("atomos_escritos", 0),
        "quarentena": execucao.get("quarentena", 0),
        "evidence_reference": f"data/grc/evidencias/{wo_id}.json",
        "conditions": [
            "WO submetida pelo Kernel antes de qualquer leitura de bytes.",
            "Sem drive_folder_ids na política, nenhum download ocorre.",
            "Vigência permanece NAO_VERIFICADO. Publicação não é efetuada.",
        ],
    }


def executar(
    folder_id: str,
    root: Path | None = None,
    tarefas: tuple[str, ...] = ("obter", "atomizar"),
    env: dict[str, str] | None = None,
    list_children: Callable[[str], list[dict]] | None = None,
    download: Callable[[dict], bytes] | None = None,
) -> dict:
    root = Path(root or _REPO)
    env = os.environ if env is None else env
    policies = load_policies(root)
    roots = load_roots(root)
    credencial = credencial_presente(env)
    authority_rel = roots.get("authority") or AUTHORITY_REL
    autoridade_presente = (root / authority_rel).is_file()
    avaliacao = avaliar(folder_id, policies, roots, credencial, autoridade_presente)
    wo_id = wo_id_for(folder_id)
    execucao: dict[str, Any] = {
        "credencial": credencial,
        "bytes_baixados": 0,
        "atomos_escritos": 0,
        "quarentena": 0,
        "arquivos": [],
        "motivos": list(avaliacao["motivos"]),
        "decisao_kernel": avaliacao["decisao_kernel"],
        "exit_code": avaliacao["exit_code"],
        "status": avaliacao["status"],
    }
    if avaliacao["status"] == "AUTORIZADO":
        policy = avaliacao["politica"]
        if not isinstance(policy, dict):
            raise RuntimeError("Política autorizadora ausente após aprovação. Fail-closed.")
        try:
            if list_children is None or download is None:
                getter, err = _token_getter(env)
                if getter is None:
                    raise RuntimeError(err or "credencial indisponível")
                list_children = lambda folder, _getter=getter: _default_list(folder, _getter)  # noqa: E731
                download = lambda meta, _getter=getter: _default_download(meta, _getter)  # noqa: E731
            files = list_children(folder_id)
            for meta in files:
                size = int(meta.get("size") or 0)
                if size > MAX_BYTES:
                    execucao["quarentena"] += 1
                    execucao["arquivos"].append({"id": meta.get("id"), "motivo": "acima_limite"})
                    continue
                payload = download(meta)
                execucao["bytes_baixados"] += len(payload)
                summary = atomizar_arquivo(meta, payload, policy, wo_id, root)
                execucao["atomos_escritos"] += summary["aceitos"]
                execucao["quarentena"] += summary["quarentena"]
                execucao["arquivos"].append({"id": meta.get("id"), "name": meta.get("name"), **summary})
            if policy.get("requires_human_review"):
                execucao["status"] = "PENDENTE_REVISAO_HUMANA"
                execucao["decisao_kernel"] = "PENDING_HUMAN_REVIEW"
            elif execucao["quarentena"]:
                execucao["status"] = "CONCLUIDO_COM_QUARENTENA"
                execucao["decisao_kernel"] = "QUARANTINE"
            else:
                execucao["status"] = "CONCLUIDO"
                execucao["decisao_kernel"] = "EXECUTED"
            execucao["exit_code"] = 0
            execucao["motivos"] = []
        except Exception as exc:  # noqa: BLE001 — falha operacional vira WO bloqueada
            execucao["status"] = "BLOQUEADO"
            execucao["decisao_kernel"] = "REJECTED"
            execucao["exit_code"] = 2
            execucao["motivos"] = [f"Falha operacional após autorização: {type(exc).__name__}: {exc}"]
    wo = montar_wo(
        folder_id, list(tarefas), avaliacao, policies, roots, execucao, autoridade_presente
    )
    evidence = {
        "schema": "CE-KERNEL-DRIVE-ACTIVITY-1.0.0",
        "wo_id": wo_id,
        "submetida_por": "kernel",
        "avaliacao": {k: v for k, v in avaliacao.items() if k != "politica"},
        "execucao": execucao,
    }
    wo_path = root / "data" / "legado" / f"autorizacao_{wo_id}.json"
    evidence_path = root / "data" / "grc" / "evidencias" / f"{wo_id}.json"
    _write_json(wo_path, wo)
    _write_json(evidence_path, evidence)
    return wo


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kernel: WO, obter e atomizar uma pasta Drive.")
    parser.add_argument("--folder", required=True)
    parser.add_argument("--root", type=Path, default=_REPO)
    parser.add_argument("--tarefas", default="obter,atomizar")
    args = parser.parse_args(argv)
    tarefas = tuple(part.strip() for part in args.tarefas.split(",") if part.strip())
    wo = executar(args.folder, root=args.root, tarefas=tarefas)
    print(json.dumps({"wo_id": wo["wo_id"], "status": wo["status"], "exit_code": wo["exit_code"], "motivos": wo["motivos"]}, ensure_ascii=False, indent=2))
    return int(wo["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
