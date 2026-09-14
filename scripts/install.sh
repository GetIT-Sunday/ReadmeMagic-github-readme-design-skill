#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "Installing ReadmeMagic CLI from: ${PROJECT_DIR}"
"${PYTHON_BIN}" -m pip install --upgrade "pip>=24" "flit_core>=3.12"
"${PYTHON_BIN}" -m pip install --editable "${PROJECT_DIR}" "$@"
echo "ReadmeMagic CLI is installed. Try: readme-magic check-install"
