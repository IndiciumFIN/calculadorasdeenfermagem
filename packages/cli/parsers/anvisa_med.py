"""Anvisa medications registered-products CSV parser, local pinned snapshot only.

Reference: dados.anvisa.gov.br/dados/DADOS_ABERTOS_MEDICAMENTOS.csv
Source dictionary: Documentacao_e_Dicionario_de_Dados_Registros_Validos_Medicamento_V1.pdf
Only candidate identifiers and provenance, never product text or clinical advice.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re

SOURCE_CONTRACT = "contracts/fontes/anvisa_med.json"
PARSER_API_VERSION = "1.0.0"
SOURCE_URI = "https://dados.anvisa.gov.br/dados/DADOS_ABERTOS_MEDICAMENTOS.csv"
MAX_BYTES = 100_000_000
MAX_RECORDS = 500_000
HEADER = (
    "TIPO_PRODUTO", "NOME_PRODUTO", "DATA_FINALIZACAO_PROCESSO",
    "CATEGORIA_REGULATORIA", "NUMERO_REGISTRO_PRODUTO", "DATA_VENCIMENTO_REGISTRO",
    "NUMERO_PROCESSO", "CLASSE_TERAPEUTICA", "EMPRESA_DETENTORA_REGISTRO",
    "SITUACAO_REGISTRO", "PRINCIPIO_ATIVO",
)
SHA_RE = re.compile(r"[0-9a-f]{64}", re.ASCII)
MONTH_RE = re.compile(r"20[0-9]{2}-(0[1-9]|1[0-2])", re.ASCII)
PROCESS_RE = re.compile(r"[0-9./-]{7,40}", re.ASCII)
REG_RE = re.compile(r"[0-9]{9,20}", re.ASCII)


class ParseHold(ValueError):
    """Malformed, unverified or inconsistent Anvisa CSV snapshot."""


def _text(value, label: str, max_size: int = 5000, nullable: bool = False) -> str:
    if not isinstance(value, str):
        raise ParseHold(f"{label}: text expected")
    value = value.strip()
    if len(value) > max_size or (not nullable and not value):
        raise ParseHold(f"{label}: missing/oversized")
    if any(ord(ch) < 32 and ch not in "\t" for ch in value):
        raise ParseHold(f"{label}: invalid control")
    return value


def parse(raw: bytes | str, *, source_id: str, document_id: str,
          snapshot_month: str, expected_sha256: str) -> list[dict]:
    """Parse a pinned, complete CSV payload. No network, no release.

    Technical interpretation uses official column names. A SHA match proves
    byte identity, not that the file was really retrieved from Anvisa.
    Official rows can have null identifiers and exact duplicates, so they
    are retained in original order and occurrences are recorded, not dropped.
    """
    source_id = _text(source_id, "source_id", 256)
    document_id = _text(document_id, "document_id", 256)
    if not isinstance(snapshot_month, str) or not MONTH_RE.fullmatch(snapshot_month):
        raise ParseHold("snapshot_month must be YYYY-MM")
    if not isinstance(raw, (bytes, str)):
        raise ParseHold("CSV must be raw bytes or text")
    payload = raw.encode("cp1252") if isinstance(raw, str) else raw
    if not payload or len(payload) > MAX_BYTES or bytes([0]) in payload:
        raise ParseHold("CSV empty, oversized or binary")
    if not isinstance(expected_sha256, str) or not SHA_RE.fullmatch(expected_sha256):
        raise ParseHold("expected_sha256 must be a lowercase digest")
    digest = hashlib.sha256(payload).hexdigest()
    if digest != expected_sha256:
        raise ParseHold("pinned CSV SHA-256 mismatch")
    try:
        content = payload.decode("cp1252")
        rows = csv.reader(io.StringIO(content, newline=""), delimiter=";", quotechar='"', strict=True)
        header = next(rows)
        if tuple(header) != HEADER:
            raise ParseHold("Anvisa medicines CSV header differs from pinned dictionary")
        outputs = []
        seen = {}
        for row_number, cells in enumerate(rows, 2):
            if row_number > MAX_RECORDS + 1:
                raise ParseHold("CSV exceeds maximum row count")
            if len(cells) != len(HEADER):
                raise ParseHold(f"row {row_number}: field count mismatch")
            obj = dict(zip(HEADER, cells))
            if _text(obj["TIPO_PRODUTO"], "TIPO_PRODUTO", 100) != "MEDICAMENTO":
                raise ParseHold(f"row {row_number}: unexpected product type")
            _text(obj["NOME_PRODUTO"], "NOME_PRODUTO")
            process = _text(obj["NUMERO_PROCESSO"], "NUMERO_PROCESSO", 40)
            if not PROCESS_RE.fullmatch(process):
                raise ParseHold(f"row {row_number}: invalid process shape")
            registration = _text(obj["NUMERO_REGISTRO_PRODUTO"], "NUMERO_REGISTRO_PRODUTO", 20, nullable=True)
            if registration and not REG_RE.fullmatch(registration):
                raise ParseHold(f"row {row_number}: invalid product registration")
            # Null descriptive fields are supported by Anvisa's dictionary.
            for name in HEADER:
                _text(obj[name], name, 5000, nullable=name not in ("TIPO_PRODUTO", "NOME_PRODUTO", "NUMERO_PROCESSO"))
            # Only product/process identifiers appear in result. No active-status,
            # therapeutic indication, ingredient, company or date is interpreted.
            key = (registration, process)
            seen[key] = seen.get(key, 0) + 1
            atom = {
                "registration_number_candidate": registration or None,
                "process_number_candidate": process,
                "occurrence_index": seen[key],
            }
            record_sha = hashlib.sha256(json.dumps(
                atom, sort_keys=True, ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8")).hexdigest()
            outputs.append({
                **atom,
                "record_sha256": record_sha,
                "source_sha256": digest,
                "source_id": source_id,
                "document_id": document_id,
                "source_contract": SOURCE_CONTRACT,
                "parser": "anvisa_med",
                "parser_version": PARSER_API_VERSION,
                "official_source_uri": SOURCE_URI,
                "snapshot_month_declared": snapshot_month,
                "source_origin_verified": False,
                "record_registration_current_verified": False,
                "rights_verified": False,
                "status": "HOLD_HUMAN",
                "clinical_approved": False,
                "publication_allowed": False,
                "release_allowed": False,
            })
        if not outputs:
            raise ParseHold("CSV has header but no product rows")
        return outputs
    except (UnicodeError, csv.Error, StopIteration, ValueError) as exc:
        if isinstance(exc, ParseHold):
            raise
        raise ParseHold("CSV malformed or unsupported encoding") from exc
