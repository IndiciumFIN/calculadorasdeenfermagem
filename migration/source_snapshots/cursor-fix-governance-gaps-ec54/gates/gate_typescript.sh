#!/usr/bin/env bash
# Gate: type check do frontend. Sem '|| echo': falha de tipo bloqueia (GOV-002).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d node_modules ]; then
  npm ci
fi
npx tsc --noEmit
echo "PASS typescript"
