"""SIES supply distribution data from official OpenDataSUS CSV/ZIP snapshots.

Source: dadosabertos.saude.gov.br/dataset/sies
Data dictionary defines TX_SIGLA, IBGE, TX_INSUMO, ANO, MES, QTDE,
ORIGEM, TX_AREA. No network, clinical recommendation or public release.
"""
from __future__ import annotations

import csv
from datetime import date
import hashlib
import io
import json
import re
import stat
import zipfile
from pathlib import PurePosixPath

SOURCE_CONTRACT = "contracts/fontes/sies.json"
PARSER_API_VERSION = "1.0.0"
SOURCE_URI = "https://dadosabertos.saude.gov.br/dataset/sies"
HEADER = frozenset(("TX_SIGLA", "IBGE", "TX_INSUMO", "ANO",
                    "MES", "QTDE", "ORIGEM", "TX_AREA"))
MAX_ZIP_BYTES = 80_000_000
MAX_UNCOMPRESSED = 200_000_000
MAX_MEMBERS = 64
MAX_RECORDS = 500_000
SHA_RE = re.compile(r"[0-9a-f]{64}", re.ASCII)


class ParseHold(ValueError):
    """Untrusted SIES snapshot rejected atomically."""


def _required_text(v, field, bound=1500):
    if not isinstance(v, str) or not v.strip() or len(v) > bound:
        raise ParseHold(f"{field}: missing or oversized")
    v = v.strip()
    if any(ord(x) < 32 for x in v):
        raise ParseHold(f"{field}: invalid control")
    return v


def _read_members(blob: bytes):
    if not blob.startswith(b"PK"):
        if len(blob) > MAX_UNCOMPRESSED:
            raise ParseHold("CSV exceeds uncompressed limit")
        return [("local-sies.csv", blob)]
    try:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            info = z.infolist()
            if not 1 <= len(info) <= MAX_MEMBERS:
                raise ParseHold("ZIP empty or member limit exceeded")
            total = 0
            members = []
            seen = set()
            for item in info:
                name = item.filename
                path = PurePosixPath(name)
                if (not name or item.is_dir() or path.is_absolute()
                    or len(path.parts) != 1 or ".." in path.parts
                    or "\\" in name or ":" in name
                    or not name.lower().endswith(".csv")
                    or name.lower() in seen):
                    raise ParseHold("ZIP unexpected/unsafe member path")
                seen.add(name.lower())
                mode = (item.external_attr >> 16)
                if stat.S_ISLNK(mode):
                    raise ParseHold("ZIP symlink forbidden")
                if item.flag_bits & 1:
                    raise ParseHold("ZIP encrypted member forbidden")
                total += item.file_size
                if total > MAX_UNCOMPRESSED or item.file_size == 0:
                    raise ParseHold("ZIP expanded data outside safe bound")
                if item.compress_size == 0 or item.file_size > item.compress_size * 500:
                    raise ParseHold("ZIP expansion ratio outside safe bound")
                data = z.read(item)
                if len(data) != item.file_size:
                    raise ParseHold("ZIP member length mismatch")
                members.append((name, data))
            return members
    except (zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError, EOFError) as exc:
        raise ParseHold("corrupt or unsupported ZIP") from exc


