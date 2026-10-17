#!/usr/bin/env bash
# Gate: lint de workflows (GOV-002 / GAP-03).
# Proíbe mascaramento de falhas e exige pinagem por SHA e permissions mínimos.
set -euo pipefail
cd "$(dirname "$0")/.."

FALHAS=0

for wf in .github/workflows/*.yml .github/workflows/*.yaml; do
  [ -e "$wf" ] || continue

  # Comentários (#) são ignorados: o lint avalia apenas linhas executáveis.
  sem_comentarios=$(grep -vE '^\s*#' "$wf")

  if grep -nE '\|\|\s*(echo|true|:)' <<<"$sem_comentarios"; then
    echo "FAIL [$wf]: mascaramento de erro ('|| echo' / '|| true') é proibido (GOV-002)"
    FALHAS=1
  fi

  if grep -n 'continue-on-error' <<<"$sem_comentarios"; then
    echo "FAIL [$wf]: continue-on-error é proibido (fail-closed)"
    FALHAS=1
  fi

  if ! grep -qE '^permissions:' "$wf"; then
    echo "FAIL [$wf]: bloco 'permissions:' obrigatório (least privilege do GITHUB_TOKEN)"
    FALHAS=1
  fi

  while IFS= read -r linha; do
    ref="${linha##*@}"
    if ! [[ "$ref" =~ ^[0-9a-f]{40}([[:space:]]|$) ]]; then
      echo "FAIL [$wf]: action não pinada por SHA de 40 hex: $linha"
      FALHAS=1
    fi
  done < <(grep -E '^\s*(-\s*)?uses:' <<<"$sem_comentarios" | grep -v '\./')
done

if [ "$FALHAS" -ne 0 ]; then
  exit 2
fi
echo "PASS workflow_lint"
