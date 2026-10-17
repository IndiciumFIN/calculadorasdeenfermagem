#!/usr/bin/env python3
"""Gate 2 — Corpus Canonical Não Vazio + validação AtomoBlindado."""
import json, sys
from pathlib import Path

def main():
    atoms_dir = Path("data/canonical/atoms")
    if not atoms_dir.exists():
        print("FAIL: data/canonical/atoms/ não existe")
        sys.exit(2)

    atoms = list(atoms_dir.glob("*.json"))
    if not atoms:
        print("FAIL: corpus vazio — 0 átomos canônicos")
        sys.exit(2)

    print(f"Atomos encontrados: {len(atoms)}")

    # Validação básica de schema
    errors = []
    for p in atoms:
        try:
            data = json.loads(p.read_text())
            if not isinstance(data, dict):
                errors.append(f"{p.name}: não é dict")
                continue
            # Verificar campos mínimos de AtomoBlindado
            required = ["id", "sha256", "fonte", "texto_regra"]
            missing = [f for f in required if f not in data]
            if missing:
                errors.append(f"{p.name}: campos faltando: {missing}")
        except json.JSONDecodeError as e:
            errors.append(f"{p.name}: JSON inválido: {e}")
        except Exception as e:
            errors.append(f"{p.name}: erro: {e}")

    if errors:
        print(f"FAIL: {len(errors)} átomos inválidos:")
        for e in errors[:10]:
            print(f"  {e}")
        sys.exit(2)

    print(f"OK: {len(atoms)} átomos canônicos validados")
    sys.exit(0)

if __name__ == "__main__":
    main()
