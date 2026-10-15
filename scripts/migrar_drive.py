#!/usr/bin/env python3
"""Migração do Drive sob WO-2026_10_15_0041.

Regras:
- Não sobrescreve arquivo com mesmo SHA-256.
- Conteúdo divergente vai para quarentena.
- Não promove status.
- Exit 2 se houver conflito não resolvido.
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

WO_ID = "WO-2026_10_15_0041"
QUARENTENA = Path("data/quarentena_drive")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()

def carregar_inventario(raiz: Path) -> dict[str, str]:
    inv = {}
    for p in raiz.rglob("*"):
        if p.is_file() and not any(part.startswith(".") for part in p.parts):
            try:
                inv[sha256_file(p)] = str(p.relative_to(raiz))
            except Exception:
                continue
    return inv

def main() -> int:
    origem = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if origem is None or not origem.exists():
        print(json.dumps({"status": "FAIL", "motivo": "origem não informada ou inexistente"}))
        return 2

    raiz = Path(".")
    inventario = carregar_inventario(raiz)
    QUARENTENA.mkdir(parents=True, exist_ok=True)

    copiados = []
    quarentena = []
    rejeitados = []

    for p in origem.rglob("*"):
        if not p.is_file():
            continue
        digest = sha256_file(p)
        destino = raiz / "data" / "drive_migrado" / p.relative_to(origem)
        if digest in inventario:
            rejeitados.append({"arquivo": str(p), "sha256": digest, "motivo": "já existe"})
            continue
        if destino.exists():
            quarentena.append({"arquivo": str(p), "motivo": "nome existe com conteúdo diferente"})
            dest_q = QUARENTENA / p.name
            shutil.copy2(p, dest_q)
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, destino)
        copiados.append(str(destino.relative_to(raiz)))

    relatorio = {
        "wo": WO_ID,
        "copiados": len(copiados),
        "rejeitados": len(rejeitados),
        "quarentena": len(quarentena),
        "status": "PASS" if not quarentena else "QUARENTENA"
    }
    print(json.dumps(relatorio, indent=2, ensure_ascii=False))
    (raiz / "data" / "relatorio_migracao.json").write_text(
        json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return 0 if not quarentena else 2

if __name__ == "__main__":
    sys.exit(main())
