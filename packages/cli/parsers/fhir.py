"""FHIR R4 Vital Signs Observation parser: deterministic, narrow and fail-closed.

Normative reference: https://hl7.org/fhir/R4/observation-vitalsigns.html
Supports individual Observation and a Bundle of Observation entries; no network,
clinical inference, persistence, patient identifiers in output, or publication.
For actual patient data, a separately approved LGPD/security workflow is required.
"""
from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime
from typing import Any

PARSER_API_VERSION = "1.0.0"
SOURCE_CONTRACT = "contracts/fontes/fhir_vitais.json"
SPEC_URI = "https://hl7.org/fhir/R4/observation-vitalsigns.html"
CATEGORY_URI = "http://terminology.hl7.org/CodeSystem/observation-category"
LOINC_URI = "http://loinc.org"
UCUM_URI = "http://unitsofmeasure.org"

# Codes and units taken from the FHIR R4 Vital Signs table (not clinical ranges).
VITAL_UNITS = {
    "9279-1": frozenset({"/min"}),               # Respiratory rate
    "8867-4": frozenset({"/min"}),               # Heart rate
    "2708-6": frozenset({"%"}),                  # O2 saturation
    "8310-5": frozenset({"Cel", "[degF]"}),       # Temperature
    "8302-2": frozenset({"cm", "[in_i]"}),        # Height
    "9843-4": frozenset({"cm", "[in_i]"}),        # Head circumference
    "29463-7": frozenset({"g", "kg", "[lb_av]"}), # Weight
    "39156-5": frozenset({"kg/m2"}),             # BMI
}
BP_PANEL = "85354-9"
BP_COMPONENTS = {"8480-6": "systolic", "8462-4": "diastolic"}
MAX_INPUT_BYTES = 2_000_000
MAX_BUNDLE_ENTRIES = 256
ELIGIBLE_STATUSES = frozenset({"preliminary", "final", "amended", "corrected"})


class ParseHold(ValueError):
    """Unsupported, invalid or unverified input. Do not ingest or publish."""


def _object(value: Any, field: str) -> dict:
    if not isinstance(value, dict):
        raise ParseHold(f"{field}: expected object")
    return value


