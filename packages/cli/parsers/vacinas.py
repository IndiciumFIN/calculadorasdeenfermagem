"""CDC CVX flat-file metadata reader (candidate only, never clinical release).

Official publication: https://www.cdc.gov/iis/code-sets/index.html
Official flat file: https://www2.cdc.gov/vaccines/iis/iisstandards/downloads/CVX.txt

Input is a pinned, locally supplied CDC CVX.txt snapshot, NOT a live request.
The CDC file has seven pipe-delimited fields: code, short name, full name,
notes, status, nonvaccine flag, update date. Textual descriptions and notes
are deliberately excluded from output. No clinical or Brazilian PNI inference.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime

PARSER_API_VERSION = "1.0.0"
SOURCE_CONTRACT = "contracts/fontes/vacinas_cdc.json"
SOURCE_URI = "https://www2.cdc.gov/vaccines/iis/iisstandards/downloads/CVX.txt"
SPEC_URI = "https://www.cdc.gov/iis/code-sets/index.html"
MAX_INPUT_BYTES = 16_000_000
MAX_RECORDS = 20_000
STATUS_US = frozenset({"Active", "Inactive", "Pending", "Non-US", "Never Active"})
CODE_PATTERN = re.compile(r"[0-9]{1,4}", re.ASCII)
SHA_PATTERN = re.compile(r"[0-9a-f]{64}", re.ASCII)


class ParseHold(ValueError):
    """Invalid, unverified or unsupported CVX batch; reject atomically."""


def _required_string(value, field):
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ParseHold(f"{field}: explicit nonempty text required")
    return value.strip()


def _date(value, field, fmt):
    if not isinstance(value, str):
        raise ParseHold(f"{field}: expected date string")
    try:
        parsed = datetime.strptime(value, fmt).date()
    except ValueError as exc:
        raise ParseHold(f"{field}: invalid date") from exc
    return parsed


def parse(
    raw: bytes | str, *, source_id: str, document_id: str,
    release_date: str, expected_sha256: str
) -> list[dict]:
    """Parse a single CDC CVX.txt snapshot with strict provenance and HOLD.

    Caller must provide the source artifact's SHA-256 and release date from a
    separate provenance manifest. A matching hash proves byte equality only,
    not CDC authorship, authorization, a valid clinical code or release rights.
    The parsed status is a US administrative flag, not vaccination guidance.
    """
    source_id = _required_string(source_id, "source_id")
    document_id = _required_string(document_id, "document_id")
    release = _date(release_date, "release_date", "%Y-%m-%d")
    if release > date(2100, 1, 1) or release < date(2000, 1, 1):
        raise ParseHold("release_date: implausible snapshot date")
    if not isinstance(raw, (bytes, str)):
        raise ParseHold("CVX input must be bytes or str")
    payload = raw.encode("utf-8") if isinstance(raw, str) else raw
    if not payload or len(payload) > MAX_INPUT_BYTES or bytes([0]) in payload:
        raise ParseHold("CVX source empty, oversized or binary")
    digest = hashlib.sha256(payload).hexdigest()
    if not isinstance(expected_sha256, str) or not SHA_PATTERN.fullmatch(expected_sha256):
        raise ParseHold("expected_sha256 must be canonical lowercase SHA-256")
    if digest != expected_sha256:
        raise ParseHold("source SHA-256 does not match pinned snapshot")
    try:
        lines = payload.decode("utf-8-sig").splitlines()
    except UnicodeError as exc:
        raise ParseHold("CVX input is not UTF-8") from exc
    if not lines or len(lines) > MAX_RECORDS:
        raise ParseHold("CVX file empty or exceeds record bound")

    seen = set()
    records = []
    for index, line in enumerate(lines, 1):
        if not line.strip():
            raise ParseHold(f"CVX line {index}: empty record")
        fields = [field.strip() for field in line.split("|")]
        if len(fields) != 7:
            raise ParseHold(f"CVX line {index}: expected seven fields")
        code, short, full, note, status, nonvaccine, last_updated = fields
        if not CODE_PATTERN.fullmatch(code):
            raise ParseHold(f"CVX line {index}: invalid code")
        if code in seen:
            raise ParseHold(f"CVX line {index}: repeated CVX code")
        seen.add(code)
        if not short or not full or len(short) > 1024 or len(full) > 4096 or len(note) > 16384:
            raise ParseHold(f"CVX line {index}: missing or oversized source fields")
        if status not in STATUS_US:
            raise ParseHold(f"CVX line {index}: unknown CDC US status")
        if nonvaccine not in {"True", "False"}:
            raise ParseHold(f"CVX line {index}: invalid nonvaccine flag")
        updated = _date(last_updated, f"CVX line {index} updated", "%Y/%m/%d")
        if updated > release:
            raise ParseHold(f"CVX line {index}: updated after declared release")
        record = {
            "cvx_code_candidate": code,  # Keep leading zeros, e.g., "01".
            "status_us_candidate": status,
            "is_nonvaccine_candidate": nonvaccine == "True",
            "last_updated_us": updated.isoformat(),
        }
        record_digest = hashlib.sha256(json.dumps(
            record, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")).hexdigest()
        records.append({
            **record,
            "record_sha256": record_digest,
            "source_sha256": digest,
            "source_id": source_id,
            "document_id": document_id,
            "source_contract": SOURCE_CONTRACT,
            "official_source_uri": SOURCE_URI,
            "parser": "vacinas",
            "parser_version": PARSER_API_VERSION,
            "release_date_declared": release.isoformat(),
            "origin_and_rights_verified": False,
            "status": "HOLD_HUMAN",
            "clinical_approved": False,
            "publication_allowed": False,
            "release_allowed": False,
        })
    if not records:
        raise ParseHold("No CVX records")
    return sorted(records, key=lambda r: (int(r["cvx_code_candidate"]), r["cvx_code_candidate"]))
