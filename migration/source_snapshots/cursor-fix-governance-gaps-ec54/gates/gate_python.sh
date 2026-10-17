#!/usr/bin/env bash
# Gate: compilação e testes de regressão Python (inclui testes negativos T1–T4/T9).
set -euo pipefail
cd "$(dirname "$0")/.."

PY="$(command -v python || command -v python3)"

"$PY" -m compileall packages -q
PYTHONPATH="$(pwd)" "$PY" -m pytest tests/ -q
echo "PASS python"
