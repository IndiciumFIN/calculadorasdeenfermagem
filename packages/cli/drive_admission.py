"""Admissão de pasta Drive pelo Kernel.

Toda atividade (obter, atomizar) recebe uma WO submetida pelo Kernel.
Sem raiz registrada, credencial, política aderente e texto sanitizado,
o Kernel bloqueia (exit 2). Não baixa bytes, não publica e não promove
átomo a canônico.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

FOLDER_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,128}$")
ACTIVITIES = ("obter", "atomizar")
SCHEMA = "CE-WO-AUTHORIZATION-1.0.0"
EVIDENCE_SCHEMA = "CE-DRIVE-ADMISSION-1.0.0"
ROOTS_REL = "config/drive_inventory_roots_20261016.json"
URL_VALIDATOR_REL = "packages/cli/validators/sha256_validator.py"


class RedirectCaptured(Exception):
    def __init__(self, code: int, host: str | None) -> None:
        self.code = code
        self.host = host
        super().__init__(f"{code} {host}")


class _CaptureRedirect(HTTPRedirectHandler):
    """Registra o primeiro redirect e não o segue."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ARG002
        host = urlparse(newurl).hostname if newurl else None
        raise RedirectCaptured(code, host)


@dataclass
class Admission:
    exit_code: int
    evidence: dict[str, Any]
    work_orders: list[dict[str, Any]]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def official_url_domains(root: Path) -> set[str]:
    """Domínios da allowlist do url_validator, lidos do código versionado."""
    text = (root / URL_VALIDATOR_REL).read_text(encoding="utf-8")
    match = re.search(r"ALLOWED_DOMAINS = frozenset\(\{(.*?)\}\)", text, re.S)
    if not match:
        raise RuntimeError("url_validator allowlist ausente; fail-closed")
    return set(re.findall(r'"([^"]+)"', match.group(1)))


def load_policies(root: Path) -> list[dict[str, Any]]:
    directory = root / "contracts" / "policies"
    if not directory.is_dir():
        raise FileNotFoundError("contracts/policies ausente; fail-closed")
    policies: list[dict[str, Any]] = []
    for path in sorted(directory.glob("KERNEL-POLICY-*.json")):
        data = _read_json(path)
        if not isinstance(data, dict) or not data.get("id") or not data.get("validators"):
            raise ValueError(f"política inválida: {path.name}")
        policies.append(data)
    if not policies:
        raise ValueError("nenhuma política KERNEL-POLICY registrada; fail-closed")
    return policies


def load_roots(root: Path) -> dict[str, Any]:
    path = root / ROOTS_REL
    if not path.is_file():
        raise FileNotFoundError(f"{ROOTS_REL} ausente; fail-closed")
    data = _read_json(path)
    roots = data.get("roots")
    if not isinstance(roots, list) or not roots:
        raise ValueError("raízes Drive vazias; fail-closed")
    return data


def _domain_allowed(host: str, domains: set[str]) -> bool:
    host = host.lower()
    return any(host == domain or host.endswith("." + domain) for domain in domains)


def evaluate_policies(
    policies: list[dict[str, Any]],
    *,
    folder_id: str,
    folder_url: str,
    domains: set[str],
    root: Path,
) -> list[dict[str, Any]]:
    host = urlparse(folder_url).hostname or ""
    results: list[dict[str, Any]] = []
    for policy in policies:
        reasons: list[str] = []
        validators = policy.get("validators") or []
        if "url_validator" in validators and not _domain_allowed(host, domains):
            reasons.append("URL_DOMAIN_NOT_ALLOWED")
        source_rel = policy.get("source_contract")
        source_text = ""
        if isinstance(source_rel, str):
            source_path = root / source_rel
            if source_path.is_file():
                source_text = source_path.read_text(encoding="utf-8")
            else:
                reasons.append("POLICY_SOURCE_MISSING")
        if folder_id not in source_text and folder_url not in source_text:
            reasons.append("SOURCE_CONTRACT_NOT_THIS_FOLDER")
        results.append(
            {
                "policy_id": policy.get("id"),
                "wo_required": bool(policy.get("wo_required")),
                "admitted": not reasons,
                "reasons": reasons,
            }
        )
    return results


