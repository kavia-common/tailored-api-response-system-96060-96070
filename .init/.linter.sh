#!/bin/bash
set -euo pipefail

PROJ_ROOT="/home/kavia/workspace/code-generation/tailored-api-response-system-96060-96070"
BACKEND_DIR="$PROJ_ROOT/backend"
REQ_FILE="$BACKEND_DIR/requirements.txt"
VENV_CANDIDATES=("$PROJ_ROOT/venv" "$BACKEND_DIR/venv")

cd "$BACKEND_DIR"

# Prefer python3 if available for venv creation
if command -v python3 >/dev/null 2>&1; then
  PY_BIN="python3"
else
  PY_BIN="python"
fi

# Locate or create virtual environment
VENV_DIR=""
for v in "${VENV_CANDIDATES[@]}"; do
  if [ -d "$v" ]; then
    VENV_DIR="$v"
    break
  fi
done

if [ -z "$VENV_DIR" ]; then
  "$PY_BIN" -m venv "$PROJ_ROOT/venv"
  VENV_DIR="$PROJ_ROOT/venv"
fi

# Activate venv
# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

# Ensure pip is up to date
python -m pip install -U pip >/dev/null

# Ensure dependencies / flake8 are available
if [ -f "$REQ_FILE" ]; then
  python -m pip install -r "$REQ_FILE" >/dev/null || python -m pip install flake8 >/dev/null
else
  python -m pip install flake8 >/dev/null
fi

# Run flake8 using the repo's top-level configuration
FLAKE8_CONFIG="$PROJ_ROOT/.flake8"
if [ -f "$FLAKE8_CONFIG" ]; then
  flake8 --config "$FLAKE8_CONFIG" "$BACKEND_DIR"
else
  flake8 "$BACKEND_DIR"
fi

LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi
