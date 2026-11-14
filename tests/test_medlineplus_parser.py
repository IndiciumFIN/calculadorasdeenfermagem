"""MedlinePlus XML metadata extractor regression tests; all subjects synthetic."""
from __future__ import annotations

import copy
import unittest
from xml.sax.saxutils import escape

from packages.cli.parsers.medlineplus import parse, ParseHold

SRC = "SRC-SYNTHETIC-MEDLINEPLUS"
DOC = "DOC-SYNTHETIC-MEDLINEPLUS-001"


def topic(id="101", title="Synthetic nursing topic", language="English",
          links="", groups="<group id='2'>Nursing</group>",
          site="<site url='https://example.org' title='Do-not-export'><information-category>Test</information-category></site>",
          mapped="", mesh="<mesh-heading><descriptor id='D012345'>Fake Descriptor</descriptor></mesh-heading>"):
    return (f'<health-topic id="{id}" title="{escape(title)}" '
            f'language="{language}" url="https://medlineplus.gov/topic{id}.html">'
            f'{groups}{site}{links}{mapped}{mesh}'
            f'<full-summary>SECRET_COPYRIGHTED_TEST_PAYLOAD</full-summary>'
            f'</health-topic>')


def fixture(*records, total=None, doctype=False):
    if total is None:
        total = len(records)
    header = '<?xml version="1.0" encoding="utf-8"?>'
    if doctype:
        header += '<!DOCTYPE health-topics SYSTEM "healthtopics.dtd">'
    return (header + f'<health-topics total="{total}" date-generated="11/13/2026 00:00:00">'
            + ''.join(records) + '</health-topics>')


def run(xml):
    return parse(xml, source_id=SRC, document_id=DOC)


class MedlineplusParserTests(unittest.TestCase):
    def test_one_metadata_record(self):
        row = run(fixture(topic()))[0]
        self.assertEqual(row["topic_id"], "101")
        self.assertEqual(row["date_generated"], "2026-11-13")
        self.assertEqual(row["mesh_descriptor_ids_candidate"], ["D012345"])
        self.assertEqual(row["attribution"],
                         "MedlinePlus.gov — U.S. National Library of Medicine")
        self.assertFalse(row["publication_allowed"])
        self.assertFalse(row["clinical_approved"])

    def test_external_doctype_does_not_expand_or_fetch(self):
        out = run(fixture(topic(), doctype=True))
        self.assertEqual(len(out), 1)

    def test_two_languages_and_cross_links(self):
        en = topic(mapped='<language-mapped-topic id="202" language="Spanish" '
                          'url="https://medlineplus.gov/spanish/topic202.html">Tema</language-mapped-topic>',
                   links='<related-topic id="202" url="https://medlineplus.gov/spanish/topic202.html">Tema</related-topic>')
        es = topic(id="202", title="Tema falso", language="Spanish",
                   mapped='<language-mapped-topic id="101" language="English" '
                          'url="https://medlineplus.gov/topic101.html">Nursing</language-mapped-topic>')
        result = run(fixture(en, es))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["topic_id"], "101")
        self.assertEqual(result[0]["related_topic_ids_candidate"], ["202"])
        self.assertEqual(result[0]["language_mapped_topic_id_candidate"], "202")

    def test_no_copyrighted_text_or_site_data_export(self):
        output = str(run(fixture(topic())))
        self.assertNotIn("SECRET_COPYRIGHTED_TEST_PAYLOAD", output)
        self.assertNotIn("Do-not-export", output)
        self.assertNotIn("example.org", output)

    def test_deterministic_idempotency(self):
        xml = fixture(topic())
        self.assertEqual(run(xml), run(xml))
        self.assertEqual(run(xml.encode("utf-8")), run(xml))

    def test_duplicate_or_dangling_edges_hold(self):
        examples = [
            fixture(topic(), topic(id="101")),
            fixture(topic(links='<related-topic id="999" url="https://medlineplus.gov/topic999.html">Other</related-topic>')),
            fixture(topic(mapped='<language-mapped-topic id="999" url="https://medlineplus.gov/topic999.html">Other</language-mapped-topic>')),
            fixture(topic(links='<related-topic id="101" url="https://medlineplus.gov/topic101.html">Self</related-topic>')),
        ]
        for index, payload in enumerate(examples):
            with self.subTest(index=index), self.assertRaises(ParseHold):
                run(payload)

    def test_invalid_metadata_is_rejected(self):
        inputs = [
            fixture(topic(id="not-an-id")),
            fixture(topic(language="Portuguese")),
            fixture(topic(groups="")),
            fixture(topic(site="")),
            fixture(topic(mesh='<mesh-heading><descriptor id="bad">Bad</descriptor></mesh-heading>')),
            fixture(topic()).replace("https://medlineplus.gov/topic101.html",
                                    "https://medlineplus.gov.evil.test/topic101.html"),
            fixture(topic()).replace("https://medlineplus.gov/topic101.html",
                                    "http://medlineplus.gov/topic101.html"),
            fixture(topic(), total=999),
            '<other-topics><health-topic /></other-topics>',
            '<?xml version="1.0"?><health-topics><health-topic /></health-topics>',
            '<health-topics total="1" date-generated="not-a-date">' + topic() + '</health-topics>',
        ]
        for n, payload in enumerate(inputs):
            with self.subTest(index=n), self.assertRaises(ParseHold):
                run(payload)

    def test_reject_malicious_entities_and_broken_xml(self):
        payloads = [
            b'<!DOCTYPE health-topics [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
            b'<health-topics total="1" date-generated="11/13/2026">'
            b'<health-topic id="1" title="&xxe;" /></health-topics>',
            "<health-topics>",
            "",
        ]
        for payload in payloads:
            with self.assertRaises(ParseHold):
                run(payload)

    def test_provenance_is_required(self):
        with self.assertRaises(ParseHold):
            parse(fixture(topic()), source_id="", document_id=DOC)
        with self.assertRaises(ParseHold):
            parse(fixture(topic()), source_id=SRC, document_id="")

    def test_batch_error_is_atomic(self):
        xml = fixture(topic(), topic(id="202", site=""))
        with self.assertRaises(ParseHold):
            run(xml)

    def test_large_input_not_accepted(self):
        with self.assertRaises(ParseHold):
            run("x" * (64_000_000 + 1))

    def test_source_field_is_canonical_contract(self):
        result = run(fixture(topic()))[0]
        self.assertEqual(result["source_contract"], "contracts/fontes/medlineplus.json")
        self.assertEqual(result["source_id"], SRC)
        self.assertEqual(result["document_id"], DOC)


if __name__ == "__main__":
    unittest.main()
