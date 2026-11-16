"""Synthetic rights composite-key and fail-closed claim lineage checks."""
import csv
import io
import json
import pathlib
import sys
import tempfile
import unittest
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from rights_claim_crosswalk import inspect


def csv_blob(rows, keys):
    buff=io.StringIO()
    writer=csv.DictWriter(buff,fieldnames=keys)
    writer.writeheader();writer.writerows(rows)
    return buff.getvalue()

class CrosswalkTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.path=pathlib.Path(self.temp.name)/'sample.zip'
        self.source={'source_id':'SYN-ORG','rights_ref':'RTS-SYN'}
        self.rights=[]
        for document in ['DOC-1','DOC-2']:
            for operation,status in [('text_extraction','APPROVED'),('public_excerpt','PENDING'),('redistribution','DENIED')]:
                self.rights.append({'rights_id':f'RTS-SYN-{operation}','source_id':'SYN-ORG',
                                    'document_version_id':document,'operation':operation,'status':status})
        self.evidence=[{'evidence_atom_id':'EV-1','document_version_id':'DOC-1',
                        'verified_against_primary':True,'fragment_sha256':'a'*64},
                       {'evidence_atom_id':'EV-2','document_version_id':'DOC-2',
                        'verified_against_primary':True,'fragment_sha256':'b'*64}]
        self.claims=[{'claim_id':'CLM-SYN-001','rights_id':'RTS-SYN','status':'CANDIDATE',
                      'clinical_release_allowed':False,'clinical_reviewer_receipt_id':None,
                      'source_evidence_atom_ids':['EV-1']},
                     {'claim_id':'CLM-SYN-002','rights_id':'RTS-SYN','status':'CANDIDATE',
                      'clinical_release_allowed':False,'clinical_reviewer_receipt_id':None,
                      'source_evidence_atom_ids':['EV-2']}]

    def tearDown(self):self.temp.cleanup()

    def write_fixture(self):
        with zipfile.ZipFile(self.path,'w') as z:
            z.writestr('pilot/registros/00_source_registry.csv',csv_blob([self.source],list(self.source)))
            z.writestr('pilot/registros/01_rights_by_operation.csv',csv_blob(self.rights,list(self.rights[0])))
            z.writestr('pilot/dados/SYN/atoms/evidence_atoms.jsonl','\n'.join(json.dumps(x) for x in self.evidence)+'\n')
            z.writestr('pilot/dados/SYN/atoms/clinical_claims_candidates.jsonl','\n'.join(json.dumps(x) for x in self.claims)+'\n')

    def test_repeated_right_id_requires_composite_document_key(self):
        self.write_fixture()
        rows,report=inspect(self.path)
        self.assertEqual(len(rows),2)
        self.assertEqual(report['rights_rows'],6)
        self.assertEqual(report['rights_id_distinct'],3)
        self.assertTrue(report['rights_composite_key_unique'])
        self.assertEqual(report['claims_redistribution_denied_in_internal_ledger'],2)
        self.assertEqual(report['claims_verified_against_primary'],0)
        self.assertTrue(any(x['code']=='PRIMARY_VERIFICATION_RECEIPT_MISSING'
                            for x in report['errors']))
        self.assertTrue(any(x['code']=='UNTRUSTED_PRIMARY_VERIFICATION_FLAG'
                            for x in report['errors']))

    def test_untrusted_true_flags_cannot_manufacture_primary_approval(self):
        self.write_fixture()
        rows,report=inspect(self.path)
        self.assertEqual(report['claims_verified_against_primary'],0)
        self.assertEqual([r['primary_source_verified'] for r in rows],
                         ['false','false'])
        self.assertEqual(sum(x['code']=='PRIMARY_VERIFICATION_RECEIPT_MISSING'
                             for x in report['errors']),2)
        self.assertFalse(report['publication_allowed'])

    def test_duplicate_zip_member_names_are_rejected(self):
        self.write_fixture()
        with zipfile.ZipFile(self.path,'a') as z:
            z.writestr('pilot/registros/00_source_registry.csv', 'forged')
        with self.assertRaises(ValueError):
            inspect(self.path)

    def test_windows_zip_paths_are_rejected(self):
        self.write_fixture()
        with zipfile.ZipFile(self.path,'a') as z:
            z.writestr('..\\\\secrets.csv', 'forged')
        with self.assertRaises(ValueError):
            inspect(self.path)

    def test_missing_evidence_is_hold(self):
        self.claims[0]['source_evidence_atom_ids']=['EV-NOT-EXISTS']
        self.write_fixture()
        _,report=inspect(self.path)
        self.assertTrue(any(x['code']=='EVIDENCE_REF_ORPHAN' for x in report['errors']))

    def test_missing_per_document_rights_is_hold(self):
        self.rights=[r for r in self.rights if not (r['document_version_id']=='DOC-2' and r['operation']=='public_excerpt')]
        self.write_fixture()
        _,report=inspect(self.path)
        self.assertTrue(any(x['code']=='RIGHTS_OPERATION_NOT_UNIQUE' for x in report['errors']))

    def test_duplicate_composite_rights_key_is_hold(self):
        self.rights.append(dict(self.rights[0]))
        self.write_fixture()
        _,report=inspect(self.path)
        self.assertFalse(report['rights_composite_key_unique'])
        self.assertTrue(report['errors'])

    def test_unverified_primary_is_hold(self):
        self.evidence[0]['verified_against_primary']=False
        self.write_fixture()
        _,report=inspect(self.path)
        self.assertEqual(report['claims_verified_against_primary'],0)
        self.assertTrue(any(x['code']=='PRIMARY_SOURCE_NOT_VERIFIED' for x in report['errors']))

    def test_missing_fragment_sha_is_hold(self):
        del self.evidence[0]['fragment_sha256']
        self.write_fixture()
        _,report=inspect(self.path)
        self.assertTrue(any(x['code']=='FRAGMENT_SHA256_UNVERIFIED' for x in report['errors']))

    def test_superseded_document_is_hold(self):
        self.evidence[0]['document_version_id']='DOC-BR-COFEN-RES-429-2012'
        self.write_fixture()
        _,report=inspect(self.path)
        self.assertEqual(report['claims_with_superseded_document'],1)
        self.assertTrue(any(x['code']=='SUPERSEDED_DOCUMENT_HOLD' for x in report['errors']))

    def test_duplicate_claim_id_is_rejected(self):
        self.claims.append(dict(self.claims[0]))
        self.write_fixture()
        with self.assertRaises(ValueError): inspect(self.path)

    def test_self_release_attempt_is_hold(self):
        self.claims[0]['clinical_release_allowed']=True
        self.write_fixture()
        _,report=inspect(self.path)
        self.assertTrue(any(x['code']=='SELF_RELEASE_RISK' for x in report['errors']))

if __name__=='__main__':unittest.main()
