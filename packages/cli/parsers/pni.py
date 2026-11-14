"""PNI 2026 routine-vaccination CSV/ZIP candidate: aggregate-only, fail-closed.

Official dictionary: https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/dbbni/Dicionario_tb_ria_rotina.pdf
Data: https://dadosabertos.saude.gov.br/dataset/doses-aplicadas-pelo-programa-de-nacional-de-imunizacoes-pni-2026

NO record-level output. Patient/document identifiers never leave this function.
Only cells with >= 10 distinct source documents are returned, always HOLD.
"""
from __future__ import annotations

import csv
from datetime import date
import hashlib
import io
import json
from pathlib import PurePosixPath
import re
import stat
import zipfile

SOURCE_CONTRACT = "contracts/fontes/pni.json"
PARSER_API_VERSION = "1.0.0"
SOURCE_URI = "https://dadosabertos.saude.gov.br/dataset/doses-aplicadas-pelo-programa-de-nacional-de-imunizacoes-pni-2026"
DICTIONARY_URI = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/dbbni/Dicionario_tb_ria_rotina.pdf"
MIN_CELL_RECORDS = 10
MAX_SNAPSHOT_BYTES = 80_000_000
MAX_EXPANDED_BYTES = 100_000_000
MAX_RECORDS = 250_000
SHA_RE = re.compile(r"[0-9a-f]{64}", re.ASCII)
MONTH_RE = re.compile(r"2026-(0[1-9]|1[0-2])", re.ASCII)
CODE_RE = re.compile(r"[0-9]{1,10}", re.ASCII)
UF_RE = re.compile(r"[A-Z]{2}", re.ASCII)

# Exact 60 source field names from the Ministry of Health's published dictionary.
DICTIONARY_FIELDS = (
    "co_documento", "co_paciente", "tp_sexo_paciente", "co_raca_cor_paciente",
    "no_raca_cor_paciente", "co_municipio_paciente", "co_pais_paciente",
    "no_municipio_paciente", "no_pais_paciente", "sg_uf_paciente",
    "nu_cep_paciente", "ds_nacionalidade_paciente", "st_vida_paciente",
    "no_etnia_indigena_paciente", "co_etnia_indigena_paciente",
    "co_cnes_estabelecimento", "no_razao_social_estabelecimento",
    "no_fantasia_estalecimento", "co_municipio_estabelecimento",
    "no_municipio_estabelecimento", "sg_uf_estabelecimento",
    "co_troca_documento", "co_vacina", "sg_vacina", "dt_vacina",
    "co_dose_vacina", "ds_dose_vacina", "co_local_aplicacao",
    "ds_local_aplicacao", "co_via_administracao", "ds_via_administracao",
    "co_lote_vacina", "ds_vacina_fabricante", "dt_entrada_datalake",
    "dt_entrada_rnds", "co_sistema_origem", "ds_sistema_origem",
    "co_identificador_sistema", "st_documento", "co_estrategia_vacinacao",
    "ds_estrategia_vacinacao", "co_origem_registro", "ds_origem_registro",
    "co_vacina_grupo_atendimento", "ds_vacina_grupo_atendimento",
    "co_vacina_categoria_atendimento", "ds_vacina_categoria_atendimento",
    "co_vacina_fabricante", "ds_vacina", "ds_condicao_maternal",
    "co_tipo_estabelecimento", "ds_tipo_estabelecimento",
    "co_natureza_estabelecimento", "ds_natureza_estabelecimento",
    "nu_idade_paciente", "co_condicao_maternal", "no_uf_paciente",
    "dt_deleted", "ds_identificador_sistema", "no_uf_estabelecimento",
)
assert len(DICTIONARY_FIELDS) == len(set(DICTIONARY_FIELDS)) == 60


class ParseHold(ValueError):
    """Reject a snapshot without exporting anything from an invalid batch."""


def _manifest_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not 1 <= len(value.strip()) <= 256:
        raise ParseHold(f"{name} missing or invalid")
    return value.strip()


def _extract(raw: bytes) -> bytes:
    if not raw.startswith(b"PK"):
        return raw
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            members = archive.infolist()
            if len(members) != 1:
                raise ParseHold("expected one CSV in PNI snapshot ZIP")
            member = members[0]
            name = member.filename
            path = PurePosixPath(name)
            if (not name or member.is_dir() or path.is_absolute()
                    or len(path.parts) != 1 or ".." in path.parts
                    or "\\" in name or ":" in name or not name.lower().endswith(".csv")
                    or stat.S_ISLNK(member.external_attr >> 16) or member.flag_bits & 1):
                raise ParseHold("ZIP member path/type rejected")
            if (member.file_size <= 0 or member.file_size > MAX_EXPANDED_BYTES
                    or member.compress_size <= 0
                    or member.file_size > 500 * member.compress_size):
                raise ParseHold("ZIP expansion limits exceeded")
            data = archive.read(member)
            if len(data) != member.file_size:
                raise ParseHold("ZIP member size mismatch")
            return data
    except (zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError, EOFError) as exc:
        raise ParseHold("unreadable PNI ZIP snapshot") from exc


