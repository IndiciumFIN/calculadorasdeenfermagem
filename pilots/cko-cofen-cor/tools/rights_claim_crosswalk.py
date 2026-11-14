#!/usr/bin/env python3
"""Read-only rights/claim evidence crosswalk of COFEN/COR pilot ZIP; no fetch or publication.
This program never copies clinical statements, source documents, or approval receipts.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, zipfile
from collections import Counter,defaultdict
from pathlib import Path

OPS=('text_extraction','public_excerpt','redistribution')
MISSING=('schema_version','canonical_id','version','updated_at','provenance_refs',
         'object_id','assertion_key','source_ids','binding_ids','jurisdiction','applicability','review')

def inspect(path:Path):
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        assert all(not name.startswith('/') and '..' not in Path(name).parts for name in names)
        def csv_read(suffix):
            paths=[p for p in names if p.endswith('/registros/'+suffix)]
            if len(paths)!=1:raise ValueError(f'exactly one registry required: {suffix}')
            return list(csv.DictReader(io.StringIO(z.read(paths[0]).decode('utf-8-sig'))))
        def jsonl(suffix):
            lines=[]
            for p in names:
                if p.endswith('/atoms/'+suffix):
                    lines.extend(json.loads(x) for x in z.read(p).decode('utf-8').splitlines() if x.strip())
            return lines
        sources=csv_read('00_source_registry.csv')
        rights=csv_read('01_rights_by_operation.csv')
        evidences=jsonl('evidence_atoms.jsonl')
        claims=jsonl('clinical_claims_candidates.jsonl')
    ev_by_id={r['evidence_atom_id']:r for r in evidences}
    if len(ev_by_id)!=len(evidences):raise ValueError('duplicate evidence atom id')
    source_by_right=defaultdict(set)
    for r in sources:source_by_right[r['rights_ref']].add(r['source_id'])
    rights_by_doc_op=defaultdict(list)
    rights_id_count=Counter()
    for r in rights:
        rights_by_doc_op[(r['source_id'],r['document_version_id'],r['operation'])].append(r)
        rights_id_count[r['rights_id']]+=1
    dup=[key for key,rs in rights_by_doc_op.items() if len(rs)!=1]
    rows=[];findings=[]
    for r in sorted(claims,key=lambda x:x['claim_id']):
        cid=r['claim_id']
        refs=r['source_evidence_atom_ids']
        known=[ev_by_id[k] for k in refs if k in ev_by_id]
        missing=[k for k in refs if k not in ev_by_id]
        srcs=source_by_right[r['rights_id']]
        docs=sorted({e['document_version_id'] for e in known})
        operation_status={}
        for op in OPS:
            status=[]
            for src in srcs:
                for doc in docs:
                    hits=rights_by_doc_op[(src,doc,op)]
                    status+= [x['status'] for x in hits]
                    if len(hits)!=1:findings.append({'claim_id':cid,'code':'RIGHTS_OPERATION_NOT_UNIQUE','operation':op})
            operation_status[op]='|'.join(sorted(set(status))) if status else 'SOURCE_MISSING'
        if missing:findings.append({'claim_id':cid,'code':'EVIDENCE_REF_ORPHAN','count':len(missing)})
        if len(srcs)!=1:findings.append({'claim_id':cid,'code':'SOURCE_RIGHTS_REF_AMBIGUOUS','count':len(srcs)})
        if r.get('clinical_release_allowed') is not False or r.get('clinical_reviewer_receipt_id') is not None:
            findings.append({'claim_id':cid,'code':'SELF_RELEASE_RISK'})
        rows.append({
            'claim_candidate_id':cid,
            'evidence_refs':'|'.join(refs),
            'document_version_ids':'|'.join(docs),
            'source_ids':'|'.join(sorted(srcs)),
            'source_level_rights_ref':r['rights_id'],
            'text_extraction':operation_status['text_extraction'],
            'public_excerpt':operation_status['public_excerpt'],
            'redistribution':operation_status['redistribution'],
            'claim_status':r['status'],
            'clinical_release_allowed':str(r['clinical_release_allowed']).lower(),
            'canonical_claim_id':'',
            'canonical_missing_fields':'|'.join(MISSING),
            'semantic_crosswalk':'HOLD_UNVERIFIED',
            'publication_decision':'HOLD'
        })
    summary={
        'schema':'CKO-P0-CLAIM-RIGHTS-CROSSWALK-v1',
        'status':'READ_ONLY_CANDIDATE_NO_RELEASE',
        'source_zip_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'claims':len(claims),'rows':len(rows),'evidence_atoms':len(evidences),
        'rights_rows':len(rights),'rights_id_distinct':len(rights_id_count),
        'rights_composite_key_unique':not dup,
        'claims_with_resolved_evidence':sum(bool(row['evidence_refs']) and bool(row['document_version_ids']) for row in rows),
        'claims_text_extraction_approved_in_internal_ledger':sum(r['text_extraction']=='APPROVED' for r in rows),
        'claims_public_excerpt_pending_in_internal_ledger':sum(r['public_excerpt']=='PENDING' for r in rows),
        'claims_redistribution_denied_in_internal_ledger':sum(r['redistribution']=='DENIED' for r in rows),
        'canonical_claim_schema_required_fields_missing_in_candidate':len(MISSING),
        'canonical_contract_ref':'IndiciumFIN/dev-chatgpt-workspace:contracts/cko-schemas/claim.schema.json@ccbb2fa40953557b796205f880370dcffe638e71',
        'rights_legal_approval':'NOT_VERIFIED',
        'clinical_approval':'NOT_VERIFIED',
        'publication_allowed':False,
        'errors':findings
    }
    return rows,summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--output-dir',required=True,type=Path)
    a=p.parse_args()
    rows,summary=inspect(a.input)
    a.output_dir.mkdir(parents=True,exist_ok=True)
    path=a.output_dir/'P0_CKO_CLAIM_RIGHTS_CROSSWALK_23.csv'
    with path.open('w',newline='',encoding='utf-8-sig') as fh:
        writer=csv.DictWriter(fh,fieldnames=list(rows[0]),delimiter=';')
        writer.writeheader();writer.writerows(rows)
    (a.output_dir/'P0_CKO_CLAIM_RIGHTS_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='errors'},ensure_ascii=False))
    return 0 if not summary['errors'] and summary['rights_composite_key_unique'] else 2

if __name__=='__main__':raise SystemExit(main())
