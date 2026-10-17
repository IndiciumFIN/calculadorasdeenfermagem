#!/usr/bin/env python3
"""Checagem de duplicidades. Não copia e não escolhe lado.

Conteúdo idêntico em caminhos diferentes fica registrado como duplicata.
O mesmo nome com hashes diferentes é conflito e encerra com código 2.
"""
import hashlib
import json
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def classificar(raiz: Path) -> dict:
    por_hash: dict[str, list[str]] = {}
    por_nome: dict[str, list[tuple[str, str]]] = {}
    for caminho in raiz.rglob("*"):
        if not caminho.is_file() or any(parte.startswith(".") for parte in caminho.parts):
            continue
        digest = sha256_file(caminho)
        relativo = str(caminho.relative_to(raiz))
        por_hash.setdefault(digest, []).append(relativo)
        por_nome.setdefault(caminho.name, []).append((relativo, digest))

    duplicatas = [
        {"sha256": digest, "caminhos": caminhos, "tipo": "duplicata_identica"}
        for digest, caminhos in sorted(por_hash.items())
        if len(caminhos) > 1
    ]
    conflitos = []
    for nome, itens in sorted(por_nome.items()):
        hashes = {digest for _, digest in itens}
        if len(itens) > 1 and len(hashes) > 1:
            conflitos.append({
                "nome": nome,
                "caminhos": [relativo for relativo, _ in itens],
                "tipo": "mesmo_nome_conteudo_diferente",
            })
    return {
        "duplicatas_identicas": len(duplicatas),
        "conflitos": len(conflitos),
        "status": "FAIL" if conflitos else "PASS",
        "detalhes_duplicatas": duplicatas[:10],
        "detalhes_conflitos": conflitos[:10],
    }


def main() -> int:
    raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    if not raiz.is_dir():
        print(json.dumps({"status": "FAIL", "motivo": "diretório ausente"}, ensure_ascii=False))
        return 2
    relatorio = classificar(raiz)
    print(json.dumps(relatorio, indent=2, ensure_ascii=False))
    return 2 if relatorio["conflitos"] else 0


if __name__ == "__main__":
    sys.exit(main())
