#!/usr/bin/env bash
# Gate agregador: ÚNICO check obrigatório do branch protection.
# Executa todos os gates; qualquer falha, ausência ou não execução = FAIL.
# Fail-closed: não existe gate opcional nem resultado parcial.
set -uo pipefail
cd "$(dirname "$0")/.."

GATES=(
  gates/gate_workflow_lint.sh
  gates/gate_python.sh
  gates/gate_typescript.sh
  gates/gate_secrets.sh
  gates/gate_deps_audit.sh
)

declare -A RESULTADO
FALHAS=0

for gate in "${GATES[@]}"; do
  if [ ! -f "$gate" ]; then
    RESULTADO["$gate"]="AUSENTE"
    FALHAS=1
    continue
  fi
  echo ""
  echo "=== ${gate} ==="
  if bash "$gate"; then
    RESULTADO["$gate"]="PASS"
  else
    RESULTADO["$gate"]="FAIL"
    FALHAS=1
  fi
done

echo ""
echo "===== RESUMO DO GATE AGREGADOR ====="
for gate in "${GATES[@]}"; do
  echo "  ${RESULTADO[$gate]}  ${gate}"
done

if [ "$FALHAS" -ne 0 ]; then
  echo "RESULTADO: FAIL (fail-closed)"
  exit 2
fi
echo "RESULTADO: PASS"
