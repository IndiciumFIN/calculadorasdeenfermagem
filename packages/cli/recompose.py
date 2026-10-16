"""Reconstituir partes de arquivo SOMENTE com Work Order qualificada do Kernel.

Nunca executa scripts, extrai ZIPs, exclui originais, publica ou escolhe versões.
"""
import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path


def _sha(path):
    h = hashlib.sha256()
    n = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
            n += len(block)
    return h.hexdigest(), n


def reconstruir(wo, root):
    root = Path(root).resolve()
    safe = (root / 'data/legado/extracao_bruta').resolve()
    if len(wo.entradas) < 3:
        raise ValueError('manifesto e ao menos duas partes são obrigatórios')
    if len({x.id_origem for x in wo.entradas}) != len(wo.entradas):
        raise ValueError('IDs de origem repetidos')
    checked = []
    for item in wo.entradas:
        if item.classe != 'REFERENCIA' or not item.sha256:
            raise ValueError('entrada exige classe REFERENCIA e SHA-256')
        loc = (root / item.caminho).resolve()
        if not loc.is_relative_to(safe) or not loc.is_file() or loc.is_symlink():
            raise ValueError('entrada fora do staging privado')
        digest, count = _sha(loc)
        if digest != item.sha256:
            raise ValueError('hash da entrada difere da WO')
        checked.append((item, loc, count))
    manifest = json.loads(checked[0][1].read_text(encoding='utf-8'))
    specs = manifest.get('parts')
    if not isinstance(specs, list) or len(specs) != len(checked)-1 or len(specs) > 100:
        raise ValueError('quantidade de partes não coincide com manifesto')
    if manifest.get('split_method') != 'raw binary concatenation in numeric order':
        raise ValueError('método de concatenação não autorizado')
    for ix, spec in enumerate(specs):
        item, path, size = checked[ix+1]
        if path.name != spec.get('file') or item.sha256 != spec.get('sha256') or size != spec.get('bytes'):
            raise ValueError(f'parte {ix}: nome, SHA ou tamanho diverge do manifesto')
        if not path.name.endswith(f'.part-{ix:02d}'):
            raise ValueError('ordem numérica inválida')
    expected_sha = manifest.get('source_sha256')
    expected_bytes = manifest.get('source_bytes')
    target = (root / wo.parametros.get('output_path', '')).resolve()
    if (not target.is_relative_to(safe) or target.suffix.lower() != '.zip'
            or target.name != manifest.get('source_file')):
        raise ValueError('destino não é ZIP canônico permitido')
    if target.exists():
        h, n = _sha(target)
        if (h, n) != (expected_sha, expected_bytes):
            raise ValueError('destino existente divergente, intervenção humana')
        state = 'REASSEMBLED_ALREADY_PRESENT'
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.wo_', delete=False) as writer:
                tmp = Path(writer.name)
                for _, source, _ in checked[1:]:
                    with source.open('rb') as reader:
                        for block in iter(lambda: reader.read(1048576), b''):
                            writer.write(block)
                writer.flush()
                os.fsync(writer.fileno())
            h, n = _sha(tmp)
            if (h, n) != (expected_sha, expected_bytes):
                raise ValueError('SHA-256 ou tamanho do ZIP reconstruído não confere')
            os.replace(tmp, target)
            state = 'REASSEMBLED_INTEGRITY_PASS'
        finally:
            if tmp is not None and tmp.exists():
                tmp.unlink()
    with zipfile.ZipFile(target, 'r') as z:
        members = z.infolist()
        # Validar diretório central; os membros não são executados nem extraídos.
        unsafe = [x.filename for x in members if Path(x.filename.replace('\\','/')).is_absolute()
                  or '..' in Path(x.filename.replace('\\','/')).parts
                  or (x.flag_bits & 1)]
    report = {'schema':'CE-SPLIT-REASSEMBLY-1.0.0','work_order':wo.id,
              'status':state if not unsafe else 'HOLD_HUMAN',
              'expected_sha256':expected_sha,'expected_bytes':expected_bytes,
              'reconstructed_sha256':_sha(target)[0], 'members_central_directory':len(members),
              'suspicious_member_names':unsafe[:100], 'source_part_count':len(specs),
              'source_drive_ids':[x.id_origem for x in wo.entradas],
              'content_homologated':False,'published':False,'deleted':False,
              'durable_independent_backup_verified':False}
    evidence = root / 'data/grc/evidencias' / f'reconstituir_partes_{wo.id}.json'
    evidence.parent.mkdir(parents=True, exist_ok=True)
    tmp = evidence.with_suffix('.json.tmp')
    tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    os.replace(tmp,evidence)
    return report, evidence
