#!/usr/bin/env bash
# Local CI for Python repos (matches GitHub Actions test job).

set -euo pipefail

cd "$(dirname "$0")/.."

pick_python() {
  if command -v python >/dev/null 2>&1; then
    echo python
  elif command -v python3 >/dev/null 2>&1; then
    echo python3
  elif [[ -x .venv/bin/python ]]; then
    echo .venv/bin/python
  elif [[ -f .venv/Scripts/python.exe ]]; then
    echo .venv/Scripts/python.exe
  else
    echo python
  fi
}

PY="$(pick_python)"

echo "ci-local: syncing dev dependencies..."
"$PY" -m pip install -q -r requirements-dev.txt

"$PY" -m ruff check .
"$PY" -m pytest -q