def parse(raw: bytes | str, *, source_id: str, document_id: str,
          snapshot_date: str, expected_sha256: str, delimiter: str = ";") -> list[dict]:
    """Ingest only locally supplied source bytes pinned by an external manifest."""
    source_id = _required_text(source_id, "source_id", 256)
    document_id = _required_text(document_id, "document_id", 256)
    if not isinstance(snapshot_date, str) or not re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}", snapshot_date):
        raise ParseHold("snapshot_date must be explicitly declared YYYY-MM-DD")
    try:
        date.fromisoformat(snapshot_date)
    except ValueError as exc:
        raise ParseHold("snapshot_date is not a valid calendar date") from exc
    if delimiter not in (",", ";"):
        raise ParseHold("CSV delimiter must be pinned comma or semicolon")
    if not isinstance(raw, (bytes, str)):
        raise ParseHold("SIES ZIP/CSV requires bytes or string")
    blob = raw.encode("utf-8") if isinstance(raw, str) else raw
    if not blob or len(blob) > MAX_ZIP_BYTES or bytes([0]) in blob and not blob.startswith(b"PK"):
        raise ParseHold("source empty, oversized or binary")
    if not isinstance(expected_sha256, str) or not SHA_RE.fullmatch(expected_sha256):
        raise ParseHold("expected_sha256 must be lowercase digest")
    archive_sha = hashlib.sha256(blob).hexdigest()
    if archive_sha != expected_sha256:
        raise ParseHold("source byte hash does not match declared snapshot")

    seen = {}
    rows_out = []
    for member_name, data in _read_members(blob):
        member_digest = hashlib.sha256(data).hexdigest()
        try:
            text = data.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(text, newline=""),
                                    delimiter=delimiter, strict=True)
            if (reader.fieldnames is None or set(reader.fieldnames) != HEADER
                    or len(reader.fieldnames) != len(HEADER)):
                raise ParseHold("CSV columns differ from official SIES dictionary")
            for record in reader:
                if len(rows_out) >= MAX_RECORDS:
                    raise ParseHold("maximum SIES row count exceeded")
                if None in record or any(v is None for v in record.values()):
                    raise ParseHold("CSV malformed row width")
                uf = _required_text(record["TX_SIGLA"], "TX_SIGLA", 128)
                ibge = _required_text(record["IBGE"], "IBGE", 12) if record["IBGE"].strip() else None
                if ibge is not None and not re.fullmatch(r"[0-9]{6,7}", ibge):
                    raise ParseHold("IBGE municipal code invalid")
                year = _required_text(record["ANO"], "ANO", 4)
                month = _required_text(record["MES"], "MES", 2)
                if not re.fullmatch(r"20[0-9]{2}", year) or not month.isascii() or not month.isdigit() or not 1 <= int(month) <= 12:
                    raise ParseHold("Invalid SIES year/month")
                qty = _required_text(record["QTDE"], "QTDE", 128)
                if not re.fullmatch(r"[0-9]+(?:[.,][0-9]+)?", qty):
                    raise ParseHold("SIES quantity string requires unambiguous decimal")
                inp = _required_text(record["TX_INSUMO"], "TX_INSUMO", 2000)
                org = _required_text(record["ORIGEM"], "ORIGEM", 2000)
                area = _required_text(record["TX_AREA"], "TX_AREA", 2000)
                record_key = (member_name, uf, ibge, year, month, qty, inp, org, area)
                seen[record_key] = seen.get(record_key, 0) + 1
                candidate = {
                    "uf_candidate": uf,
                    "ibge_municipio_candidate": ibge,
                    "period_candidate": f"{year}-{int(month):02d}",
                    "quantity_string_candidate": qty,
                    "supply_type_sha256": hashlib.sha256(inp.encode("utf-8")).hexdigest(),
                    "source_type_sha256": hashlib.sha256(org.encode("utf-8")).hexdigest(),
                    "area_sha256": hashlib.sha256(area.encode("utf-8")).hexdigest(),
                }
                record_sha = hashlib.sha256(json.dumps(candidate, sort_keys=True,
                    ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
                rows_out.append({
                    **candidate,
                    "record_sha256": record_sha,
                    "source_occurrence_index": seen[record_key],
                    "source_sha256": archive_sha,
                    "csv_member_sha256": member_digest,
                    "source_id": source_id, "document_id": document_id,
                    "source_contract": SOURCE_CONTRACT,
                    "parser": "sies", "parser_version": PARSER_API_VERSION,
                    "source_uri": SOURCE_URI,
                    "snapshot_date_declared": snapshot_date,
                    "source_origin_verified": False,
                    "rights_verified": False,
                    "clinical_approved": False,
                    "publication_allowed": False,
                    "release_allowed": False,
                    "status": "HOLD_HUMAN",
                })
        except (UnicodeError, csv.Error) as exc:
            raise ParseHold("CSV malformed or unsupported encoding") from exc
    if not rows_out:
        raise ParseHold("SIES snapshot has no rows")
    return rows_out
