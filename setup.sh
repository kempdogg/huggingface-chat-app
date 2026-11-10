#!/usr/bin/env bash
set -euo pipefail

# Optional standalone setup entry point. Installs the Python requirements into
# a virtual environment and downloads selected models immediately.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="$SCRIPT_DIR/.venv"

"$PYTHON_BIN" -m venv "$VENV_DIR"
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r "$SCRIPT_DIR/requirements.txt"

if [ ! -f "$SCRIPT_DIR/.env" ] && [ -f "$SCRIPT_DIR/.env.example" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
fi

"$VENV_DIR/bin/python" "$SCRIPT_DIR/scripts/setup_install.py"
echo "Setup complete. Launch with: $VENV_DIR/bin/python $SCRIPT_DIR/main.py"
