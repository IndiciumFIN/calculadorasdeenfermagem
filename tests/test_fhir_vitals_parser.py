"""Contract tests using only synthetic patients and observations, FHIR R4."""
from __future__ import annotations

import copy
import json
import unittest

from packages.cli.parsers.fhir import ParseHold, parse, SPEC_URI

CATEGORY = {"coding": [{"system":
    "http://terminology.hl7.org/CodeSystem/observation-category",
    "code": "vital-signs"}]}
LOINC = "http://loinc.org"
UCUM = "http://unitsofmeasure.org"
SRC = "SRC-SYNTHETIC-HL7-TEST"
DOC = "DOC-SYNTHETIC-0001"


def coding(code):
    return {"coding": [{"system": LOINC, "code": code}]}


def qty(value, unit):
    return {"value": value, "system": UCUM, "code": unit}


def example(code="8867-4", value=80, unit="/min"):
    return {
        "resourceType": "Observation", "id": "secret-synthetic-observation",
        "status": "final", "category": [copy.deepcopy(CATEGORY)],
        "code": coding(code), "subject": {"reference": "Patient/private-fixture"},
        "effectiveDateTime": "2026-11-14T09:00:00-03:00",
        "valueQuantity": qty(value, unit),
        "note": [{"text": "SENSITIVE_SYNTHETIC_ONLY"}]
    }


def bp(*, absent=False):
    obj = example("85354-9")
    obj.pop("valueQuantity")
    obj["component"] = [
        {"code": coding("8480-6"), "valueQuantity": qty(120, "mm[Hg]")},
        {"code": coding("8462-4"), **(
            {"dataAbsentReason": {"coding": [
                {"system": "http://terminology.hl7.org/CodeSystem/data-absent-reason",
                 "code": "unknown"}]}}
            if absent else {"valueQuantity": qty(80, "mm[Hg]")})},
    ]
    return obj


def run(raw):
    return parse(raw, source_id=SRC, document_id=DOC)


