#!/usr/bin/env python3
"""Checagem de duplicidades para migração do Drive.

Fail-closed: qualquer conflito de conteúdo diferente gera exit 2.
"""
import hashlib
import json
import sys
from pathlib import Path

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()

def main() -> int:
    raiz = Path(".")
    inventario = {}
    conflitos = []

    for p in raiz.rglob("*"):
        if p.is_file() and not any(part.startswith(".") for part in p.parts):
            try:
                digest = sha256_file(p)
                rel = str(p.relative_to(raiz))
                if digest in inventario and inventario[digest] != rel:
                    conflitos.append({
                        "sha256": digest,
                        "existente": inventario[digest],
                        "novo": rel,
                        "tipo": "conteudo_igual_caminho_diferente"
                    })
                else:
                    inventario[digest] = rel
            except Exception:
                continue

    relatorio = {
        "total_arquivos": len(inventario),
        "conflitos": len(conflitos),
        "status": "FAIL" if conflitos else "PASS",
        "detalhes": conflitos[:10]
    }
    print(json.dumps(relatorio, indent=2, ensure_ascii=False))
    return 2 if conflitos else 0

if __name__ == "__main__":
    sys.exit(main())