def probe_drive(folder_id: str, timeout: float = 20.0) -> dict[str, Any]:
    """Consulta a pasta sem seguir login e sem registrar corpo nem cookie."""
    page_url = f"https://drive.google.com/drive/folders/{folder_id}?hl=pt-br"
    api_url = (
        "https://www.googleapis.com/drive/v3/files/"
        f"{folder_id}?fields=id,name,mimeType&supportsAllDrives=true"
    )
    probe: dict[str, Any] = {
        "folder_http_status": None,
        "folder_redirect_host": None,
        "api_http_status": None,
        "api_status": None,
    }
    opener = build_opener(_CaptureRedirect())
    request = Request(page_url, headers={"Accept": "text/html", "User-Agent": "CE-Kernel/1.0"})
    try:
        with opener.open(request, timeout=timeout) as response:
            probe["folder_http_status"] = getattr(response, "status", None)
    except RedirectCaptured as captured:
        probe["folder_http_status"] = captured.code
        probe["folder_redirect_host"] = captured.host
    except HTTPError as exc:
        probe["folder_http_status"] = exc.code
    except URLError:
        probe["folder_error"] = "URLError"
    except Exception:
        probe["folder_error"] = "ProbeError"

    api_request = Request(api_url, headers={"Accept": "application/json", "User-Agent": "CE-Kernel/1.0"})
    try:
        with build_opener().open(api_request, timeout=timeout) as response:
            probe["api_http_status"] = getattr(response, "status", None)
    except HTTPError as exc:
        probe["api_http_status"] = exc.code
        try:
            payload = json.loads(exc.read().decode("utf-8", errors="replace"))
            error = payload.get("error") if isinstance(payload, dict) else None
            if isinstance(error, dict):
                probe["api_status"] = error.get("status")
        except (OSError, ValueError):
            probe["api_status"] = None
    except URLError:
        probe["api_error"] = "URLError"
    except Exception:
        probe["api_error"] = "ProbeError"
    return probe


def _credential_flags(env: Mapping[str, str]) -> dict[str, bool]:
    return {
        "gdrive_sa_key": bool(env.get("GDRIVE_SA_KEY")),
        "drive_access_token": bool(env.get("DRIVE_ACCESS_TOKEN")),
    }


def _previous_attempt(path: Path) -> int:
    if not path.is_file():
        return 0
    try:
        data = _read_json(path)
    except (OSError, ValueError):
        return 0
    count = data.get("attempt_count")
    return count if isinstance(count, int) and count >= 0 else 0


def _first_submitted(path: Path, now: str) -> str:
    if not path.is_file():
        return now
    try:
        data = _read_json(path)
    except (OSError, ValueError):
        return now
    first = data.get("first_submitted_at")
    return first if isinstance(first, str) and first else now


