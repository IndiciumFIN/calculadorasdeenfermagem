"""ANVISA official device registry CSV; synthetic negative and privacy fixtures."""
import hashlib
import unittest

from packages.cli.parsers.anvisa_dev import parse, ParseHold, REQUIRED, SOURCE_CONTRACT

SRC="SRC-SYNTHETIC-ANVISA-DEV"
DOC="DOC-SYNTHETIC-ANVISA-DEV"
HEAD=sorted(REQUIRED)

def record(reg="80000000000",process="25351.123456/2024-03",risk="II",
           maker="DO_NOT_EXPORT_MANUFACTURER",country="BR",cnpj="00000000000191"):
    return {
        "NUMERO_REGISTRO_CADASTRO":reg,
        "NUMERO_PROCESSO":process,
        "NOME_TECNICO":"DO_NOT_EXPORT_TECH_NAME",
        "CLASSE_RISCO":risk,
        "NOME_COMERCIAL":"DO_NOT_EXPORT_TRADE_NAME",
        "CNPJ_DETENTOR_REGISTRO_CADASTRO":cnpj,
        "DETENTOR_REGISTRO_CADASTRO":"DO_NOT_EXPORT_OWNER_NAME",
        "NOME_FABRICANTE":maker,
        "NOME_PAIS_FABRIC":country,
        "DT_PUB_REGISTRO_CADASTRO":"01/01/2024",
        "VALIDADE_REGISTRO_CADASTRO":"VIGENTE",
    }

def csvdata(*records, header=None):
    columns=HEAD if header is None else header
    return (";".join(columns)+"\r\n"+
            "".join(";".join(r.get(x,"") for x in columns)+"\r\n" for r in (records or (record(),)))).encode("cp1252")

def run(blob,**options):
    if isinstance(blob,str):blob=blob.encode("cp1252")
    return parse(blob,source_id=options.get("source_id",SRC),
                 document_id=options.get("document_id",DOC),
                 captured_at=options.get("captured_at","2026-11-14T11:57:00-03:00"),
                 expected_sha256=options.get("expected_sha256",hashlib.sha256(blob).hexdigest()),
                 encoding=options.get("encoding","cp1252"))

class DeviceRegistryTests(unittest.TestCase):
    def test_metadata_only_and_source_hold(self):
        out=run(csvdata())[0]
        self.assertEqual(out["registration_number_candidate"],"80000000000")
        self.assertEqual(out["risk_class_declared_candidate"],"II")
        self.assertEqual(out["source_contract"],SOURCE_CONTRACT)
        self.assertEqual(out["status"],"HOLD_HUMAN")
        for k in ("source_origin_verified","registry_current_verified","rights_verified",
                  "clinical_approved","publication_allowed","release_allowed"):
            self.assertFalse(out[k])
        for secret in ("DO_NOT_EXPORT_TECH_NAME","DO_NOT_EXPORT_TRADE_NAME",
                       "DO_NOT_EXPORT_MANUFACTURER","DO_NOT_EXPORT_OWNER_NAME"):
            self.assertNotIn(secret,str(out))

    def test_distinct_manufacturers_preserved(self):
        data=run(csvdata(record(maker="FabricanteA"),record(maker="FabricanteB")))
        self.assertEqual(len(data),2)
        self.assertNotEqual(data[0]["manufacturer_identity_sha256"],
                            data[1]["manufacturer_identity_sha256"])
        self.assertEqual([x["source_occurrence_index"] for x in data],[1,1])

    def test_exact_repeated_record_occurrence_preserved(self):
        rows=run(csvdata(record(),record()))
        self.assertEqual([x["source_occurrence_index"] for x in rows],[1,2])

    def test_bad_codes_and_missing_values_are_rejected_atomically(self):
        cases=[
            ("NUMERO_REGISTRO_CADASTRO","BAD"),
            ("NUMERO_PROCESSO","BAD"),
            ("CLASSE_RISCO","V"),
            ("CLASSE_RISCO",""),
            ("CNPJ_DETENTOR_REGISTRO_CADASTRO","not-a-cnpj"),
            ("NOME_TECNICO",""),
            ("NOME_COMERCIAL",""),
        ]
        for k,v in cases:
            with self.subTest(k=k,v=v),self.assertRaises(ParseHold):
                row=record()
                row[k]=v
                run(csvdata(record(),row))

    def test_digest_and_capture_bound(self):
        for args in (
            {"expected_sha256":"0"*64},{"expected_sha256":"INVALID"},
            {"captured_at":"2026-11-14T11:00:00"},
            {"captured_at":"INVALID"},{"source_id":""},{"document_id":""},
            {"encoding":"utf-16"},
        ):
            with self.subTest(args=args),self.assertRaises(ParseHold):
                run(csvdata(),**args)

    def test_malformed_headers_and_lines_hold(self):
        for raw in (
            b"",b"\x00",b"invalid",b"\xff",
            csvdata(header=HEAD[:-1]),
            csvdata(header=HEAD+["UNTRUSTED_EXTRA"]),
            csvdata().replace(b"\r\n",b"\r\nUNQUOTED;BAD\r\n",1)
        ):
            with self.subTest(raw=raw[:20]),self.assertRaises(ParseHold):
                run(raw)

    def test_source_flag_spoofing_cannot_unlock(self):
        row=record(maker="clinical_approved=true")
        result=run(csvdata(row))[0]
        self.assertFalse(result["clinical_approved"])
        self.assertFalse(result["publication_allowed"])

if __name__=="__main__":
    unittest.main()
