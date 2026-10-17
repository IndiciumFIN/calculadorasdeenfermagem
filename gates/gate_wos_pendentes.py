#!/usr/bin/env python3
"""Gate 4 — WOs PREAUTHORIZED Executados."""
import json, sys
from pathlib import Path

def main():
    status_file = Path("data/legado/status_wo.json")
    if not status_file.exists():
        print("OK: status_wo.json não existe — pipeline de WOs não iniciado")
        sys.exit(0)

    with open(status_file) as f:
        data = json.load(f)

    wos = data.get("work_orders", data.get("wos", []))
    preauth = [w for w in wos if w.get("estado", w.get("status", "")).upper() == "PREAUTHORIZED"]
    blocked_no_motivo = [
        w for w in wos
        if w.get("estado", w.get("status", "")).upper() == "BLOQUEADO"
        and not w.get("motivo")
    ]

    if preauth:
        print(f"FAIL: {len(preauth)} WOs PREAUTHORIZED pendentes:")
        for w in preauth[:5]:
            print(f"  {w.get('id', w.get('wo_id', '?'))}")
        sys.exit(2)

    if blocked_no_motivo:
        print(f"FAIL: {len(blocked_no_motivo)} WOs BLOQUEADO sem motivo:")
        for w in blocked_no_motivo[:5]:
            print(f"  {w.get('id', w.get('wo_id', '?'))}")
        sys.exit(2)

    print(f"OK: {len(wos)} WOs — 0 PREAUTHORIZED, 0 BLOQUEADO sem razão")
    sys.exit(0)

if __name__ == "__main__":
    main()
