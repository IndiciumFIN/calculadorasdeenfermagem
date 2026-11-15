#!/usr/bin/env python3
"""Offline release-candidate verification; never promotes to production."""
import hashlib,json,subprocess,sys,unittest
from pathlib import Path
root=Path(__file__).resolve().parents[1]
suite=unittest.defaultTestLoader.discover(str(root/'tests'),pattern='test_governed_tools.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful(): sys.exit(2)
output_dir=root/'docs/ecossistema/governed-tools'
output_dir.mkdir(parents=True,exist_ok=True)
files=sorted(p for p in root.rglob('*') if p.is_file() and p.name not in ('CHECKSUMS_v0.1.0.sha256','MANIFEST_v0.1.0.json'))
entries=[{'path':str(p.relative_to(root)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in files]
manifest={'version':'0.1.0','status':'CANDIDATE_NOT_DEPLOYED','files':entries}
(output_dir/'MANIFEST_v0.1.0.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n')
(output_dir/'CHECKSUMS_v0.1.0.sha256').write_text(''.join(f"{x['sha256']}  {x['path']}\n" for x in entries))
print(f'PASS {result.testsRun} tests; {len(entries)} files hashed. No WO, no promotion.')
