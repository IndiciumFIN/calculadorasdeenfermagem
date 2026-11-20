"""NLM MedlinePlus health-topics XML metadata parser: fail-closed, no text reuse.

Official schema: https://medlineplus.gov/xmldescription.html
Input may contain copyrighted/licensed article summaries; do not emit or publish
full-summary, snippets, external site text, images, trademarks or page excerpts.
"""
from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime
from urllib.parse import urlsplit
from xml.etree.ElementTree import ParseError
from defusedxml.ElementTree import iterparse
from defusedxml.common import DefusedXmlException

SOURCE_CONTRACT = "contracts/fontes/medlineplus.json"
PARSER_API_VERSION = "1.0.0"
SPEC_URI = "https://medlineplus.gov/xmldescription.html"
ATTRIBUTION = "MedlinePlus.gov — U.S. National Library of Medicine"
MAX_XML_BYTES = 64_000_000
MAX_RECORDS = 20_000


class ParseHold(ValueError):
    """Invalid/unverified MedlinePlus metadata; entire feed must stay HOLD."""


def _nonempty(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ParseHold(f"{name}: missing or invalid")
    return value.strip()


def _id(value, name):
    identifier = _nonempty(value, name)
    if not identifier.isascii() or not identifier.isdecimal():
        raise ParseHold(f"{name}: MedlinePlus ID must be digits")
    return identifier


def _url(value, name):
    url = _nonempty(value, name)
    try:
        u = urlsplit(url)
    except ValueError as exc:
        raise ParseHold(f"{name}: malformed URL") from exc
    if (u.scheme != "https" or u.hostname != "medlineplus.gov"
            or u.username is not None or u.password is not None
            or u.port is not None or not u.path or u.path == "/"
            or u.query or u.fragment):
        raise ParseHold(f"{name}: URL is not canonical MedlinePlus HTTPS")
    return url


def _date_generated(raw):
    raw = _nonempty(raw, "health-topics.date-generated")
    for fmt in ("%m/%d/%Y %H:%M:%S", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    raise ParseHold("health-topics date-generated is invalid")


def _record(el):
    identifier = _id(el.get("id"), "health-topic.id")
    language = _nonempty(el.get("language"), "health-topic.language")
    if language not in {"English", "Spanish"}:
        raise ParseHold("MedlinePlus health-topic language not supported")
    title = _nonempty(el.get("title"), "health-topic.title")
    if len(title) > 512:
        raise ParseHold("health-topic title exceeds safe size")
    canonical_url = _url(el.get("url"), "health-topic.url")
    groups = sorted(set(
        _nonempty(x.text, "group") for x in el.findall("group")
    ))
    if not groups:
        raise ParseHold("health-topic requires at least one group")
    if not el.findall("site"):
        raise ParseHold("health-topic requires at least one site entry")

    related = []
    for x in el.findall("related-topic"):
        related.append(_id(x.get("id"), "related-topic.id"))
        _url(x.get("url"), "related-topic.url")
    if identifier in related:
        raise ParseHold("health-topic must not relate to itself")
    if len(related) != len(set(related)):
        raise ParseHold("duplicated related-topic id")

    mapped = el.find("language-mapped-topic")
    mapped_id = None
    if mapped is not None:
        mapped_id = _id(mapped.get("id"), "language-mapped-topic.id")
        _url(mapped.get("url"), "language-mapped-topic.url")
        if mapped_id == identifier:
            raise ParseHold("language mapping cannot refer to same topic")

    mesh_ids = []
    for x in el.findall("mesh-heading/descriptor"):
        mesh_id = _nonempty(x.get("id"), "mesh descriptor.id")
        if not mesh_id.startswith("D") or not mesh_id[1:].isdigit():
            raise ParseHold("MeSH descriptor id outside expected format")
        mesh_ids.append(mesh_id)
    if len(mesh_ids) != len(set(mesh_ids)):
        raise ParseHold("duplicated MeSH descriptor id")

    # Omit full-summary, all site content, synonyms, external linked text.
    return {
        "topic_id": identifier,
        "language": language,
        "title": title,
        "canonical_url": canonical_url,
        "group_titles": groups,
        "related_topic_ids_candidate": sorted(related),
        "language_mapped_topic_id_candidate": mapped_id,
        "mesh_descriptor_ids_candidate": sorted(mesh_ids),
    }


def parse(raw: bytes | str, *, source_id: str, document_id: str,
          verify_internal_links: bool = True) -> list[dict]:
    """Parse one official MedlinePlus health-topics XML feed to metadata only.

    Accepts a 64 MB or smaller raw XML payload; external DTD is not loaded.
    defusedxml rejects entity expansion/external entity injection. The entire
    batch is atomic: any malformed record, duplicate or dangling internal link
    causes ParseHold. No external downloads, publish or clinical promotion.
    """
    source_id = _nonempty(source_id, "source_id")
    document_id = _nonempty(document_id, "document_id")
    if not isinstance(raw, (bytes, str)):
        raise ParseHold("MedlinePlus XML input must be bytes or string")
    payload = raw.encode("utf-8") if isinstance(raw, str) else raw
    if not payload or len(payload) > MAX_XML_BYTES:
        raise ParseHold("XML is empty or exceeds limit")
    total = None
    generated = None
    seen_root = False
    records = []
    seen = set()
    try:
        for event, element in iterparse(io.BytesIO(payload), events=("start", "end")):
            if not seen_root:
                if event != "start" or element.tag != "health-topics":
                    raise ParseHold("expected MedlinePlus health-topics root")
                seen_root = True
                value = _id(element.get("total"), "health-topics.total")
                total = int(value)
                date_raw = (element.get("date-generated")
                            or element.get("dategenerated"))
                generated = _date_generated(date_raw)
            if event == "end" and element.tag == "health-topic":
                if len(records) >= MAX_RECORDS:
                    raise ParseHold("XML topic count exceeds safety limit")
                item = _record(element)
                if item["topic_id"] in seen:
                    raise ParseHold("duplicate health-topic id")
                seen.add(item["topic_id"])
                records.append(item)
                element.clear()
    except (ParseError, DefusedXmlException, UnicodeError, OverflowError) as exc:
        raise ParseHold("unsafe or malformed MedlinePlus XML") from exc
    if not seen_root or not records or total != len(records):
        raise ParseHold("health-topics.total or feed contents inconsistent")

    by_id = {r["topic_id"]: r for r in records}
    if verify_internal_links:
        for item in records:
            for target in item["related_topic_ids_candidate"]:
                if target not in by_id:
                    raise ParseHold(f"related topic {target} has no matching source")
            mapped = item["language_mapped_topic_id_candidate"]
            if mapped is not None:
                other = by_id.get(mapped)
                if other is None or other["language"] == item["language"]:
                    raise ParseHold("language mapping missing or wrong language")
    feed_sha = hashlib.sha256(payload).hexdigest()
    output = []
    for item in sorted(records, key=lambda r: (r["language"], r["topic_id"])):
        item_hash = hashlib.sha256(json.dumps(
            item, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")).hexdigest()
        output.append({
            **item,
            "record_sha256": item_hash,
            "source_sha256": feed_sha,
            "source_id": source_id,
            "document_id": document_id,
            "date_generated": generated,
            "source_contract": SOURCE_CONTRACT,
            "parser": "medlineplus",
            "parser_version": PARSER_API_VERSION,
            "rights": "REVIEW_BY_OPERATION",
            "attribution": ATTRIBUTION,
            "status": "HOLD_HUMAN",
            "clinical_approved": False,
            "publication_allowed": False,
            "release_allowed": False,
        })
    return output
