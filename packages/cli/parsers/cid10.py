"""CID-10 DATASUS V2008 categories CSV: source-bound metadata candidates only.

Official source: http://www2.datasus.gov.br/cid10/V2008/downloads/CID10CSV.zip
Subset: CID-10-CATEGORIAS.CSV, not the full four-table classification.
No network access, copying descriptions, clinical inference or publication.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re

SOURCE_CONTRACT = "contracts/fontes/cid10.json"
PARSER_API_VERSION = "1.0.0"
SOURCE_URI = "http://www2.datasus.gov.br/cid10/V2008/downloads/CID10CSV.zip"
TABLE_NAME = "CID-10-CATEGORIAS.CSV"
HEADER = ("CAT", "CLASSIF", "DESCRICAO", "DESCRABREV", "REFER", "EXCLUIDOS", "")
MAX_RAW_BYTES = 8_000_000
MAX_RECORDS = 10_000
CODE_RE = re.compile(r"[A-Z][0-9]{2}", re.ASCII)
SHA_RE = re.compile(r"[0-9a-f]{64}", re.ASCII)


class ParseHold(ValueError):
    """Unsupported, damaged or unverified DATASUS source; reject atomically."""


def _required(value, name, max_size=512):
    if not isinstance(value, str) or not value.strip() or len(value) > max_size:
        raise ParseHold(f"{name}: explicit nonempty bounded string required")
    text = value.strip()
    if any(ord(c) < 32 for c in text):
        raise ParseHold(f"{name}: control character")
    return text


def parse(raw: bytes | str, *, source_id: str, document_id: str,
          edition: str, expected_sha256: str, table_name: str) -> list[dict]:
    """Interpret one pinned category CSV extracted from official DATASUS ZIP.

    Input manifests, edition, licensing and authenticity must be verified
    outside the parser. An exact SHA only proves equality with caller-supplied
    bytes and cannot authorize a clinical or publication decision.
    """
    source_id = _required(source_id, "source_id", 256)
    document_id = _required(document_id, "document_id", 256)
    if edition != "V2008":
        raise ParseHold("only DATASUS CID-10 V2008 category subset supported")
    if table_name != TABLE_NAME:
        raise ParseHold("only exact CID-10-CATEGORIAS.CSV table supported")
    if not isinstance(raw, (str, bytes)):
        raise ParseHold("CSV must be bytes or text")
    payload = raw.encode("cp1252") if isinstance(raw, str) else raw
    if not payload or len(payload) > MAX_RAW_BYTES or bytes([0]) in payload:
        raise ParseHold("CSV empty, oversized or binary")
    if not isinstance(expected_sha256, str) or not SHA_RE.fullmatch(expected_sha256):
        raise ParseHold("expected_sha256 must be canonical lowercase digest")
    digest = hashlib.sha256(payload).hexdigest()
    if digest != expected_sha256:
        raise ParseHold("DATASUS snapshot hash mismatch")
    try:
        text = payload.decode("cp1252")
        reader = csv.reader(io.StringIO(text, newline=""), delimiter=";",
                            quotechar='"', strict=True)
        actual_header = next(reader, None)
        if tuple(actual_header or ()) != HEADER:
            raise ParseHold("unexpected CID-10 category table header")
        output = []
        seen = set()
        for row_number, row in enumerate(reader, 2):
            if row_number > MAX_RECORDS + 1:
                raise ParseHold("CID-10 category CSV exceeds record limit")
            if len(row) != len(HEADER):
                raise ParseHold(f"row {row_number}: column count mismatch")
            item = dict(zip(HEADER, row))
            code = _required(item["CAT"], "CAT", 3)
            if not CODE_RE.fullmatch(code) or code in seen:
                raise ParseHold(f"row {row_number}: invalid/duplicate CID category")
            seen.add(code)
            marker = item["CLASSIF"].strip()
            if marker not in ("", "+", "*"):
                raise ParseHold(f"row {row_number}: unsupported classif marker")
            # Required descriptive fields checked but never exported.
            _required(item["DESCRICAO"], "DESCRICAO", 16384)
            _required(item["DESCRABREV"], "DESCRABREV", 16384)
            for extra in ("REFER", "EXCLUIDOS", ""):
                cell = item[extra]
                if not isinstance(cell, str) or len(cell) > 16384:
                    raise ParseHold(f"row {row_number}: malformed reference field")
            if item[""] != "":
                raise ParseHold(f"row {row_number}: unexpected trailing field")
            record = {
                "cid10_category_candidate": code,
                "classification_marker_candidate": marker or None,
                "edition_declared": edition,
            }
            record_hash = hashlib.sha256(json.dumps(
                record, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            ).encode("utf-8")).hexdigest()
            output.append({
                **record,
                "record_sha256": record_hash,
                "source_sha256": digest,
                "source_id": source_id,
                "document_id": document_id,
                "source_contract": SOURCE_CONTRACT,
                "parser": "cid10",
                "parser_version": PARSER_API_VERSION,
                "source_uri": SOURCE_URI,
                "table_name": TABLE_NAME,
                "source_origin_verified": False,
                "edition_membership_verified": False,
                "rights_verified": False,
                "clinical_approved": False,
                "publication_allowed": False,
                "release_allowed": False,
                "status": "HOLD_HUMAN",
            })
        if not output:
            raise ParseHold("CID-10 category CSV lacks records")
        return output
    except (UnicodeError, csv.Error, UnicodeEncodeError) as exc:
        raise ParseHold("unrecognized/corrupt DATASUS category encoding") from exc
