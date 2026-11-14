"""ANVISA medical devices official open-data CSV: bounded metadata-only parser.

Official source: https://dados.anvisa.gov.br/dados/TA_PRODUTO_SAUDE_SITE.csv
Official data dictionary: Documentação_e_Dicionário_de_Dados_Produto_para_Saúde_V1.0.pdf
Duplicates by registration/fabricante are meaningful. No network, clinical
release, copied device names, recommendation or inferred active registration.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from typing import Any

SOURCE_CONTRACT = "contracts/fontes/anvisa_dev.json"
PARSER_API_VERSION = "1.0.0"
SOURCE_URI = "https://dados.anvisa.gov.br/dados/TA_PRODUTO_SAUDE_SITE.csv"
REQUIRED = frozenset({
    "NUMERO_REGISTRO_CADASTRO", "NUMERO_PROCESSO", "NOME_TECNICO",
    "CLASSE_RISCO", "NOME_COMERCIAL", "CNPJ_DETENTOR_REGISTRO_CADASTRO",
    "DETENTOR_REGISTRO_CADASTRO", "NOME_FABRICANTE",
    "NOME_PAIS_FABRIC", "DT_PUB_REGISTRO_CADASTRO",
    "VALIDADE_REGISTRO_CADASTRO",
})
OPTIONAL = frozenset({"DT_ATUALIZACAO_DADO"})
MAX_BYTES = 100_000_000
MAX_RECORDS = 200_000
SHA_RE = re.compile(r"[0-9a-f]{64}", re.ASCII)
REG_RE = re.compile(r"[0-9]{10,11}", re.ASCII)
PROC_RE = re.compile(r"[0-9./-]{6,24}", re.ASCII)
CNPJ_RE = re.compile(r"[0-9]{14}", re.ASCII)
RISK = frozenset({"I", "II", "III", "IV"})


class ParseHold(ValueError):
    """Unknown, malformed or unverified device snapshot: reject entire batch."""


def _text(x: Any, field: str, *, required: bool = True, max_len: int = 4096) -> str:
    if not isinstance(x, str) or len(x) > max_len:
        raise ParseHold(f"{field}: invalid text")
    v = x.strip()
    if required and not v:
        raise ParseHold(f"{field}: empty")
    if any(ord(c) < 32 for c in v):
        raise ParseHold(f"{field}: control character")
    return v


def parse(raw: bytes | str, *, source_id: str, document_id: str,
          captured_at: str, expected_sha256: str, encoding: str) -> list[dict]:
    """Parse one complete locally supplied CSV snapshot pinned by external manifest.

    Hash agreement proves byte equality only. Real product status and rights
    must be verified independently using Anvisa's live consultative channel.
    """
    source_id = _text(source_id, "source_id", max_len=256)
    document_id = _text(document_id, "document_id", max_len=256)
    captured_at = _text(captured_at, "captured_at", max_len=35)
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
        if dt.utcoffset() is None:
            raise ValueError("timezone required")
    except ValueError as exc:
        raise ParseHold("captured_at must have a timezone") from exc
    if encoding not in ("cp1252", "utf-8-sig"):
        raise ParseHold("explicit cp1252 or utf-8-sig encoding required")
    if not isinstance(raw, (bytes, str)):
        raise ParseHold("CSV input must be bytes or str")
    try:
        payload = raw.encode(encoding) if isinstance(raw, str) else raw
    except UnicodeError as exc:
        raise ParseHold("text could not be encoded as declared") from exc
    if not payload or len(payload) > MAX_BYTES or bytes([0]) in payload:
        raise ParseHold("Anvisa device source empty/oversized/binary")
    if not isinstance(expected_sha256, str) or not SHA_RE.fullmatch(expected_sha256):
        raise ParseHold("expected_sha256 must be canonical lowercase hex")
    digest = hashlib.sha256(payload).hexdigest()
    if digest != expected_sha256:
        raise ParseHold("Anvisa device snapshot SHA-256 mismatch")
    try:
        rows = csv.DictReader(io.StringIO(payload.decode(encoding), newline=""),
                              delimiter=";", strict=True)
        fields = rows.fieldnames
        if (not isinstance(fields, list)
                or len(fields) != len(set(fields))
                or not REQUIRED.issubset(fields)
                or set(fields).difference(REQUIRED | OPTIONAL)):
            raise ParseHold("Anvisa device CSV schema does not match pinned dictionary")
        seen = {}
        output = []
        for row_number, row in enumerate(rows, 2):
            if row_number > MAX_RECORDS + 1:
                raise ParseHold("Anvisa devices exceed row limit")
            if None in row or any(v is None for v in row.values()):
                raise ParseHold(f"row {row_number}: malformed CSV columns")
            reg = _text(row["NUMERO_REGISTRO_CADASTRO"],
                        "NUMERO_REGISTRO_CADASTRO", max_len=20)
            proc = _text(row["NUMERO_PROCESSO"], "NUMERO_PROCESSO", max_len=40)
            risk = _text(row["CLASSE_RISCO"], "CLASSE_RISCO", max_len=8)
            cnpj = _text(row["CNPJ_DETENTOR_REGISTRO_CADASTRO"],
                         "CNPJ_DETENTOR_REGISTRO_CADASTRO", max_len=24)
            if not REG_RE.fullmatch(reg) or not PROC_RE.fullmatch(proc):
                raise ParseHold(f"row {row_number}: invalid registry/process identifiers")
            if risk not in RISK or not CNPJ_RE.fullmatch(cnpj):
                raise ParseHold(f"row {row_number}: invalid declared risk class or CNPJ")
            _text(row["NOME_TECNICO"], "NOME_TECNICO")
            _text(row["NOME_COMERCIAL"], "NOME_COMERCIAL")
            _text(row["DETENTOR_REGISTRO_CADASTRO"], "DETENTOR_REGISTRO_CADASTRO")
            manufacturer = _text(row["NOME_FABRICANTE"], "NOME_FABRICANTE", required=False)
            country = _text(row["NOME_PAIS_FABRIC"], "NOME_PAIS_FABRIC", required=False)
            _text(row["DT_PUB_REGISTRO_CADASTRO"], "DT_PUB_REGISTRO_CADASTRO",
                  required=False, max_len=120)
            _text(row["VALIDADE_REGISTRO_CADASTRO"], "VALIDADE_REGISTRO_CADASTRO",
                  required=False, max_len=120)
            if "DT_ATUALIZACAO_DADO" in row:
                _text(row["DT_ATUALIZACAO_DADO"], "DT_ATUALIZACAO_DADO",
                      required=False, max_len=120)
            # Distinct manufacturer/country rows are not collapsed to product.
            key = (reg, proc, cnpj, manufacturer, country)
            seen[key] = seen.get(key, 0) + 1
            candidate = {
                "registration_number_candidate": reg,
                "process_number_candidate": proc,
                "risk_class_declared_candidate": risk,
                "source_occurrence_index": seen[key],
                "manufacturer_identity_sha256": hashlib.sha256(
                    f"{manufacturer}|{country}".encode("utf-8")).hexdigest(),
            }
            rec_sha = hashlib.sha256(json.dumps(candidate, sort_keys=True,
                separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
            output.append({
                **candidate, "record_sha256": rec_sha, "source_sha256": digest,
                "source_id": source_id, "document_id": document_id,
                "source_contract": SOURCE_CONTRACT, "parser": "anvisa_dev",
                "parser_version": PARSER_API_VERSION,
                "official_source_uri": SOURCE_URI, "captured_at_declared": dt.isoformat(),
                "source_origin_verified": False, "registry_current_verified": False,
                "rights_verified": False, "clinical_approved": False,
                "publication_allowed": False, "release_allowed": False,
                "status": "HOLD_HUMAN",
            })
        if not output:
            raise ParseHold("Anvisa device CSV has no records")
        return output
    except (UnicodeError, csv.Error) as exc:
        raise ParseHold("malformed or unsupported Anvisa device CSV") from exc
