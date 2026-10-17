"""Auditoria de inventário: exclusivamente via WO qualificada e Kernel.

Não conecta a Drive, não deduplica, não remove e não homologa o conteúdo.
Análise de metadados coletados em snapshot versionado.
"""
import hashlib
import json
import os
from pathlib import Path

RAIZES_ESPERADAS = {
    "1FDBAMQ3-WT-8l6xU0664u7QjABd0FbEH",
    "1xhNiG35r_1_Cb211b3oz5IvcCE_Ql0K7",
    "1l519_P-9o6bnQcItydKvEEDpEYeE8R8s",
    "1c9vErI_It3XwzAcAFOnbxw9V0Mn6xfB9",
}


def sha256_file(path: Path) -> str:
    hash_value = hashlib.sha256()
    with path.open("rb") as reader:
        for chunk in iter(lambda: reader.read(1024 * 1024), b""):
            hash_value.update(chunk)
    return hash_value.hexdigest()


def auditar(wo, raiz: Path):
    """Retorna (relatório, caminho). Escreve apenas evidência no workspace."""
    if len(wo.entradas) != 1:
        raise ValueError("inventário exige exatamente um snapshot por WO")
    entrada = wo.entradas[0]
    if entrada.classe != "DOCUMENTO":
        raise ValueError("inventário exige classe DOCUMENTO")
    base = raiz.resolve()
    origem = (base / entrada.caminho).resolve()
    if not origem.is_relative_to(base) or not entrada.caminho.startswith("data/grc/"):
        raise ValueError("snapshot precisa estar no diretório governado data/grc")
    if not origem.is_file():
        raise ValueError("snapshot ausente")
    obtido = sha256_file(origem)
    if obtido != entrada.sha256:
        raise ValueError("SHA-256 do snapshot diverge da Work Order")
    dados = json.loads(origem.read_text(encoding="utf-8"))
    raizes = dados.get("roots")
    if not isinstance(raizes, list) or {r.get("id") for r in raizes} != RAIZES_ESPERADAS or len(raizes) != 4:
        raise ValueError("snapshot não possui as quatro raízes autorizadas")
    totais = {"itens": 0, "zips": 0}
    grupos_candidatos = []
    detalhes = []
    for r in raizes:
        if not isinstance(r.get("scanned"), int) or r["scanned"] < 0:
            raise ValueError("contagem inválida")
        if not isinstance(r.get("may_be_partial"), bool):
            raise ValueError("completude não declarada")
        if r.get("files", 0) + r.get("folders", 0) != r["scanned"]:
            raise ValueError("soma de arquivos e pastas não reconcilia")
        zips = r.get("zip_candidates", [])
        if not isinstance(zips, list):
            raise ValueError("zips inválidos")
        for z in zips:
            if not isinstance(z.get("size_bytes"), int) or z["size_bytes"] < 0 or not z.get("id"):
                raise ValueError("ZIP sem metadados válidos")
        totais["itens"] += r["scanned"]
        totais["zips"] += len(zips)
        grupos_candidatos.extend({"root": r["label"], "name": nome, "motivo": "nome igual; SHA pendente"} for nome in r.get("duplicate_candidate_names", []))
        detalhes.append({"root": r["label"], "id": r["id"], "observados": r["scanned"],
                         "zips": len(zips), "listagem_parcial": r["may_be_partial"]})
    relato = {
        "schema": "CE-AUDIT-INVENTORY-1.0.0", "work_order": wo.id,
        "task_id": wo.task_id, "source": entrada.caminho,
        "source_sha256": obtido, "checker_id": wo.checker_id,
        "authorized_by": wo.authorized_by, "status": "PARCIAL",
        "arquivos_observados": totais["itens"], "zips_observados": totais["zips"],
        "raizes": detalhes, "duplicatas_candidatas": grupos_candidatos,
        "sha256_dos_zips": "PENDENTE",
        "profundidade_total_validada": False,
        "homologacao": False, "exclusao_autorizada": False,
        "publicacao_autorizada": False,
        "motivo": "Inventário de metadados por raiz; subpastas e paginação ainda abertas.",
    }
    destino = base / "data" / "grc" / "evidencias" / f"auditar_inventario_{wo.id}.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = destino.with_suffix(".json.tmp")
    temporario.write_text(json.dumps(relato, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporario, destino)
    return relato, destino
