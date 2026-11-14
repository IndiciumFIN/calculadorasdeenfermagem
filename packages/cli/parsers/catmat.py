"""CATMAT item catalog API page metadata parser: strictly local, source-bound.

Official specification: https://dadosabertos.compras.gov.br/swagger-ui/index.html
Endpoint: /modulo-material/4_consultarItemMaterial
No network, publishing, clinical inference or procurement recommendation.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from typing import Any

SOURCE_CONTRACT = "contracts/fontes/catmat.json"
PARSER_API_VERSION = "1.0.0"
SOURCE_URI = "https://dadosabertos.compras.gov.br/modulo-material/4_consultarItemMaterial"
MAX_BYTES = 5_000_000
MAX_PAGE_SIZE = 500
MAX_TEXT = 20000
HEX_SHA = re.compile(r"[0-9a-f]{64}", re.ASCII)


class ParseHold(ValueError):
    """Invalid snapshot, inconsistent page or unverified provenance."""


def _positive(value: Any, field: str, *, minimum: int = 1, maximum: int = 999_999_999) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ParseHold(f"{field}: invalid integer")
    return value


def _text(value: Any, field: str, maximum: int = 256) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ParseHold(f"{field}: missing or oversized")
    return value.strip()


def _unique_pairs(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            raise ParseHold(f"duplicate JSON key: {k[:60]}")
        obj[k] = v
    return obj


def _reject_constant(_):
    raise ParseHold("Nonfinite JSON number")


def parse(raw: bytes | str, *, source_id: str, document_id: str,
          expected_sha256: str, page: int, captured_at: str) -> list[dict]:
    """Parse one pinned official CATMAT item-catalog API page.

    API response bytes must be collected separately with authenticated
    provenance. Caller-supplied expected_sha256 alone does not prove origin.
    """
    source_id = _text(source_id, "source_id")
    document_id = _text(document_id, "document_id")
    page = _positive(page, "page")
    capture = _text(captured_at, "captured_at")
    try:
        dt = datetime.fromisoformat(capture.replace("Z", "+00:00"))
        if dt.utcoffset() is None:
            raise ValueError("timezone required")
    except ValueError as e:
        raise ParseHold("captured_at: timezone-aware ISO date required") from e

    if not isinstance(raw, (bytes, str)):
        raise ParseHold("API response requires bytes or str")
    payload = raw.encode("utf-8") if isinstance(raw, str) else raw
    if not payload or len(payload) > MAX_BYTES or bytes([0]) in payload:
        raise ParseHold("API payload empty, too large or binary")
    if not isinstance(expected_sha256, str) or not HEX_SHA.fullmatch(expected_sha256):
        raise ParseHold("expected_sha256 must be a lowercase digest")
    digest = hashlib.sha256(payload).hexdigest()
    if expected_sha256 != digest:
        raise ParseHold("CATMAT response differs from pinned snapshot")
    try:
        root = json.loads(payload.decode("utf-8-sig"), object_pairs_hook=_unique_pairs,
                          parse_constant=_reject_constant)
    except (UnicodeError, json.JSONDecodeError) as e:
        raise ParseHold("CATMAT JSON malformed") from e
    if not isinstance(root, dict):
        raise ParseHold("CATMAT response expected object")
    records = root.get("resultado")
    if not isinstance(records, list) or not 1 <= len(records) <= MAX_PAGE_SIZE:
        raise ParseHold("CATMAT nonempty bounded resultado required")
    total = _positive(root.get("totalRegistros"), "totalRegistros")
    pages = _positive(root.get("totalPaginas"), "totalPaginas")
    remaining = _positive(root.get("paginasRestantes"), "paginasRestantes", minimum=0)
    if page > pages or remaining != pages - page or total < len(records):
        raise ParseHold("CATMAT pagination inconsistent")
    if page < pages and len(records) < 1:
        raise ParseHold("empty intermediate CATMAT page")

    seen = set()
    out = []
    for number, row in enumerate(records, 1):
        if not isinstance(row, dict):
            raise ParseHold(f"row {number}: object required")
        code = _positive(row.get("codigoItem"), "codigoItem")
        group = _positive(row.get("codigoGrupo"), "codigoGrupo")
        cls = _positive(row.get("codigoClasse"), "codigoClasse")
        pdm = _positive(row.get("codigoPdm"), "codigoPdm")
        desc = _text(row.get("descricaoItem"), "descricaoItem", MAX_TEXT)
        if code in seen:
            raise ParseHold("duplicate CATMAT material code")
        seen.add(code)
        status = row.get("statusItem")
        if type(status) is not bool:
            raise ParseHold("statusItem must be boolean")
        # Text is checked for presence, but deliberately not exported.
        if any(ord(char) < 32 for char in desc):
            raise ParseHold("description contains invalid controls")
        candidate = {
            "catmat_item_code_candidate": code,
            "catmat_group_code_candidate": group,
            "catmat_class_code_candidate": cls,
            "catmat_pdm_code_candidate": pdm,
            "status_active_useless_for_clinical_decision": status,
        }
        normalized_sha = hashlib.sha256(json.dumps(
            candidate, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")).hexdigest()
        out.append({
            **candidate,
            "record_sha256": normalized_sha,
            "source_sha256": digest,
            "source_id": source_id,
            "document_id": document_id,
            "source_contract": SOURCE_CONTRACT,
            "parser": "catmat",
            "parser_version": PARSER_API_VERSION,
            "source_endpoint": SOURCE_URI,
            "page_declared": page,
            "total_pages_declared": pages,
            "capture_time_declared": dt.isoformat(),
            "source_origin_verified": False,
            "catalog_membership_verified": False,
            "rights_verified": False,
            "status": "HOLD_HUMAN",
            "clinical_approved": False,
            "publication_allowed": False,
            "release_allowed": False,
        })
    return sorted(out, key=lambda row: row["catmat_item_code_candidate"])
