"""Movimentação metadata-only no Drive, autorizada por WO e reconciliada pelo Kernel.

O Kernel não deleta arquivos. O adaptador autenticado executa files.update
(addParents/removeParents) SOMENTE após preflight PASS.
"""
import hashlib
import json
import os
from pathlib import Path

REGISTRY = "policies/drive_move_destinations.json"
STAGED_ROOT = "data/legado/extracao_bruta"


def sha(path: Path):
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def guard(wo, root: Path):
    root = root.resolve()
    if len(wo.entradas) != 1 or wo.entradas[0].classe != "REFERENCIA":
        raise ValueError("movimentação exige uma entrada REFERENCIA")
    entry = wo.entradas[0]
    options = wo.parametros
    registry = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
    src, dst, category = (options[k] for k in ("source_parent_id", "target_parent_id", "file_type"))
    if src not in registry["source_parents"]:
        raise ValueError("origem não autorizada pelo registro")
    if registry["type_destinations"].get(category) != dst:
        raise ValueError("destino sem autorização canônica para o tipo")
    if src == dst:
        raise ValueError("origem e destino iguais")
    if not options["expected_title"].lower().endswith("." + category.lower()):
        raise ValueError("extensão divergente")
    if options["expected_mime"] != registry["mime_by_type"][category]:
        raise ValueError("MIME fora da allowlist")
    path = (root / entry.caminho).resolve()
    safe = (root / STAGED_ROOT).resolve()
    if not path.is_relative_to(safe) or not path.is_file() or path.is_symlink():
        raise ValueError("arquivo original não está em staging autorizado")
    digest, size = sha(path)
    if digest != entry.sha256 or size != int(options["expected_bytes"]):
        raise ValueError("tamanho ou SHA-256 divergente")
    return {"entry": entry, "path": path, "sha256": digest,
            "bytes": size, "options": options, "root": root}


def preflight(wo, root: Path):
    info = guard(wo, root)
    opt = info["options"]
    report = {"schema": "CE-DRIVE-MOVE-1.0.0", "work_order": wo.id,
              "phase": "PREFLIGHT_PASS", "file_id": info["entry"].id_origem,
              "file_name": opt["expected_title"], "file_type": opt["file_type"],
              "source_parent_id": opt["source_parent_id"],
              "target_parent_id": opt["target_parent_id"],
              "sha256": info["sha256"], "bytes": info["bytes"],
              "source_preserved_as_drive_file_id": True,
              "copy_authorized": False, "deletion_authorized": False,
              "requires_connector_readback": True}
    output = info["root"] / "data/grc/evidencias" / f"move_preflight_{wo.id}.json"
    write_json(output, report)
    return report, output


def reconcile(wo, root: Path, receipt: Path):
    info = guard(wo, root)
    opt = info["options"]
    permit = info["root"] / "data/grc/evidencias" / f"move_preflight_{wo.id}.json"
    if not permit.is_file() or json.loads(permit.read_text())["phase"] != "PREFLIGHT_PASS":
        raise ValueError("preflight não encontrado")
    receipt = receipt.resolve()
    allowed = (info["root"] / "data/grc/receipts").resolve()
    if not receipt.is_relative_to(allowed) or not receipt.is_file():
        raise ValueError("recibo fora do diretório controlado")
    observed = json.loads(receipt.read_text(encoding="utf-8"))
    expected = {"work_order": wo.id, "file_id": info["entry"].id_origem,
                "source_parent_id": opt["source_parent_id"],
                "target_parent_id": opt["target_parent_id"],
                "name": opt["expected_title"], "mime_type": opt["expected_mime"],
                "bytes": info["bytes"]}
    for key, value in expected.items():
        if observed.get(key) != value:
            raise ValueError(f"readback incompatível: {key}")
    if (observed.get("before_parent_ids") != [opt["source_parent_id"]]
            or observed.get("after_parent_ids") != [opt["target_parent_id"]]
            or observed.get("postmove_sha256") != info["sha256"]
            or observed.get("connector_update_success") is not True):
        raise ValueError("mudança de parent ou SHA pós-movimento não comprovada")
    post_path = (info["root"] / observed.get("postmove_local_path", "")).resolve()
    if not post_path.is_relative_to((info["root"] / STAGED_ROOT).resolve()) or not post_path.is_file():
        raise ValueError("arquivo pós-movimento ausente")
    post_hash, post_bytes = sha(post_path)
    if post_hash != info["sha256"] or post_bytes != info["bytes"]:
        raise ValueError("fixidez pós-movimento não confere")
    output = info["root"] / "data/grc/evidencias" / f"move_confirmed_{wo.id}.json"
    report = {**expected, "phase": "MOVE_CONFIRMED", "sha256": post_hash,
              "type_folder": opt["file_type"], "connector_verified": True,
              "copy_performed": False, "delete_performed": False,
              "rollback": {"addParents": opt["source_parent_id"],
                           "removeParents": opt["target_parent_id"]}}
    write_json(output, report)
    return report, output
