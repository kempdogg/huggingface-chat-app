#!/bin/bash

# Hugging Face Chat App Installation Script for Kali Linux
# This script creates an isolated virtual environment and installs dependencies

set -euo pipefail

echo "╔════════════════════════════════════════════════════════╗"
echo "║   ☠️  Hugging Face Chat App - Kali Linux Setup  ☠️    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Optional: allow the explicit legacy system-wide pip mode
BREAK_SYSTEM_PACKAGES=""
if [[ "${1:-}" == "--break-system-packages" ]]; then
    BREAK_SYSTEM_PACKAGES="--break-system-packages"
fi

# Check if running on Kali Linux
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "${ID:-}" != "kali" && "${ID_LIKE:-}" != *"kali"* && "${ID_LIKE:-}" != *"debian"* ]]; then
        echo "⚠️  Warning: This script is optimized for Kali Linux"
        echo "   It may still work on Debian-based systems"
    fi
fi

echo "Step 1: Updating system packages..."
sudo apt-get update || true

echo ""
echo "Step 2: Installing system dependencies..."
sudo apt-get install -y \
    python3-tk \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    || true

echo ""
echo "Step 3: Creating the Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel

echo ""
echo "Step 4: Installing Python dependencies..."
python -m pip install -r requirements.txt $BREAK_SYSTEM_PACKAGES

echo ""
echo "Step 5: Creating configuration files..."

# Create .env.example if it doesn't exist
if [ ! -f .env.example ]; then
    cat > .env.example << 'EOF'
# Hugging Face API Token (optional - only for gated models)
# Get your token from: https://huggingface.co/settings/tokens
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx

# Legacy API key (optional)
HUGGINGFACE_API_KEY=your_api_key_here
EOF
    echo "✅ Created .env.example"
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created .env (copy of .env.example)"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Hugging Face token"
    echo "   nano .env"
else
    echo "✅ .env already exists"
fi

echo ""
echo "Step 6: Verifying installation..."

python << 'PYEOF'
import sys
print(f"✅ Python version: {sys.version}")

try:
    import tkinter
    print("✅ tkinter: OK")
except ImportError:
    print("❌ tkinter: FAILED - Install with: sudo apt-get install python3-tk")
    sys.exit(1)

try:
    import transformers
    print(f"✅ transformers: {transformers.__version__}")
except ImportError:
    print("❌ transformers: FAILED")
    sys.exit(1)

try:
    import torch
    print(f"✅ torch: {torch.__version__}")
except ImportError:
    print("❌ torch: FAILED")
    sys.exit(1)

try:
    import dotenv
    print("✅ python-dotenv: OK")
except ImportError:
    print("❌ python-dotenv: FAILED")
    sys.exit(1)

print("")
print("✅ All dependencies verified!")
PYEOF

echo ""
echo "Step 7: Setting up permissions..."
chmod +x main.py
chmod +x setup.sh
chmod +x install.sh
echo "✅ Made scripts executable"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║              ✅ Installation Complete! ✅              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Configure your Hugging Face token (optional):"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment:"
echo "   source .venv/bin/activate"
echo ""
echo "3. Run the application:"
echo "   python main.py"
echo ""
echo "4. On first run:"
echo "   - Accept the disclaimer"
echo "   - Select models to download (click 'Manage Models')"
echo "   - Models will download on first use (5-30 min depending on model)"
echo ""
echo "💡 Tip: To recreate the environment, remove .venv and rerun ./install.sh"
echo ""
echo "⚠️  Remember: Developer accepts NO liability for misuse!"
echo ""
