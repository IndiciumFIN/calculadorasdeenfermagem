#!/usr/bin/env python3
"""Gate 3 — Quarentena Consistente."""
import json, sys
from pathlib import Path

def main():
    qfile = Path("data/quarentena/validacao_invalida.jsonl")
    if not qfile.exists():
        print("OK: nenhuma Quarentena (pipeline limpo)")
        sys.exit(0)

    required_fields = ["motivo", "sha256_original", "arquivo"]
    sha_seen = set()
    errors = []
    count = 0

    with open(qfile) as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            count += 1
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                errors.append(f"Linha {i}: JSON inválido")
                continue
            for field in required_fields:
                if field not in r:
                    errors.append(f"Linha {i}: campo {field} ausente")
            sha = r.get("sha256_original", "")
            if sha and sha in sha_seen:
                errors.append(f"Linha {i}: SHA256 duplicado na Quarentena: {sha[:16]}...")
            sha_seen.add(sha)

    if errors:
        for e in errors[:20]:
            print(f"  {e}")
        sys.exit(2)

    print(f"OK: {count} entradas em Quarentena, 0 duplicações internas")
    sys.exit(0)

if __name__ == "__main__":
    main()
