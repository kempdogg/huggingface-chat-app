#!/usr/bin/env bash
set -euo pipefail

# Create an isolated environment, install dependencies, and download models
# configured with auto_install=true in models_config.json.
PYTHON_BIN=${PYTHON_BIN:-python3}
VENV_DIR=${VENV_DIR:-.venv}

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "Python executable not found: $PYTHON_BIN" >&2
    exit 1
fi

# Apply Kali's requested PEP 668 flag to pip invocations on Kali, even though
# this script uses a virtual environment. On other systems, pip stays standard.
PIP_FLAGS=()
if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    . /etc/os-release
    if [[ "${ID:-}" == "kali" || "${ID_LIKE:-}" == *kali* ]]; then
        PIP_FLAGS+=(--break-system-packages)
        echo "Kali detected: pip will use --break-system-packages as requested."
    fi
fi

if [[ ! -d "$VENV_DIR" ]]; then
    if ! "$PYTHON_BIN" -m venv "$VENV_DIR"; then
        echo "Could not create virtual environment. On Kali/Debian install python3-venv (and the matching python3.X-venv package), then retry." >&2
        exit 1
    fi
fi

VENV_PYTHON="$VENV_DIR/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "Virtual environment Python not found at $VENV_PYTHON" >&2
    exit 1
fi

"$VENV_PYTHON" -m pip install "${PIP_FLAGS[@]}" --upgrade pip setuptools wheel
if [[ ! -f requirements.txt ]]; then
    echo "requirements.txt not found in the project directory." >&2
    exit 1
fi
"$VENV_PYTHON" -m pip install "${PIP_FLAGS[@]}" -r requirements.txt

# Run model setup with the same interpreter that installed the packages.
"$VENV_PYTHON" scripts/setup_install.py

echo "Setup complete. Activate the environment with:"
echo "  source $VENV_DIR/bin/activate"
echo "Then run: $VENV_PYTHON main.py"
