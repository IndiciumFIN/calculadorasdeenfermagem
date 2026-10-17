"""Transporte privado autenticado Drive -> staging local, autorizado pelo Kernel.

A chamada autenticada ao conector fornece SOMENTE o arquivo montado.
Esta rotina não obtém credenciais, não apaga, não publica e não envia ao Git.
"""
import hashlib
import json
import os
import tempfile
from pathlib import Path


def _sha(path):
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024 * 1024), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def importar(wo, raiz: Path):
    if len(wo.entradas) != 1:
        raise ValueError("exige exatamente uma entrada por microfase")
    entrada = wo.entradas[0]
    if entrada.classe != "REFERENCIA":
        raise ValueError("importação exige classe REFERENCIA (sem átomo automático)")
    if wo.parametros.get("source_provider") != "google_drive":
        raise ValueError("provedor de origem não autorizado")
    mounted_root_text = os.environ.get("CE_CONNECTOR_STAGING_ROOT")
    if not mounted_root_text:
        raise ValueError("CE_CONNECTOR_STAGING_ROOT obrigatório")
    mounted_root = Path(mounted_root_text).resolve()
    rel = Path(wo.parametros.get("source_mount", ""))
    if rel.is_absolute() or ".." in rel.parts or str(rel) in ("", "."):
        raise ValueError("source_mount deve ser relativo e seguro")
    mounted = (mounted_root / rel).resolve()
    if not mounted.is_relative_to(mounted_root) or not mounted.is_file():
        raise ValueError("arquivo montado ausente ou fora do perímetro")
    base = raiz.resolve()
    allowed_dest = (base / "data/legado/extracao_bruta").resolve()
    destination = (base / entrada.caminho).resolve()
    if not destination.is_relative_to(allowed_dest):
        raise ValueError("destino fora de data/legado/extracao_bruta")
    real_sha, n_bytes = _sha(mounted)
    if real_sha != entrada.sha256:
        raise ValueError("SHA-256 da origem autenticada difere da Work Order")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        dest_sha, dest_bytes = _sha(destination)
        if dest_sha != real_sha or dest_bytes != n_bytes:
            raise ValueError("destino existente com conteúdo divergente")
        status = "JA_PRESENTE_IDEMPOTENTE"
    else:
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination.parent, prefix=".wo_", delete=False) as output:
                tmp_path = Path(output.name)
                with mounted.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        output.write(chunk)
            temp_sha, temp_bytes = _sha(tmp_path)
            if temp_sha != real_sha or temp_bytes != n_bytes:
                raise ValueError("cópia temporária não confere SHA e tamanho")
            os.replace(tmp_path, destination)
            status = "ESTAGIADO"
        finally:
            if tmp_path is not None and tmp_path.exists():
                tmp_path.unlink()
    report = {
        "schema": "CE-DRIVE-TRANSFER-1.0.0", "work_order": wo.id,
        "source_provider": "google_drive", "drive_file_id": entrada.id_origem,
        "destination": entrada.caminho, "sha256": real_sha, "bytes": n_bytes,
        "status": status, "validated_by": "Kernel.importar-drive",
        "content_homologated": False, "deletion_authorized": False,
        "git_publication_authorized": False, "original_preserved": True,
    }
    evidence = base / "data/grc/evidencias" / f"importar_drive_{wo.id}.json"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    tmp = evidence.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, evidence)
    return report, evidence
