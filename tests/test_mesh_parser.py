"""NLM MeSH Descriptor XML tests, only synthetic terminology records."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from packages.cli.parsers.mesh import ParseHold, parse

SRC = "SRC-TEST-MESH"
DOC = "DOC-TEST-MESH-2026"


def descriptor(uid="D000001", title="Synthetic concept",
               concept_id="M0000001", preferred="Y", trees="<TreeNumber>A01.111</TreeNumber>",
               related="", extra=""):
    return (f'<DescriptorRecord DescriptorClass="1">'
            f'<DescriptorUI>{uid}</DescriptorUI>'
            f'<DescriptorName><String>{title}</String></DescriptorName>'
            f'<Annotation>LICENSED_TEXT_NOT_FOR_OUTPUT</Annotation>'
            f'<ConceptList><Concept PreferredConceptYN="{preferred}">'
            f'<ConceptUI>{concept_id}</ConceptUI>'
            f'<ConceptName><String>{title}</String></ConceptName>'
            f'<ScopeNote>PRIVATE_SYNTHETIC_SCOPE_NOTE</ScopeNote>'
            f'<TermList><Term><TermUI>T000001</TermUI>'
            f'<String>NOT_FOR_EXPORT_SYNONYM</String></Term></TermList>'
            f'</Concept></ConceptList>'
            f'<TreeNumberList>{trees}</TreeNumberList>{related}{extra}'
            f'</DescriptorRecord>')


def xml(*records, doctype=False):
    pre = '<?xml version="1.0" encoding="UTF-8"?>'
    if doctype:
        pre += '<!DOCTYPE DescriptorRecordSet SYSTEM "desc2026.dtd">'
    return pre + '<DescriptorRecordSet>' + ''.join(records) + '</DescriptorRecordSet>'


def run(value, **kwargs):
    return parse(value, source_id=SRC, document_id=DOC,
                 production_year=2026, **kwargs)


class MeshParserTests(unittest.TestCase):
    def test_descriptor_metadata_extracted_without_notes(self):
        row = run(xml(descriptor()))[0]
        self.assertEqual(row["descriptor_ui"], "D000001")
        self.assertEqual(row["concept_uids_candidate"], ["M0000001"])
        self.assertEqual(row["tree_numbers_candidate"], ["A01.111"])
        self.assertEqual(row["source_contract"], "contracts/fontes/mesh.json")
        self.assertEqual(row["production_year_declared"], 2026)
        self.assertIs(row["production_year_verified"], False)
        self.assertIs(row["publication_allowed"], False)

    def test_no_scope_note_or_synonym_reused(self):
        output = str(run(xml(descriptor())))
        for forbidden in ("LICENSED_TEXT_NOT_FOR_OUTPUT",
                          "PRIVATE_SYNTHETIC_SCOPE_NOTE", "NOT_FOR_EXPORT_SYNONYM"):
            self.assertNotIn(forbidden, output)

    def test_stream_file_and_memory_are_equivalent(self):
        payload = xml(descriptor(), doctype=True)
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / "mesh.xml"
            file.write_text(payload, encoding="utf-8")
            self.assertEqual(run(file), run(payload))
            self.assertEqual(run(payload.encode("utf-8")), run(payload))

    def test_two_related_descriptors(self):
        rel = ('<SeeRelatedDescriptorList><SeeRelatedDescriptor>'
               '<DescriptorReferredTo><DescriptorUI>D000002</DescriptorUI>'
               '<DescriptorName><String>Two</String></DescriptorName>'
               '</DescriptorReferredTo></SeeRelatedDescriptor></SeeRelatedDescriptorList>')
        result = run(xml(descriptor(related=rel),
                         descriptor(uid="D000002", title="Two", concept_id="M0000002")))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["see_related_descriptor_ids_candidate"], ["D000002"])

    def test_deterministic_record_ids(self):
        sample = xml(descriptor())
        self.assertEqual(run(sample), run(sample))

    def test_orphan_related_reference_rejected(self):
        rel = ('<SeeRelatedDescriptor><DescriptorReferredTo>'
               '<DescriptorUI>D999999</DescriptorUI>'
               '</DescriptorReferredTo></SeeRelatedDescriptor>')
        with self.assertRaises(ParseHold):
            run(xml(descriptor(related=rel)))
        # Explicit offline partial-dataset mode still marks references as candidates.
        out = run(xml(descriptor(related=rel)), verify_related=False)[0]
        self.assertIs(out["publication_allowed"], False)

    def test_bad_record_inputs_rejected(self):
        bad = [
            descriptor(uid="X000001"),
            descriptor(concept_id="bad"),
            descriptor(preferred="N"),
            descriptor(trees="<TreeNumber>A..000</TreeNumber>"),
            descriptor(trees="<TreeNumber>A01</TreeNumber><TreeNumber>A01</TreeNumber>"),
            descriptor(uid="D000001") + descriptor(uid="D000001", concept_id="M0000002"),
            descriptor(extra='<ConceptList></ConceptList>',
                       preferred="N"),
            descriptor(extra='<SeeRelatedDescriptor><DescriptorReferredTo>'
                             '<DescriptorUI>D000001</DescriptorUI>'
                             '</DescriptorReferredTo></SeeRelatedDescriptor>'),
        ]
        for idx, fragment in enumerate(bad):
            with self.subTest(case=idx), self.assertRaises(ParseHold):
                run(xml(fragment))

    def test_unsafe_xml_and_wrong_root_rejected(self):
        inputs = [
            '<?xml version="1.0"?><OtherRecordSet/>',
            "<DescriptorRecordSet>",
            "<DescriptorRecordSet></DescriptorRecordSet>",
            '<!DOCTYPE DescriptorRecordSet [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
            '<DescriptorRecordSet><DescriptorRecord><DescriptorName>'
            '<String>&xxe;</String></DescriptorName></DescriptorRecord></DescriptorRecordSet>',
        ]
        for text in inputs:
            with self.assertRaises(ParseHold):
                run(text)

    def test_source_provenance_and_release_year_required(self):
        payload = xml(descriptor())
        with self.assertRaises(ParseHold):
            parse(payload, source_id="", document_id=DOC, production_year=2026)
        with self.assertRaises(ParseHold):
            parse(payload, source_id=SRC, document_id="", production_year=2026)
        with self.assertRaises(ParseHold):
            parse(payload, source_id=SRC, document_id=DOC, production_year=True)
        with self.assertRaises(ParseHold):
            parse(payload, source_id=SRC, document_id=DOC, production_year=0)


if __name__ == "__main__":
    unittest.main()
