"""Narrow ICD-11 MMS JSON-LD parser, official WHO v2 response metadata only.

Official references:
https://icd.who.int/docs/icd-api/APIDoc-Version2/
https://icd.who.int/docs/icd-api/ICD-schema/

Accepts a *single*, pinned JSON-LD linearization entity response for a specific
releaseId; not Foundation, search results, or postcoordinated code combinations.
Never downloads, guesses code membership, copies clinical terms or releases data.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

PARSER_API_VERSION = "1.0.0"
SOURCE_CONTRACT = "contracts/fontes/cid11.json"
SPEC_URI = "https://icd.who.int/docs/icd-api/APIDoc-Version2/"
WHO_CONTEXT = "http://id.who.int/icd/contexts/contextForLinearizationEntity.json"
MAX_BYTES = 2_000_000
RELEASE_RE = re.compile(r"20[0-9]{2}-(0[1-9]|1[0-2])", re.ASCII)
CODE_RE = re.compile(r"[0-9A-Z]{2,8}(?:\.[0-9A-Z]{1,6})?", re.ASCII)
SHA_RE = re.compile(r"[0-9a-f]{64}", re.ASCII)


class ParseHold(ValueError):
    """A WHO ICD entity is invalid, outside the subset, or not verified."""


def _text(v: Any, name: str, max_len: int = 256) -> str:
    if not isinstance(v, str) or not v.strip() or len(v) > max_len:
        raise ParseHold(f"{name}: required bounded text")
    return v.strip()


def _unique_pairs(pairs):
    item = {}
    for key, value in pairs:
        if key in item:
            raise ParseHold(f"duplicate JSON key: {key[:40]}")
        item[key] = value
    return item


def _invalid_constant(_):
    raise ParseHold("nonfinite JSON number is forbidden")


def _json_bytes(raw):
    if not isinstance(raw, (bytes, str)):
        raise ParseHold("WHO JSON-LD input must be bytes or str")
    payload = raw.encode("utf-8") if isinstance(raw, str) else raw
    if not payload or len(payload) > MAX_BYTES or bytes([0]) in payload:
        raise ParseHold("WHO JSON-LD empty, oversized or binary")
    try:
        return payload, json.loads(payload.decode("utf-8-sig"),
                                   object_pairs_hook=_unique_pairs,
                                   parse_constant=_invalid_constant)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ParseHold("malformed WHO JSON-LD") from exc


def parse(raw: bytes | str, *, source_id: str, document_id: str,
          release_id: str, expected_sha256: str) -> list[dict]:
    """Return one source-bound, nonpublishable candidate ICD-11 MMS code.

    A digest match checks supplied bytes, not WHO origin, validity of the
    release, language license, or a code's clinical appropriateness.
    """
    source_id = _text(source_id, "source_id")
    document_id = _text(document_id, "document_id")
    release = _text(release_id, "release_id")
    if not RELEASE_RE.fullmatch(release):
        raise ParseHold("release_id must be explicitly pinned YYYY-MM")
    payload, entity = _json_bytes(raw)
    if not isinstance(expected_sha256, str) or not SHA_RE.fullmatch(expected_sha256):
        raise ParseHold("trusted manifest must provide lowercase SHA-256")
    digest = hashlib.sha256(payload).hexdigest()
    if digest != expected_sha256:
        raise ParseHold("WHO response differs from pinned SHA-256")
    if not isinstance(entity, dict):
        raise ParseHold("expected one WHO MMS JSON-LD entity")
    if entity.get("@context") != WHO_CONTEXT:
        raise ParseHold("unexpected WHO JSON-LD context")
    prefix = f"http://id.who.int/icd/release/11/{release}/mms/"
    entity_uri = _text(entity.get("@id"), "@id", 500)
    if not entity_uri.startswith(prefix):
        raise ParseHold("entity URI does not belong to pinned MMS release")
    entity_id = entity_uri.removeprefix(prefix)
    if not re.fullmatch(r"[0-9]{1,20}", entity_id, re.ASCII):
        raise ParseHold("unsupported MMS entity identifier")
    if entity.get("classKind") != "category":
        raise ParseHold("only codable category subset is supported")
    code = _text(entity.get("code"), "code", 32)
    if not CODE_RE.fullmatch(code):
        raise ParseHold("invalid code shape for narrow MMS subset")
    source_uri = _text(entity.get("source"), "source", 256)
    if not re.fullmatch(r"http://id\.who\.int/icd/entity/[0-9]{1,20}", source_uri):
        raise ParseHold("source must point to WHO Foundation URI")
    parents = entity.get("parent")
    if (not isinstance(parents, list) or len(parents) != 1
            or not isinstance(parents[0], str) or not parents[0].startswith(prefix)):
        raise ParseHold("MMS category requires one release-matching parent")
    parent_id = parents[0].removeprefix(prefix)
    if not re.fullmatch(r"[0-9]{1,20}", parent_id, re.ASCII) or parent_id == entity_id:
        raise ParseHold("invalid or self-referential MMS parent")
    title = entity.get("title")
    if not isinstance(title, dict):
        raise ParseHold("WHO entity title metadata required")
    language = _text(title.get("@language"), "title.@language", 24)
    if not re.fullmatch(r"[a-z]{2,3}(?:-[A-Za-z]{2,8})?", language, re.ASCII):
        raise ParseHold("unsupported title language tag")
    _text(title.get("@value"), "title.@value", 4096)
    # Only identifiers and metadata are released from the parser. WHO title,
    # description, definitions, coding notes, synonyms and extensions stay out.
    record = {
        "icd11_code_candidate": code,
        "mms_entity_uri": entity_uri,
        "foundation_entity_uri": source_uri,
        "mms_parent_uri_candidate": parents[0],
        "language": language,
        "release_id_declared": release,
    }
    checksum = hashlib.sha256(json.dumps(
        record, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")).hexdigest()
    return [{
        **record,
        "record_sha256": checksum,
        "source_sha256": digest,
        "source_id": source_id,
        "document_id": document_id,
        "source_contract": SOURCE_CONTRACT,
        "parser": "icd11",
        "parser_version": PARSER_API_VERSION,
        "source_origin_verified": False,
        "reference_membership_verified": False,
        "rights_verified": False,
        "status": "HOLD_HUMAN",
        "clinical_approved": False,
        "publication_allowed": False,
        "release_allowed": False,
    }]
