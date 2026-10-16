"""Reassembly under explicit WO, fail closed on hash and order."""
import hashlib
import io
import json
import zipfile
from pathlib import Path
from types import SimpleNamespace
import pytest
from packages.cli.recompose import reconstruir
from packages.cli.pep import RAIZ, carregar_wo


def test_qualified_real_wo_contract():
    wo = carregar_wo(RAIZ / "contracts/work_orders/WO-2026_10_16_0232.json")
    assert wo.task_type == "reconstituir-partes"
    assert len(wo.entradas) == 4
    assert wo.checker_id != wo.authorized_by


def _synthetic(tmp_path):
    content = io.BytesIO()
    with zipfile.ZipFile(content, 'w') as z:
        z.writestr('a.txt', b'A')
        z.writestr('b.txt', b'B')
    payload=content.getvalue()
    parts=[payload[:30], payload[30:60], payload[60:]]
    root=tmp_path
    base=Path('data/legado/extracao_bruta/test')
    specs=[]
    entries=[]
    for i, blob in enumerate(parts):
        name=f'example.zip.part-{i:02d}'
        path=root/base/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(blob)
        digest=hashlib.sha256(blob).hexdigest()
        specs.append({'file':name,'bytes':len(blob),'sha256':digest})
        entries.append(SimpleNamespace(id_origem=f'drivepart{i}',caminho=str(base/name),classe='REFERENCIA',sha256=digest))
    manifest={'source_file':'example.zip','source_bytes':len(payload),'source_sha256':hashlib.sha256(payload).hexdigest(),
              'split_method':'raw binary concatenation in numeric order','parts':specs}
    mp=root/base/'manifest.json'
    mp.write_text(json.dumps(manifest))
    entries.insert(0,SimpleNamespace(id_origem='drive-manifest',caminho=str(base/'manifest.json'),
                                     classe='REFERENCIA',sha256=hashlib.sha256(mp.read_bytes()).hexdigest()))
    wo=SimpleNamespace(id='WO-2026_10_16_0232',entradas=entries,parametros={'output_path':str(base/'assembled/example.zip')})
    return wo, root


def test_reassemble_and_idempotence(tmp_path):
    wo,root=_synthetic(tmp_path)
    report,evidence=reconstruir(wo,root)
    assert report['status']=='REASSEMBLED_INTEGRITY_PASS'
    assert report['members_central_directory']==2
    assert evidence.is_file()
    again,_=reconstruir(wo,root)
    assert again['status']=='REASSEMBLED_ALREADY_PRESENT'
    assert again['published'] is False
    assert again['deleted'] is False


def test_tampered_part_fails_closed(tmp_path):
    wo,root=_synthetic(tmp_path)
    p=root/wo.entradas[1].caminho
    p.write_bytes(p.read_bytes()+b'bad')
    with pytest.raises(ValueError,match='hash da entrada'):
        reconstruir(wo,root)
    assert not (root/wo.parametros['output_path']).exists()
