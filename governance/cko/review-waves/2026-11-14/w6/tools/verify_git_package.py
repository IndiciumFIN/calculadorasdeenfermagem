from pathlib import Path
import json,hashlib
base=Path(__file__).resolve().parent.parent
m=json.loads((base/'MANIFEST_SHA256.json').read_text(encoding='utf-8'))
for a in m['files']:
 p=base/a['path'];assert p.exists(),a['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'],a['path']
assert all(not p.is_file() for p in (base/'originais').rglob('*')) if (base/'originais').exists() else True
print('Git-safe W6 manifest PASS — no source originals packaged')
