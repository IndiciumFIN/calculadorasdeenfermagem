#!/usr/bin/env python3
"""Cópia do Drive recusada.

WO-2026_10_15_0041 existe só como documento. Não há arquivo em
contracts/work_orders nem tarefa qualificada de migração. Este comando
não cria diretório e não copia arquivo.
"""
import json
import sys


def main() -> int:
    print(json.dumps({
        "status": "FAIL",
        "wo": "WO-2026_10_15_0041",
        "motivo": (
            "cópia recusada. Não há contracts/work_orders/WO-2026_10_15_0041.json "
            "nem tarefa qualificada de migração."
        ),
    }, ensure_ascii=False))
    return 2


if __name__ == "__main__":
    sys.exit(main())
