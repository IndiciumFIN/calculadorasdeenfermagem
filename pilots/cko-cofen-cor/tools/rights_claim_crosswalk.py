#!/usr/bin/env python3
"""Read-only rights/claim evidence crosswalk of COFEN/COR pilot ZIP; no fetch or publication.
This program never copies clinical statements, source documents, or approval receipts.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, re, stat, zipfile
from collections import Counter,defaultdict
from pathlib import Path, PurePosixPath

OPS=('text_extraction','public_excerpt','redistribution')
MISSING=('schema_version','canonical_id','version','updated_at','provenance_refs',
         'object_id','assertion_key','source_ids','binding_ids','jurisdiction','applicability','review')
SUPERSEDED_DOCUMENTS={'DOC-BR-COFEN-RES-429-2012': {
    'replaced_by':'DOC-BR-COFEN-RES-754-2024',
    'official_url':'https://www.cofen.gov.br/resoluo-cofen-n-4292012/'}}
HEX_SHA256=re.compile(r'^[0-9a-f]{64}$')

def inspect(path:Path):
    with zipfile.ZipFile(path) as z:
        members=z.infolist()
        names=[m.filename for m in members]
        if not members or len(members)>2000 or len(names)!=len(set(names)):
            raise ValueError('Empty, oversized or duplicate-name ZIP manifest')
        for member in members:
            name=member.filename
            parts=PurePosixPath(name).parts
            if (not name or name.startswith('/') or '\\' in name or ':' in name
                    or '..' in parts or stat.S_ISLNK(member.external_attr >> 16)
                    or bool(member.flag_bits & 1)):
                raise ValueError('Unsafe ZIP archive member path/type')
        extracted_bytes=0
        def bounded_read(name):
            nonlocal extracted_bytes
            info=z.getinfo(name)
            if (info.file_size<0 or info.file_size>16_000_000
                or info.compress_size<0
                or (info.file_size>5_000_000 and
                    info.file_size>max(1,info.compress_size)*500)):
                raise ValueError('Oversized or suspicious compressed registry/atom')
            extracted_bytes+=info.file_size
            if extracted_bytes>64_000_000:
                raise ValueError('Registry/atom ZIP expansion quota exceeded')
            return z.read(name)
        def csv_read(suffix):
            paths=[p for p in names if p.endswith('/registros/'+suffix)]
            if len(paths)!=1:raise ValueError(f'exactly one registry required: {suffix}')
            return list(csv.DictReader(io.StringIO(bounded_read(paths[0]).decode('utf-8-sig'))))
        def jsonl(suffix):
            lines=[]
            for p in names:
                if p.endswith('/atoms/'+suffix):
                    lines.extend(json.loads(x) for x in bounded_read(p).decode('utf-8').splitlines() if x.strip())
            return lines
        sources=csv_read('00_source_registry.csv')
        rights=csv_read('01_rights_by_operation.csv')
        evidences=jsonl('evidence_atoms.jsonl')
        claims=jsonl('clinical_claims_candidates.jsonl')
    ev_by_id={r['evidence_atom_id']:r for r in evidences}
    if len(ev_by_id)!=len(evidences):raise ValueError('duplicate evidence atom id')
    source_by_right=defaultdict(set)
    for r in sources:source_by_right[r['rights_ref']].add(r['source_id'])
    claim_ids=[r['claim_id'] for r in claims]
    if len(set(claim_ids))!=len(claim_ids):
        raise ValueError('Duplicate claim ID in candidate intake')
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
        # A field supplied by the same ZIP is self-attested, not independent
        # official-source reconciliation. Never count it as a receipt.
        self_attested=[e for e in known if e.get('verified_against_primary') is True]
        unverified=known
        malformed=[e for e in known if not HEX_SHA256.fullmatch(str(e.get('fragment_sha256') or ''))]
        superseded=[d for d in docs if d in SUPERSEDED_DOCUMENTS]
        if not refs:
            findings.append({'claim_id':cid,'code':'EVIDENCE_REF_MISSING'})
        if unverified:
            findings.append({'claim_id':cid,'code':'PRIMARY_SOURCE_NOT_VERIFIED','count':len(unverified)})
            findings.append({'claim_id':cid,'code':'PRIMARY_VERIFICATION_RECEIPT_MISSING'})
        if self_attested:
            findings.append({'claim_id':cid,'code':'UNTRUSTED_PRIMARY_VERIFICATION_FLAG',
                             'count':len(self_attested)})
        if malformed:
            findings.append({'claim_id':cid,'code':'FRAGMENT_SHA256_UNVERIFIED','count':len(malformed)})
        for doc in superseded:
            findings.append({'claim_id':cid,'code':'SUPERSEDED_DOCUMENT_HOLD',
                             'document_version_id':doc,'replaced_by':SUPERSEDED_DOCUMENTS[doc]['replaced_by']})
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
            'publication_decision':'HOLD',
            'primary_source_verified':'false',
            'superseded_source':str(bool(superseded)).lower()
        })
    summary={
        'schema':'CKO-P0-CLAIM-RIGHTS-CROSSWALK-v1',
        'status':'READ_ONLY_CANDIDATE_NO_RELEASE',
        'source_zip_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'claims':len(claims),'rows':len(rows),'evidence_atoms':len(evidences),
        'rights_rows':len(rights),'rights_id_distinct':len(rights_id_count),
        'rights_composite_key_unique':not dup,
        'claims_with_resolved_evidence':sum(bool(row['evidence_refs']) and bool(row['document_version_ids']) for row in rows),
        'claims_verified_against_primary':0,
        'claims_with_superseded_document':sum(r['superseded_source']=='true' for r in rows),
        'source_supersession_registry':SUPERSEDED_DOCUMENTS,
        'claims_text_extraction_approved_in_internal_ledger':sum(r['text_extraction']=='APPROVED' for r in rows),
        'claims_public_excerpt_pending_in_internal_ledger':sum(r['public_excerpt']=='PENDING' for r in rows),
        'claims_redistribution_denied_in_internal_ledger':sum(r['redistribution']=='DENIED' for r in rows),
        'canonical_claim_schema_required_fields_missing_in_candidate':len(MISSING),
        'canonical_contract_ref':'IndiciumFIN/dev-chatgpt-workspace:contracts/cko-schemas/claim.schema.json@ccbb2fa40953557b796205f880370dcffe638e71',
        'rights_legal_approval':'NOT_VERIFIED',
        'primary_receipt_validation':'NOT_IMPLEMENTED_HOLD',
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
