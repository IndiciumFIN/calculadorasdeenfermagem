#!/usr/bin/env bash
# Gate: varredura de segredos com gitleaks pinado por versão e checksum (GAP-07).
set -euo pipefail
cd "$(dirname "$0")/.."

GITLEAKS_VERSION="8.30.1"
GITLEAKS_SHA256="551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb"
CACHE_DIR="${RUNNER_TEMP:-/tmp}/gitleaks-${GITLEAKS_VERSION}"
BIN="${CACHE_DIR}/gitleaks"

if [ ! -x "$BIN" ]; then
  mkdir -p "$CACHE_DIR"
  curl -sSL -o "${CACHE_DIR}/gitleaks.tar.gz" \
    "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_x64.tar.gz"
  echo "${GITLEAKS_SHA256}  ${CACHE_DIR}/gitleaks.tar.gz" | sha256sum -c -
  tar -xzf "${CACHE_DIR}/gitleaks.tar.gz" -C "$CACHE_DIR" gitleaks
fi

"$BIN" detect --source . --no-banner --redact
echo "PASS secrets"
