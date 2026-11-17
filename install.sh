#!/usr/bin/env bash
set -euo pipefail

# Kali/Debian installer for the GUI application. Python packages are installed
# system-wide here, so Kali's PEP 668 override is applied to every pip command.

if [[ ! -f /etc/os-release ]]; then
    echo "Cannot identify this operating system; install dependencies manually." >&2
    exit 1
fi
# shellcheck disable=SC1091
. /etc/os-release

if [[ "${ID:-}" != "kali" && "${ID_LIKE:-}" != *debian* && "${ID:-}" != "debian" && "${ID:-}" != "ubuntu" ]]; then
    echo "Warning: This installer is intended for Kali/Debian-based systems." >&2
fi

if ! command -v apt-get >/dev/null 2>&1; then
    echo "This installer requires apt-get. Use setup.sh or install dependencies manually." >&2
    exit 1
fi

PIP_FLAGS=()
if [[ "${ID:-}" == "kali" || "${ID_LIKE:-}" == *kali* ]]; then
    PIP_FLAGS+=(--break-system-packages)
    echo "Kali detected: pip will use --break-system-packages as requested."
fi

PYTHON_BIN=${PYTHON_BIN:-python3}
PIP_BIN=${PIP_BIN:-pip3}

printf '%s\n' "╔════════════════════════════════════════════════════════╗" \
    "║   Hugging Face Chat App - Kali/Debian Setup           ║" \
    "╚════════════════════════════════════════════════════════╝"

sudo apt-get update
sudo apt-get install -y \
    python3-tk \
    python3-pip \
    python3-dev \
    build-essential \
    git

"$PIP_BIN" install "${PIP_FLAGS[@]}" --upgrade pip setuptools wheel
"$PIP_BIN" install "${PIP_FLAGS[@]}" -r requirements.txt

if [[ ! -f .env.example ]]; then
    cat > .env.example <<'EOF'
# Hugging Face access token (optional; required for gated models/router access)
HF_TOKEN=
HUGGINGFACE_API_KEY=
EOF
fi

if [[ ! -f .env ]]; then
    cp .env.example .env
    echo "Created .env. Add your Hugging Face token there if required."
else
    echo ".env already exists; leaving it unchanged."
fi

echo "Verifying Python dependencies..."
"$PYTHON_BIN" - <<'PYEOF'
import sys
print(f"Python: {sys.version}")

checks = {
    "tkinter": "tkinter",
    "transformers": "transformers",
    "torch": "torch",
    "python-dotenv": "dotenv",
    "huggingface_hub": "huggingface_hub",
    "llama-cpp-python": "llama_cpp",
    "openai": "openai",
    "Pillow": "PIL",
    "ollama": "ollama",
}
failed = []
for label, module in checks.items():
    try:
        imported = __import__(module)
        version = getattr(imported, "__version__", "OK")
        print(f"✓ {label}: {version}")
    except Exception as exc:
        print(f"✗ {label}: {exc}")
        failed.append(label)
if failed:
    raise SystemExit("Missing or broken dependencies: " + ", ".join(failed))
PYEOF

chmod +x main.py

echo
echo "Installation complete. Start the GUI with:"
echo "  $PYTHON_BIN main.py"
echo "For GGUF downloads and setup, use ./setup.sh (virtual environment)."
echo "Install tkinter from apt, not pip: sudo apt-get install python3-tk"
