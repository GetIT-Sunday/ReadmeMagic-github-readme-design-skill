#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "Installing ReadmeMagic CLI from: ${PROJECT_DIR}"
if ! "${PYTHON_BIN}" -m pip --version >/dev/null 2>&1; then
  echo "Python at ${PYTHON_BIN} has no pip. Install pip for this interpreter and retry." >&2
  exit 1
fi

# Install the package and its declared runtime dependencies into the same
# interpreter that the user selected. Avoid relying on a separately activated
# environment or on a shell entrypoint being available on PATH.
if ! "${PYTHON_BIN}" -m pip install --upgrade "pip>=24" "flit_core>=3.12"; then
  echo "Warning: could not upgrade pip/build tools; trying the available installer." >&2
fi

if ! "${PYTHON_BIN}" -m pip install --editable "${PROJECT_DIR}" "$@"; then
  echo "Editable installation is unavailable; falling back to a regular package install." >&2
  "${PYTHON_BIN}" -m pip install "${PROJECT_DIR}" "$@"
fi
echo "Verifying the installed package..."
"${PYTHON_BIN}" -m readme_magic check-install
echo "ReadmeMagic is ready. You can use either:"
echo "  readme-magic optimize --project-path ."
echo "  ${PYTHON_BIN} -m readme_magic optimize --project-path ."
