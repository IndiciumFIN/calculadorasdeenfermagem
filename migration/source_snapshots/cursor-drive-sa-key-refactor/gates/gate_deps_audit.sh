#!/usr/bin/env bash
# Gate: auditoria de dependências (GAP-11). Vulnerabilidade alta ou crítica bloqueia.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "--- pip-audit"
pip-audit -r packages/cli/requirements.txt --strict

# Política: audita dependências de PRODUÇÃO em nível high (fail-closed).
# Dev tooling (eslint-config-next) carrega advisory sem correção disponível
# em braces/micromatch; não é código executado em produção. Reavaliar a cada
# atualização de dependências.
echo "--- npm audit (produção)"
npm audit --omit=dev --audit-level=high

echo "PASS deps_audit"
