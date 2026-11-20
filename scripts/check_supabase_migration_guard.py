#!/usr/bin/env python3
"""Offline source verification only; no SQL connection or execution."""
import hashlib, json, pathlib, re, sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
CREATE=re.compile(r"\bcreate\s+table\s+if\s+not\s+exists\s+(public\.[a-z_0-9]+)",re.I)
POLICY=re.compile(r"\bcreate\s+policy\b[\s\S]*?\bfor\s+select\s+using\s*\(\s*true\s*\)",re.I)

class Hold(Exception): pass

def verify(root=ROOT):
    root=pathlib.Path(root)
    obj=json.loads((root/'docs/migration-crosswalk-supabase-ce-20261115.json').read_text(encoding='utf-8'))
    if obj.get('authorization')!='HOLD_HUMAN' or obj.get('mode')!='READ_ONLY':
        raise Hold('HOLD_UNAPPROVED_PROMOTION')
    rows=obj.get('legacy_migrations',[])
    actual=sorted(p.name for p in (root/'supabase/migrations').glob('*.sql'))
    if not rows or sorted(x['name'] for x in rows)!=actual or len(set(actual))!=len(rows):
        raise Hold('HOLD_MIGRATION_SET_DRIFT')
    for row in rows:
        name=row['name']
        if not re.fullmatch(r'\d{14}_[a-z0-9_]+\.sql',name):raise Hold('HOLD_INVALID_MIGRATION_VERSION')
        src=(root/'supabase/migrations'/name).read_bytes()
        sha=hashlib.sha256(src).hexdigest()
        git=hashlib.sha1(b'blob '+str(len(src)).encode()+b'\0'+src).hexdigest()
        if sha!=row['sha256'] or git!=row['git_blob_sha1']:raise Hold('HOLD_SOURCE_CHANGED: '+name)
        txt=src.decode('utf-8')
        if sorted(set(CREATE.findall(txt)))!=sorted(row['declared_public_tables']):
            raise Hold('HOLD_DECLARED_TABLE_DRIFT: '+name)
        if not POLICY.search(txt) or row.get('unconditional_public_read') is not True:
            raise Hold('HOLD_PUBLIC_POLICY_UNACCOUNTED: '+name)
        if row.get('decision')!='HOLD_SEMANTIC_CROSSWALK':raise Hold('HOLD_MIGRATION_APPROVAL_REQUIRED')
    return {'mode':'READ_ONLY','status':'HOLD_HUMAN','files_checked':len(rows),'may_apply':False}

if __name__=='__main__':
    try:
        print(json.dumps(verify(),ensure_ascii=False))
        print('HOLD_HUMAN: no migration execution authorized',file=sys.stderr)
        sys.exit(2)
    except (Hold,ValueError,OSError,KeyError,UnicodeError) as exc:
        print('HOLD_INVALID_SOURCE: '+str(exc),file=sys.stderr)
        sys.exit(2)
