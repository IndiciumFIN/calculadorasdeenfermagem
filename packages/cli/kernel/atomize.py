"""Atomização de texto já obtido, somente com WO submetida pelo Kernel.

A classificação usa só o nome do arquivo e tokens únicos das políticas.
Texto que não casa com uma política validada não entra no corpus.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from packages.schemas.invariantes import AtomoBlindado

from kernel.core import VALIDATORS, Decision, Kernel, _ensure_validators
from kernel.policy_registry import KernelPolicy, get_policy
from kernel.work_orders import WorkOrderRejected, repo_root, require_open

try:
    from utils import aplicar_mascara, calcular_hash
except ImportError:  # pragma: no cover
    from packages.cli.utils import aplicar_mascara, calcular_hash

_LEGAL_MARKERS = ("art.", "artigo", "§", "inciso", "parágrafo", "paragrafo")
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
_STOP = frozenset(
    {
        "normativo",
        "federal",
        "classificacao",
        "brasil",
        "saude",
        "dados",
        "publico",
        "publica",
    }
)


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return decomposed.encode("ascii", "ignore").decode().lower()


def _source_payload(policy: KernelPolicy) -> dict[str, Any]:
    path = Path(policy.source_contract)
    if not path.is_absolute():
        path = repo_root() / path
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    return data


def build_needles(policies: list[KernelPolicy]) -> dict[str, str]:
    """Devolve agulha → policy_id. Agulha compartilhada é descartada."""
    owners: dict[str, set[str]] = {}

    def add(needle: str, policy_id: str) -> None:
        folded = _fold(needle).strip()
        if len(folded) < 4:
            return
        owners.setdefault(folded, set()).add(policy_id)

    for policy in policies:
        source = _source_payload(policy)
        slug = str(source.get("fonte_slug") or "")
        add(slug, policy.id)
        add(slug.replace("_", " "), policy.id)
        add(slug.replace("_", "-"), policy.id)
        add(policy.name, policy.id)
        add(policy.id, policy.id)
        for token in re.split(r"[^a-z0-9]+", _fold(f"{policy.name} {source.get('fonte_oficial') or ''}")):
            if len(token) < 4 or token in _STOP:
                continue
            add(token, policy.id)
            if len(token) > 5 and token.endswith("s"):
                add(token[:-1], policy.id)

    return {needle: next(iter(ids)) for needle, ids in owners.items() if len(ids) == 1}


def classify_name(
    name: str, needles: dict[str, str], valid_ids: set[str]
) -> tuple[str | None, str]:
    """Classifica pelo nome. Não lê o corpo do arquivo."""
    hay = _fold(name)
    raw = name.lower()
    hits = {
        policy_id
        for needle, policy_id in needles.items()
        if needle in hay or needle in raw
    }
    if not hits:
        return None, "UNMATCHED_POLICY"
    if len(hits) > 1:
        return None, "POLICY_AMBIGUOUS"
    policy_id = next(iter(hits))
    if policy_id not in valid_ids:
        return None, "POLICY_NOT_VALID"
    return policy_id, "MATCHED"


def _normalizar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()


def _official_url(text: str) -> str | None:
    _ensure_validators()
    validator = VALIDATORS.get("url_validator")
    if validator is None:
        return None
    for match in re.findall(r"https://[^\s<>\"]+", text):
        candidate = match.rstrip(").,;")
        ok, _error = validator.validate({"link_fonte": candidate})
        if ok:
            return candidate
    return None


def _line_disposition(line: str) -> str | None:
    lowered = line.lower()
    if not any(marker in lowered or (marker == "§" and marker in line) for marker in _LEGAL_MARKERS):
        return "sem_dispositivo"
    if any(term in lowered for term in _OPINION):
        return "termo_opinativo"
    if len(line) < 10:
        return "texto_curto"
    if len(line) > 800:
        return "acima_contrato"
    return None


def _atom_id(policy_id: str, file_id: str, texto: str) -> str:
    digest = hashlib.sha256(f"{policy_id}|{file_id}|{texto}".encode("utf-8")).hexdigest()
    year = datetime.now(timezone.utc).year
    return f"NORM-{year}-{int(digest[:12], 16)}"


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def atomize_documents(
    kernel: Kernel,
    policy_id: str,
    wo: dict[str, Any],
    documents: list[dict[str, str]],
    dest_root: Path,
) -> dict[str, Any]:
    """Atomiza documentos já classificados. Recusa WO ausente ou fechada."""
    require_open(wo, policy_id, "atomizar")
    policy = get_policy(policy_id)
    if kernel.gate(policy_id) != 0:
        raise WorkOrderRejected(f"Política {policy_id} não está validada pelo Kernel.")

    source = _source_payload(policy)
    slug = str(source.get("fonte_slug") or "")
    atoms_dir = dest_root / policy.atoms_output
    quarantine_dir = dest_root / (policy.quarentena_output or f"data/quarentena/{slug or policy_id}")
    quarantine_file = quarantine_dir / f"{wo['wo_id']}.jsonl"
    atoms_dir.mkdir(parents=True, exist_ok=True)

    written = 0
    quarantined = 0
    ignored = 0
    for document in documents:
        masked = aplicar_mascara(document.get("text") or "")
        link = _official_url(masked)
        file_id = document.get("id") or document.get("name") or "sem-id"
        for raw_line in masked.splitlines():
            line = _normalizar(raw_line)
            if not line:
                continue
            motivo = _line_disposition(line)
            if motivo == "sem_dispositivo":
                ignored += 1
                continue
            if motivo:
                _append_jsonl(
                    quarantine_file,
                    {
                        "motivo": motivo,
                        "texto": line,
                        "policy_id": policy_id,
                        "wo_id": wo["wo_id"],
                        "origem": document.get("name") or file_id,
                    },
                )
                quarantined += 1
                continue

            atom = {
                "id_atomo": _atom_id(policy_id, file_id, line),
                "versao_contrato": "1.2.0",
                "fonte_slug": slug or None,
                "texto_regra": line,
                "dispositivo_legal": line[:100],
                "link_fonte": link,
                "idioma": "pt-BR",
                "sha256_texto": calcular_hash(line),
                "sha256_original": calcular_hash(line),
                "hash_status": "CONFERIDO",
                "vigencia": "NAO_VERIFICADO",
                "data_verificacao": datetime.now(timezone.utc).date().isoformat(),
                "wo_id": wo["wo_id"],
            }
            decision = kernel.evaluate(atom, policy_id)
            if decision.decision != Decision.APPROVED:
                _append_jsonl(
                    quarantine_file,
                    {
                        "motivo": "rejeitado_pelo_kernel",
                        "texto": line,
                        "policy_id": policy_id,
                        "wo_id": wo["wo_id"],
                        "origem": document.get("name") or file_id,
                        "erros": decision.errors
                        or [r.error for r in decision.results if r.error],
                    },
                )
                quarantined += 1
                continue
            try:
                AtomoBlindado.model_validate(atom)
            except Exception as exc:
                _append_jsonl(
                    quarantine_file,
                    {
                        "motivo": "acima_contrato",
                        "texto": line,
                        "policy_id": policy_id,
                        "wo_id": wo["wo_id"],
                        "origem": document.get("name") or file_id,
                        "erros": [str(exc)],
                    },
                )
                quarantined += 1
                continue
            target = atoms_dir / f"{atom['id_atomo']}.json"
            if target.exists():
                current = json.loads(target.read_text(encoding="utf-8"))
                if current.get("sha256_texto") != atom["sha256_texto"]:
                    _append_jsonl(
                        quarantine_file,
                        {
                            "motivo": "conflito_duplicata",
                            "texto": line,
                            "policy_id": policy_id,
                            "wo_id": wo["wo_id"],
                            "origem": document.get("name") or file_id,
                            "id_atomo": atom["id_atomo"],
                        },
                    )
                    quarantined += 1
                continue
            target.write_text(
                json.dumps(atom, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            written += 1

    return {
        "policy_id": policy_id,
        "wo_id": wo["wo_id"],
        "atoms_written": written,
        "quarantined": quarantined,
        "ignored_lines": ignored,
    }