def admit_drive_folder(
    folder_id: str,
    *,
    root: Path,
    env: Mapping[str, str],
    probe: dict[str, Any],
    now: datetime | None = None,
) -> Admission:
    moment = now or datetime.now(timezone.utc)
    timestamp = moment.strftime("%Y-%m-%dT%H:%M:%SZ")
    folder_url = f"https://drive.google.com/drive/folders/{folder_id}?hl=pt-br"
    evidence_rel = f"evidence/CE-WO-DRIVE-{folder_id}/admission.json"
    evidence_path = root / evidence_rel
    attempt = _previous_attempt(evidence_path) + 1
    first_at = _first_submitted(evidence_path, timestamp)

    motivos: list[str] = []
    gates: dict[str, bool] = {
        "folder_id_syntax": bool(FOLDER_ID_RE.fullmatch(folder_id)),
        "registered_root": False,
        "credential_present": False,
        "drive_identity_established": False,
        "matching_policy": False,
        "canonical_promotion_allowed": False,
        "bytes_acquired": False,
    }
    roots_doc: dict[str, Any] | None = None
    policy_results: list[dict[str, Any]] = []
    restrictions = ["READ_ONLY", "NO_DELETE", "NO_PUBLICATION", "NO_CANONICAL_PROMOTION"]

    if not gates["folder_id_syntax"]:
        motivos.append("INVALID_FOLDER_ID")
    else:
        try:
            roots_doc = load_roots(root)
        except (OSError, ValueError, FileNotFoundError):
            motivos.append("ROOTS_CONFIG_INVALID")
        else:
            restrictions = list(roots_doc.get("restrictions") or restrictions)
            registered = {item.get("id") for item in roots_doc.get("roots", []) if isinstance(item, dict)}
            gates["registered_root"] = folder_id in registered
            if not gates["registered_root"]:
                motivos.append("UNREGISTERED_ROOT")
            if roots_doc.get("scope") == "registered_roots_metadata_only":
                motivos.append("METADATA_ONLY_SCOPE")
            if "NO_CANONICAL_PROMOTION" in restrictions:
                motivos.append("NO_CANONICAL_PROMOTION")
            else:
                gates["canonical_promotion_allowed"] = True

        flags = _credential_flags(env)
        gates["credential_present"] = flags["gdrive_sa_key"] or flags["drive_access_token"]
        if not gates["credential_present"]:
            motivos.append("MISSING_CREDENTIAL")

        redirect_host = probe.get("folder_redirect_host")
        folder_status = probe.get("folder_http_status")
        api_status = probe.get("api_http_status")
        login_wall = redirect_host == "accounts.google.com" or folder_status in {401, 403}
        api_forbidden = api_status in {401, 403} or probe.get("api_status") in {"PERMISSION_DENIED", "UNAUTHENTICATED"}
        gates["drive_identity_established"] = (
            gates["credential_present"] and not login_wall and not api_forbidden and folder_status == 200
        )
        if login_wall:
            motivos.append("DRIVE_LOGIN_REQUIRED")
        if api_forbidden or probe.get("api_error"):
            motivos.append("DRIVE_API_FORBIDDEN")

        try:
            policies = load_policies(root)
            domains = official_url_domains(root)
        except (OSError, ValueError, RuntimeError, FileNotFoundError):
            motivos.append("POLICY_REGISTRY_INVALID")
        else:
            policy_results = evaluate_policies(
                policies,
                folder_id=folder_id,
                folder_url=folder_url,
                domains=domains,
                root=root,
            )
            gates["matching_policy"] = any(item["admitted"] for item in policy_results)
            if not gates["matching_policy"]:
                motivos.append("NO_MATCHING_POLICY")

    if not any(code != "ATOMIC_SOURCE_ABSENT" for code in motivos):
        motivos.append("DOWNLOAD_NOT_IMPLEMENTED")
    motivos.append("ATOMIC_SOURCE_ABSENT")

    # Ordem estável, sem duplicar.
    ordered: list[str] = []
    for code in motivos:
        if code not in ordered:
            ordered.append(code)
    motivos = ordered

    def wo_for(activity: str) -> dict[str, Any]:
        activity_motivos = (
            [code for code in motivos if code != "ATOMIC_SOURCE_ABSENT"]
            if activity == "obter"
            else motivos
        )
        if activity == "obter":
            detail = (
                "Kernel bloqueou a obtenção. "
                f"Pasta {folder_id} avaliada contra {ROOTS_REL} e as KERNEL-POLICY registradas. "
                "Nenhum byte foi baixado."
            )
        else:
            detail = (
                "Kernel bloqueou a atomização. "
                "Não há texto sanitizado porque a obtenção não produziu arquivo, "
                "e nenhuma política admite esta pasta como fonte."
            )
        return {
            "schema": SCHEMA,
            "wo_id": f"CE-WO-DRIVE-{activity.upper()}-{folder_id}",
            "slug": f"drive_folder_{folder_id}_{activity}",
            "status": "BLOQUEADO",
            "tarefa": activity,
            "submitted_by": "kernel",
            "authorized_by": None,
            "policy_id": None,
            "folder_id": folder_id,
            "folder_url": folder_url,
            "motivos": activity_motivos,
            "motivo": detail + " Motivos: " + ", ".join(activity_motivos) + ".",
            "timestamp": timestamp,
            "first_submitted_at": first_at,
            "tentativas": attempt,
            "conditions": restrictions,
            "bytes_acquired": False,
            "atoms_written": 0,
            "canonical_promoted": False,
            "exit_code": 2,
            "evidence_reference": evidence_rel,
        }

    work_orders = [wo_for(activity) for activity in ACTIVITIES]
    evidence = {
        "schema": EVIDENCE_SCHEMA,
        "folder_id": folder_id,
        "folder_url": folder_url,
        "decision": "BLOQUEADO",
        "exit_code": 2,
        "submitted_by": "kernel",
        "motivos": motivos,
        "attempt_count": attempt,
        "first_submitted_at": first_at,
        "last_submitted_at": timestamp,
        "gates": gates,
        "credentials": _credential_flags(env),
        "probe": probe,
        "policies": policy_results,
        "work_orders": [item["wo_id"] for item in work_orders],
        "bytes_acquired": False,
        "atoms_written": 0,
        "canonical_promoted": False,
        "restrictions": restrictions,
    }
    return Admission(exit_code=2, evidence=evidence, work_orders=work_orders)


def write_admission(root: Path, admission: Admission) -> list[Path]:
    """Persiste as WOs e a evidência. Não cria átomo canônico."""
    written: list[Path] = []
    for order in admission.work_orders:
        suffix = order["wo_id"].removeprefix("CE-WO-")
        path = root / "data" / "legado" / f"autorizacao_WO-{suffix}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        _atomic_write(path, order)
        written.append(path)
    evidence_rel = admission.work_orders[0]["evidence_reference"]
    evidence_path = root / evidence_rel
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(evidence_path, admission.evidence)
    written.append(evidence_path)
    return written


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def run(folder_id: str, root: Path | None = None, env: Mapping[str, str] | None = None) -> int:
    import os

    base = root or repo_root()
    environment = env if env is not None else os.environ
    if not FOLDER_ID_RE.fullmatch(folder_id):
        probe: dict[str, Any] = {}
    else:
        probe = probe_drive(folder_id)
    admission = admit_drive_folder(folder_id, root=base, env=environment, probe=probe)
    paths = write_admission(base, admission)
    print(f"KERNEL BLOQUEADO exit={admission.exit_code} wo={len(admission.work_orders)}")
    for path in paths:
        print(path.relative_to(base).as_posix())
    return admission.exit_code


def main() -> int:
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Kernel submete WO e admite pasta Drive (fail-closed).")
    parser.add_argument("--folder", required=True, help="ID da pasta Google Drive")
    parser.add_argument("--root", type=Path, default=None, help="Raiz do repositório")
    args = parser.parse_args()
    return run(args.folder, root=args.root, env=os.environ)


if __name__ == "__main__":
    raise SystemExit(main())