def parse(raw: bytes | str, *, source_id: str, document_id: str,
          snapshot_month: str, expected_sha256: str,
          encoding: str = "utf-8-sig", delimiter: str = ";") -> list[dict]:
    """Return only large aggregated cells; PII and pseudonyms are never exported.

    Input must be a trusted-manifest-pinned local snapshot. A matching SHA
    proves byte equality, NOT origin, patient deidentification, or rights.
    """
    source_id = _manifest_text(source_id, "source_id")
    document_id = _manifest_text(document_id, "document_id")
    if not isinstance(snapshot_month, str) or not MONTH_RE.fullmatch(snapshot_month):
        raise ParseHold("snapshot_month needs YYYY-MM")
    if encoding not in ("utf-8-sig", "cp1252") or delimiter not in (";", ","):
        raise ParseHold("unknown CSV encoding or delimiter")
    if not isinstance(raw, (str, bytes)):
        raise ParseHold("PNI snapshot must be raw bytes or text")
    try:
        blob = raw.encode("cp1252" if encoding == "cp1252" else "utf-8") if isinstance(raw, str) else raw
    except UnicodeError as exc:
        raise ParseHold("invalid PNI text") from exc
    if not blob or len(blob) > MAX_SNAPSHOT_BYTES:
        raise ParseHold("PNI snapshot empty or over safe input bound")
    if not isinstance(expected_sha256, str) or not SHA_RE.fullmatch(expected_sha256):
        raise ParseHold("expected_sha256 must be lowercase SHA-256")
    source_sha = hashlib.sha256(blob).hexdigest()
    if source_sha != expected_sha256:
        raise ParseHold("PNI snapshot SHA-256 mismatch")
    data = _extract(blob)
    if len(data) > MAX_EXPANDED_BYTES or bytes([0]) in data:
        raise ParseHold("PNI expanded CSV malformed")
    try:
        text = data.decode(encoding)
        reader = csv.DictReader(io.StringIO(text, newline=""),
                                delimiter=delimiter, strict=True)
        names = reader.fieldnames
        if (not isinstance(names, list) or len(names) != 60
                or set(names) != set(DICTIONARY_FIELDS)):
            raise ParseHold("PNI CSV differs from pinned 60-field dictionary")
        unique_documents: set[str] = set()
        groups: dict[tuple[str, str], int] = {}
        count = 0
        for record in reader:
            count += 1
            if count > MAX_RECORDS:
                raise ParseHold("PNI record bound exceeded")
            if None in record or any(v is None for v in record.values()):
                raise ParseHold("PNI CSV malformed row width")
            doc = record["co_documento"].strip()
            if not 1 <= len(doc) <= 256 or doc in unique_documents:
                raise ParseHold("missing or duplicate RNDS document code")
            unique_documents.add(doc)
            date_string = record["dt_vacina"].strip()
            try:
                given = date.fromisoformat(date_string)
            except ValueError as exc:
                raise ParseHold("invalid vaccination date") from exc
            if given.strftime("%Y-%m") != snapshot_month:
                raise ParseHold("PNI vaccination outside pinned snapshot month")
            vaccine = record["co_vacina"].strip()
            uf = record["sg_uf_estabelecimento"].strip()
            if not CODE_RE.fullmatch(vaccine) or not UF_RE.fullmatch(uf):
                raise ParseHold("invalid vaccine code or UF dimension")
            if any(not isinstance(x, str) or len(x) > 2048 for x in record.values()):
                raise ParseHold("PNI source field exceeds safe size bound")
            group = (uf, vaccine)
            groups[group] = groups.get(group, 0) + 1
    except (UnicodeError, csv.Error) as exc:
        raise ParseHold("PNI CSV decoding or quoting invalid") from exc
    if not count:
        raise ParseHold("PNI snapshot has no records")
    outputs = []
    for (uf, vaccine), number in sorted(groups.items()):
        if number < MIN_CELL_RECORDS:
            continue  # no count or group identifier from suppressed cells leaks
        record = {"uf_estabelecimento": uf, "co_vacina_candidate": vaccine,
                  "period": snapshot_month, "dose_records": number}
        rec_sha = hashlib.sha256(json.dumps(record, sort_keys=True,
            separators=(",", ":")).encode("utf-8")).hexdigest()
        outputs.append({
            **record, "record_sha256": rec_sha, "source_sha256": source_sha,
            "source_id": source_id, "document_id": document_id,
            "source_contract": SOURCE_CONTRACT,
            "parser": "pni", "parser_version": PARSER_API_VERSION,
            "dictionary_uri": DICTIONARY_URI, "source_uri": SOURCE_URI,
            "suppression_threshold": MIN_CELL_RECORDS,
            "no_row_level_output": True,
            "data_privacy_release_reviewed": False,
            "source_origin_verified": False, "rights_verified": False,
            "clinical_approved": False, "publication_allowed": False,
            "release_allowed": False, "status": "HOLD_HUMAN",
        })
    return outputs
