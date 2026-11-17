#!/usr/bin/env python3
"""Offline release-candidate verification; never promotes to production."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

root = Path(__file__).resolve().parents[1]
suite = unittest.defaultTestLoader.discover(str(root / 'tests'), pattern='test_governed_tools.py')
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    sys.exit(2)

output_dir = root / 'docs/ecossistema/governed-tools'
output_dir.mkdir(parents=True, exist_ok=True)
excluded = {
    'docs/ecossistema/governed-tools/CHECKSUMS_v0.1.0.sha256',
    'docs/ecossistema/governed-tools/MANIFEST_v0.1.0.json',
}
# Only Git-indexed sources are admissible. Never include untracked files, caches,
# .git internals or filesystem artifacts. Fail closed outside a valid checkout.
try:
    tracked = subprocess.run(
        ['git', '-C', str(root), 'ls-files', '--cached', '-z'],
        check=True, capture_output=True,
    ).stdout.decode('utf-8').split('\0')
except (OSError, subprocess.CalledProcessError, UnicodeDecodeError) as exc:
    sys.exit(f'FAIL: unable to enumerate Git-indexed sources: {exc}')
if not tracked or not any(tracked):
    sys.exit('FAIL: empty Git index')
entries = []
for name in sorted(set(filter(None, tracked))):
    if name in excluded:
        continue
    p = root / name
    if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root.resolve()):
        sys.exit(f'FAIL: missing, symlinked or escaping tracked source: {name}')
    payload = p.read_bytes()
    entries.append({
        'path': name.replace('\\', '/'),
        'sha256': hashlib.sha256(payload).hexdigest(),
        'bytes': len(payload),
    })
manifest = {'version': '0.1.0', 'status': 'CANDIDATE_NOT_DEPLOYED', 'files': entries}
(output_dir / 'MANIFEST_v0.1.0.json').write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8'
)
(output_dir / 'CHECKSUMS_v0.1.0.sha256').write_text(
    ''.join(f"{x['sha256']}  {x['path']}\n" for x in entries), encoding='utf-8'
)
print(f'PASS {result.testsRun} tests; {len(entries)} tracked files hashed. No WO, no promotion.')