class FhirVitalParserTests(unittest.TestCase):
    def test_heart_rate_accepts_normalized_unit(self):
        out = run(example())[0]
        self.assertEqual(out["loinc_code"], "8867-4")
        self.assertEqual(out["measurement"], {"value": 80, "unit_code": "/min"})
        self.assertEqual(out["status"], "HOLD_HUMAN")
        self.assertFalse(out["clinical_approved"])
        self.assertFalse(out["publication_allowed"])

    def test_supported_fhir_r4_vitals(self):
        for code, value, unit in [
            ("9279-1", 18, "/min"), ("2708-6", 99, "%"),
            ("8310-5", 37, "Cel"), ("8310-5", 98.6, "[degF]"),
            ("8302-2", 170, "cm"), ("9843-4", 56, "cm"),
            ("29463-7", 68, "kg"), ("29463-7", 68000, "g"),
            ("39156-5", 23, "kg/m2"),
        ]:
            with self.subTest(code=code, unit=unit):
                self.assertEqual(run(example(code, value, unit))[0]["loinc_code"], code)

    def test_blood_pressure_components(self):
        values = run(bp())[0]["measurement"]["components"]
        self.assertEqual(values["8480-6"]["value"], 120)
        self.assertEqual(values["8462-4"]["unit_code"], "mm[Hg]")

    def test_absent_reason_for_one_bp_component(self):
        out = run(bp(absent=True))[0]
        self.assertEqual(out["measurement"]["components"]["8462-4"]["data_absent_reason"], "unknown")

    def test_absent_reason_for_single_vital(self):
        raw = example()
        raw.pop("valueQuantity")
        raw["dataAbsentReason"] = {"coding": [{"system":
            "http://terminology.hl7.org/CodeSystem/data-absent-reason",
            "code": "unknown"}]}
        self.assertEqual(run(raw)[0]["measurement"], {"data_absent_reason": "unknown"})

    def test_bundle_multiple_distinct_observations(self):
        bundle = {"resourceType": "Bundle", "type": "collection",
                  "entry": [{"resource": example()},
                            {"resource": example("8310-5", 37, "Cel")}]}
        self.assertEqual(len(run(bundle)), 2)

    def test_bytes_and_json_string_are_equivalent(self):
        raw = example()
        self.assertEqual(run(raw), run(json.dumps(raw)))
        self.assertEqual(run(raw), run(json.dumps(raw).encode()))

    def test_deterministic_same_input(self):
        self.assertEqual(run(example()), run(example()))

    def test_private_identifiers_not_in_output(self):
        out = json.dumps(run(example()))
        self.assertNotIn("private-fixture", out)
        self.assertNotIn("secret-synthetic-observation", out)
        self.assertNotIn("SENSITIVE_SYNTHETIC_ONLY", out)

    def test_reference_to_formal_spec(self):
        self.assertEqual(SPEC_URI, "https://hl7.org/fhir/R4/observation-vitalsigns.html")

    def test_malformed_values_are_holds(self):
        mutators = [
            lambda x: x.pop("status"),
            lambda x: x.update({"status": "entered-in-error"}),
            lambda x: x.update({"resourceType": "Patient"}),
            lambda x: x.update({"category": []}),
            lambda x: x.update({"category": [{"coding": None}]}),
            lambda x: x.update({"code": coding("99999-9")}),
            lambda x: x.update({"effectiveDateTime": "2026-11-14T09:00:00"}),
            lambda x: x.update({"effectiveDateTime": "bad-date"}),
            lambda x: x.update({"subject": {}}),
            lambda x: x.update({"subject": {"reference": "Practitioner/fake"}}),
            lambda x: x.update({"valueQuantity": qty(80, "kg")}),
            lambda x: x.update({"valueQuantity": qty(True, "/min")}),
            lambda x: x.update({"valueQuantity": qty(float("inf"), "/min")}),
            lambda x: x.update({"valueQuantity": qty(float("nan"), "/min")}),
            lambda x: x.pop("valueQuantity"),
            lambda x: x.update({"dataAbsentReason": {"coding": []}}),
        ]
        for n, mutation in enumerate(mutators):
            with self.subTest(case=n):
                raw = example()
                mutation(raw)
                with self.assertRaises(ParseHold):
                    run(raw)

    def test_blood_pressure_invalid_cases(self):
        for mutation in [
            lambda x: x["component"].pop(),
            lambda x: x["component"][1].update(
                {"code": coding("8480-6")}),
            lambda x: x["component"][0].update(
                {"valueQuantity": qty(120, "kg")}),
            lambda x: x.update({"valueQuantity": qty(100, "mm[Hg]")}),
        ]:
            obj = bp()
            mutation(obj)
            with self.assertRaises(ParseHold):
                run(obj)

    def test_duplicate_bundle_and_invalid_entry_rejected_atomically(self):
        raw = example()
        bundle = {"resourceType": "Bundle", "type": "collection",
                  "entry": [{"resource": raw}, {"resource": copy.deepcopy(raw)}]}
        with self.assertRaises(ParseHold):
            run(bundle)
        bundle["entry"][1]["resource"]["status"] = "entered-in-error"
        with self.assertRaises(ParseHold):
            run(bundle)

    def test_reject_unverified_provenance(self):
        with self.assertRaises(ParseHold):
            parse(example(), source_id="", document_id=DOC)
        with self.assertRaises(ParseHold):
            parse(example(), source_id=SRC, document_id="")

    def test_reject_oversized_or_corrupt_json(self):
        with self.assertRaises(ParseHold):
            run("{" + "x" * 2_000_001 + "}")
        with self.assertRaises(ParseHold):
            run("{broken")
        with self.assertRaises(ParseHold):
            run('{"resourceType":"Observation","value":NaN}')


if __name__ == "__main__":
    unittest.main()
