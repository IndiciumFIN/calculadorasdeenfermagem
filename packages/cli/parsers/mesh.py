"""NLM MeSH DescriptorRecordSet XML parser; metadata and candidate graph only.

Primary sources: https://www.nlm.nih.gov/mesh/xmlmesh.html
                 https://www.nlm.nih.gov/mesh/xml_data_elements.html
No clinical claims, terminological license grant or public publication.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
from pathlib import Path
from xml.etree.ElementTree import ParseError
from defusedxml.ElementTree import iterparse
from defusedxml.common import DefusedXmlException

PARSER_API_VERSION = "1.0.0"
SOURCE_CONTRACT = "contracts/fontes/mesh.json"
SPEC_URI = "https://www.nlm.nih.gov/mesh/xmlmesh.html"
MAX_RAW_BYTES = 64_000_000
MAX_FILE_BYTES = 1_000_000_000
MAX_DESCRIPTOR_RECORDS = 100_000

_DESCRIPTOR_RE = re.compile(r"D[0-9]{6}")
_CONCEPT_RE = re.compile(r"M[0-9]{7,8}")
_TREE_RE = re.compile(r"[A-Z][0-9]{2}(?:\.[0-9]{1,9})*")


class ParseHold(ValueError):
    """MeSH descriptor data does not satisfy validated subset/rights gates."""


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ParseHold(f"{field}: empty")
    return value.strip()


def _ui(value, pattern, field):
    v = _text(value, field)
    if not pattern.fullmatch(v):
        raise ParseHold(f"{field}: invalid identifier")
    return v


def _descriptor(el):
    did = _ui(el.findtext("DescriptorUI"), _DESCRIPTOR_RE, "DescriptorUI")
    title = _text(el.findtext("DescriptorName/String"), "DescriptorName/String")
    if len(title) > 512:
        raise ParseHold("DescriptorName too long")
    descriptor_class = el.get("DescriptorClass")
    if descriptor_class is not None and descriptor_class not in {"1", "2", "3", "4"}:
        raise ParseHold("DescriptorClass out of NLM range")

    concepts = el.findall("ConceptList/Concept")
    if not concepts:
        raise ParseHold("Descriptor requires ConceptList")
    preferred = [c for c in concepts if c.get("PreferredConceptYN") == "Y"]
    if len(preferred) != 1:
        raise ParseHold("Descriptor requires one preferred concept")
    concept_ids = [
        _ui(c.findtext("ConceptUI"), _CONCEPT_RE, "ConceptUI") for c in concepts
    ]
    if len(set(concept_ids)) != len(concept_ids):
        raise ParseHold("Duplicate ConceptUI within descriptor")

    tree_numbers = []
    for tree in el.findall("TreeNumberList/TreeNumber"):
        number = _text(tree.text, "TreeNumber")
        if not _TREE_RE.fullmatch(number):
            raise ParseHold("MeSH TreeNumber malformed")
        tree_numbers.append(number)
    if len(set(tree_numbers)) != len(tree_numbers):
        raise ParseHold("Duplicate TreeNumber within descriptor")

    related = []
    for target in el.findall(".//SeeRelatedDescriptor/DescriptorReferredTo/DescriptorUI"):
        rid = _ui(target.text, _DESCRIPTOR_RE, "SeeRelatedDescriptor.DescriptorUI")
        if rid == did:
            raise ParseHold("Self-referencing SeeRelatedDescriptor")
        related.append(rid)
    if len(set(related)) != len(related):
        raise ParseHold("Duplicate SeeRelatedDescriptor")

    # Do not export synonyms, annotations, scope notes, term records or definitions.
    return {
        "descriptor_ui": did,
        "descriptor_name": title,
        "descriptor_class": descriptor_class,
        "concept_uids_candidate": sorted(concept_ids),
        "preferred_concept_ui_candidate": _ui(
            preferred[0].findtext("ConceptUI"), _CONCEPT_RE, "preferred.ConceptUI"),
        "tree_numbers_candidate": sorted(tree_numbers),
        "see_related_descriptor_ids_candidate": sorted(related),
    }


def _bytes_and_stream(raw):
    if isinstance(raw, Path):
        if not raw.is_file() or raw.stat().st_size == 0 or raw.stat().st_size > MAX_FILE_BYTES:
            raise ParseHold("MeSH input file missing, empty or too large")
        with raw.open("rb") as fp:
            digest = hashlib.file_digest(fp, "sha256").hexdigest()
        return digest, raw.open("rb")
    if not isinstance(raw, (bytes, str)):
        raise ParseHold("MeSH XML requires bytes, string or Path")
    payload = raw.encode("utf-8") if isinstance(raw, str) else raw
    if not payload or len(payload) > MAX_RAW_BYTES:
        raise ParseHold("MeSH in-memory XML empty or too large")
    return hashlib.sha256(payload).hexdigest(), io.BytesIO(payload)


def parse(raw: bytes | str | Path, *, source_id: str, document_id: str,
          production_year: int, verify_related: bool = True) -> list[dict]:
    """Read DescriptorRecordSet, preserve candidate identifiers, and fail closed.

    Path inputs are streamed to support official large MeSH descriptor releases.
    External DTDs are not fetched. Internal entity expansion is rejected by
    defusedxml. Whole batch is invalid on duplicate/malformed/orphan references.
    """
    source_id = _text(source_id, "source_id")
    document_id = _text(document_id, "document_id")
    if type(production_year) is not int or not 1900 <= production_year <= 2100:
        raise ParseHold("production_year must be an explicitly supplied valid year")
    digest, stream = _bytes_and_stream(raw)
    records = []
    seen = set()
    root = None
    try:
        with stream:
            for event, element in iterparse(stream, events=("start", "end")):
                if root is None:
                    if event != "start" or element.tag != "DescriptorRecordSet":
                        raise ParseHold("MeSH descriptor root must be DescriptorRecordSet")
                    root = element
                if event == "end" and element.tag == "DescriptorRecord":
                    if len(records) >= MAX_DESCRIPTOR_RECORDS:
                        raise ParseHold("Descriptor count exceeds bound")
                    record = _descriptor(element)
                    uid = record["descriptor_ui"]
                    if uid in seen:
                        raise ParseHold("Duplicate DescriptorUI across records")
                    seen.add(uid)
                    records.append(record)
                    element.clear()
                    root.clear()
    except (ParseError, DefusedXmlException, UnicodeError, OverflowError) as exc:
        raise ParseHold("Unsafe or malformed MeSH XML") from exc
    if root is None or not records:
        raise ParseHold("Empty MeSH DescriptorRecordSet")
    if verify_related:
        for record in records:
            for rid in record["see_related_descriptor_ids_candidate"]:
                if rid not in seen:
                    raise ParseHold(f"SeeRelatedDescriptor orphan: {rid}")
    output = []
    for record in sorted(records, key=lambda r: r["descriptor_ui"]):
        record_sha = hashlib.sha256(json.dumps(
            record, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False
        ).encode("utf-8")).hexdigest()
        output.append({
            **record,
            "record_sha256": record_sha,
            "source_sha256": digest,
            "source_id": source_id,
            "document_id": document_id,
            "source_contract": SOURCE_CONTRACT,
            "parser": "mesh",
            "parser_version": PARSER_API_VERSION,
            "production_year_declared": production_year,
            "production_year_verified": False,
            "rights": "REVIEW_NLM_TERMS_BY_OPERATION",
            "status": "HOLD_HUMAN",
            "clinical_approved": False,
            "publication_allowed": False,
            "release_allowed": False,
        })
    return output
