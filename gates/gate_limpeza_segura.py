#!/usr/bin/env python3
"""Gate 5 — Limpeza Não Removeu Canônicos."""
import sys
from pathlib import Path

def main():
    errors = []
    canonical = list(Path("data/canonical/atoms").glob("*.json"))
    legado = Path("data/legado/atomos_candidatos.json")
    atomizado = Path("data/legado/extracao_bruta/atomizado")

    if not canonical:
        errors.append("data/canonical/atoms/ está vazio ou não existe")
    if not legado.exists():
        errors.append("data/legado/atomos_candidatos.json removido (deve permanecer)")
    if not atomizado.exists():
        errors.append("data/legado/extracao_bruta/atomizado/ removido (deve permanecer)")

    for dominio in ["cid10","dispositivos","epidemiologico","ferimentos","icd11",
                    "medicamentos","medlineplus","mesh","nutricao","protocolos_enfermagem",
                    "sepse","sinais_vitais","suprimentos","vacinal_brasil","vacinas"]:
        mpath = atomizado / dominio / "MANIFESTO.json"
        if not mpath.exists():
            errors.append(f"MANIFESTO.json de {dominio} removido — SHA256 lost")

    if errors:
        for e in errors:
            print(f"  {e}")
        sys.exit(2)

    print(f"OK: {len(canonical)} canônicos + 15 domínios atomizados + atomos_candidatos intactos")
    sys.exit(0)

if __name__ == "__main__":
    main()
