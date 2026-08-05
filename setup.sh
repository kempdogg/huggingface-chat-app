#!/usr/bin/env bash
set -euo pipefail

# setup.sh - Set up virtualenv, install deps, and auto-download models listed in models_config.json
# Usage: ./setup.sh

PYTHON_BIN=${PYTHON_BIN:-python3}
VENV_DIR=".venv"

# 1) create virtualenv
$PYTHON_BIN -m venv "$VENV_DIR" || true
. "$VENV_DIR/bin/activate"

pip install --upgrade pip
if [ -f requirements.txt ]; then
  pip install -r requirements.txt || pip install huggingface_hub llama-cpp-python
else
  pip install huggingface_hub llama-cpp-python
fi

# 2) run the python setup installer which downloads models and updates configs
python3 scripts/setup_install.py

echo "Setup complete. Models (if auto_install=true) should be in ./models/* and models_config.json updated with local_path entries."

echo "Next: edit .env if you want to override MODEL_PATH_<key> entries, then run: python3 main.py"