def _nonempty(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ParseHold(f"{field}: missing string")
    return value.strip()


def _code(concept: Any, system: str, field: str) -> str:
    items = _object(concept, field).get("coding")
    if not isinstance(items, list):
        raise ParseHold(f"{field}: coding absent")
    matches = [x.get("code") for x in items
               if isinstance(x, dict) and x.get("system") == system
               and isinstance(x.get("code"), str)]
    if len(set(matches)) != 1 or not matches:
        raise ParseHold(f"{field}: missing or conflicting code system")
    return matches[0]


def _time(value: Any) -> str:
    val = _nonempty(value, "effectiveDateTime")
    try:
        parsed = datetime.fromisoformat(val.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ParseHold("effectiveDateTime: invalid timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ParseHold("effectiveDateTime: timezone required")
    return val


def _quantity(q: Any, expected_units: frozenset[str], field: str) -> dict:
    obj = _object(q, field)
    num = obj.get("value")
    if not isinstance(num, (float, int)) or isinstance(num, bool) or not math.isfinite(num):
        raise ParseHold(f"{field}: value must be finite number")
    if obj.get("system") != UCUM_URI or obj.get("code") not in expected_units:
        raise ParseHold(f"{field}: UCUM system/unit mismatch")
    return {"value": num, "unit_code": obj["code"]}


def _value_or_absent(obj: dict, units: frozenset[str], field: str) -> dict:
    has_value = "valueQuantity" in obj
    has_absent = "dataAbsentReason" in obj
    if has_value == has_absent:
        raise ParseHold(f"{field}: require exactly one valueQuantity or dataAbsentReason")
    if has_value:
        return _quantity(obj["valueQuantity"], units, field)
    reason = _code(obj["dataAbsentReason"],
                   "http://terminology.hl7.org/CodeSystem/data-absent-reason",
                   f"{field}.dataAbsentReason")
    if not reason:
        raise ParseHold(f"{field}: empty dataAbsentReason")
    return {"data_absent_reason": reason}


def _normalize(obs: dict, document_id: str, source_id: str) -> dict:
    if obs.get("resourceType") != "Observation":
        raise ParseHold("FHIR resourceType must be Observation")
    if obs.get("status") not in ELIGIBLE_STATUSES:
        raise ParseHold("Observation.status: unsupported or invalid")
    categories = obs.get("category")
    if not isinstance(categories, list) or not any(
        isinstance(c, dict) and isinstance(c.get("coding"), list) and any(
            isinstance(code, dict)
            and code.get("system") == CATEGORY_URI and code.get("code") == "vital-signs"
            for code in c["coding"])
        for c in categories
    ):
        raise ParseHold("Observation.category: missing HL7 vital-signs")
    patient_ref = _nonempty(
        _object(obs.get("subject"), "subject").get("reference"),
        "subject.reference")
    if not patient_ref.startswith("Patient/") or len(patient_ref) <= len("Patient/"):
        raise ParseHold("subject.reference: only relative Patient references supported")
    timestamp = _time(obs.get("effectiveDateTime"))
    code = _code(obs.get("code"), LOINC_URI, "Observation.code")
    if code == BP_PANEL:
        if "valueQuantity" in obs or "dataAbsentReason" in obs:
            raise ParseHold("blood pressure panel must use components")
        components = obs.get("component")
        if not isinstance(components, list) or len(components) < 2:
            raise ParseHold("blood pressure needs two components")
        normalized = {}
        for comp in components:
            comp = _object(comp, "component")
            c = _code(comp.get("code"), LOINC_URI, "component.code")
            if c in normalized:
                raise ParseHold("blood pressure duplicate component")
            if c not in BP_COMPONENTS:
                raise ParseHold("unrecognized BP component; HOLD for extended profile")
            normalized[c] = _value_or_absent(comp, frozenset({"mm[Hg]"}), c)
        if set(normalized) != set(BP_COMPONENTS):
            raise ParseHold("blood pressure systolic and diastolic components required")
        measurement = {"components": normalized}
    elif code in VITAL_UNITS:
        if obs.get("component"):
            raise ParseHold("single-value vital sign cannot have components in this parser")
        measurement = _value_or_absent(obs, VITAL_UNITS[code], code)
    else:
        raise ParseHold("LOINC code outside explicitly supported FHIR R4 vital subset")

    canonical = json.dumps(obs, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False, allow_nan=False).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    # No subject.reference, observation ID, names, identifiers or free-text are emitted.
    # The content digest is pseudonymous, NOT de-identified patient data.
    return {
        "parser": "fhir_vitais", "parser_version": PARSER_API_VERSION,
        "source_contract": SOURCE_CONTRACT, "source_id": source_id,
        "document_id": document_id, "profile_version": "FHIR_R4_4.0.1",
        "record_sha256": digest, "loinc_code": code,
        "observed_at": timestamp, "measurement": measurement,
        "status": "HOLD_HUMAN", "clinical_approved": False,
        "publication_allowed": False, "release_allowed": False,
        "phi_processing_approval": "NOT_GRANTED",
    }


def parse(raw: bytes | str | dict, *, source_id: str, document_id: str) -> list[dict]:
    """Parse FHIR R4 JSON into candidates, never directly into clinical claims.

    Raises ParseHold on invalid or unsupported payload. No partial success: one
    malformed Bundle entry blocks the whole batch. Intended for synthetic data
    until external authorization/privacy and rights gates are satisfied.
    """
    source_id = _nonempty(source_id, "source_id")
    document_id = _nonempty(document_id, "document_id")
    if isinstance(raw, dict):
        obj = raw
        try:
            encoded = json.dumps(raw, sort_keys=True, allow_nan=False,
                                 separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError) as exc:
            raise ParseHold("FHIR object is not valid JSON") from exc
    else:
        if not isinstance(raw, (bytes, str)):
            raise ParseHold("FHIR JSON must be a byte string, string or object")
        encoded = raw.encode("utf-8") if isinstance(raw, str) else raw
        if len(encoded) > MAX_INPUT_BYTES:
            raise ParseHold("FHIR payload exceeds allowed limit")
        try:
            obj = json.loads(encoded, parse_constant=lambda x: (_ for _ in ()).throw(
                ParseHold(f"non-finite JSON constant: {x}")))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ParseHold("malformed FHIR JSON") from exc
    if len(encoded) > MAX_INPUT_BYTES:
        raise ParseHold("FHIR payload exceeds allowed limit")
    obj = _object(obj, "FHIR document")
    if obj.get("resourceType") == "Bundle":
        if obj.get("type") not in {"collection", "searchset"}:
            raise ParseHold("unsupported FHIR Bundle type")
        entries = obj.get("entry")
        if not isinstance(entries, list) or not 0 < len(entries) <= MAX_BUNDLE_ENTRIES:
            raise ParseHold("Bundle entries absent or excessive")
        observations = [_object(_object(x, "entry").get("resource"), "entry.resource")
                        for x in entries]
    else:
        observations = [obj]
    parsed = [_normalize(x, document_id, source_id) for x in observations]
    digests = [x["record_sha256"] for x in parsed]
    if len(digests) != len(set(digests)):
        raise ParseHold("duplicate Observation payload in batch")
    return parsed
