#!/usr/bin/env bash
set -euo pipefail

# Install dependencies, download models marked auto_install in models_config.json,
# and create a one-command launcher.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_COMMAND="/usr/local/bin/huggingface-chat-app"

printf '%s\n' "╔════════════════════════════════════════════════════════╗" \
  "║   Hugging Face Chat App - Kali Linux Setup             ║" \
  "╚════════════════════════════════════════════════════════╝"

if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "${ID:-}" != "kali" && "${ID_LIKE:-}" != *"kali"* && "${ID_LIKE:-}" != *"debian"* ]]; then
        echo "Warning: This installer is optimized for Kali/Debian-based systems."
    fi
fi

sudo apt-get update
sudo apt-get install -y python3-tk python3-pip python3-dev build-essential git

# Debian/Kali may mark the system Python as externally managed. Use the requested
# flag so pip can install the requirements instead of failing with that error.
python3 -m pip install --break-system-packages --upgrade pip setuptools wheel
python3 -m pip install --break-system-packages -r "$SCRIPT_DIR/requirements.txt"

if [ ! -f "$SCRIPT_DIR/.env.example" ]; then
    cat > "$SCRIPT_DIR/.env.example" <<'EOF'
# Hugging Face token (optional; required only for gated models)
# Get one at https://huggingface.co/settings/tokens
HF_TOKEN=
HUGGINGFACE_API_KEY=
EOF
fi

if [ ! -f "$SCRIPT_DIR/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo "Created .env. Add HF_TOKEN there if any selected model is gated."
fi

python3 - <<'PYEOF'
import sys
try:
    import tkinter
    import transformers
    import torch
    import dotenv
    import huggingface_hub
except ImportError as exc:
    print(f"Dependency verification failed: {exc}", file=sys.stderr)
    raise SystemExit(1)
print(f"Python {sys.version.split()[0]} and application dependencies are available.")
PYEOF

# Download all models selected with auto_install=true before setup is complete.
echo "Downloading selected Hugging Face models (this may take a long time)..."
python3 "$SCRIPT_DIR/scripts/setup_install.py"

chmod +x "$SCRIPT_DIR/main.py"
launcher="$(mktemp)"
trap 'rm -f "$launcher"' EXIT
cat > "$launcher" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "$SCRIPT_DIR"
exec python3 "$SCRIPT_DIR/main.py" "\$@"
EOF
sudo install -m 755 "$launcher" "$APP_COMMAND"

printf '\nInstallation complete. Start the app with: huggingface-chat-app\n'
printf 'Configure an optional Hugging Face token in: %s/.env\n' "$SCRIPT_DIR"
printf 'Models marked auto_install=true in models_config.json have been downloaded.\n'
