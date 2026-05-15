#!/bin/bash

# Hugging Face Chat App Installation Script for Kali Linux
# This script sets up the environment and installs all dependencies

set -e

echo "╔════════════════════════════════════════════════════════╗"
echo "║   ☠️  Hugging Face Chat App - Kali Linux Setup  ☠️    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if running on Kali Linux
if [ -f /etc/os-release ]; then
    . /etc/os-release
    if [[ "$ID" != "kali" && "$ID_LIKE" != *"kali"* && "$ID_LIKE" != *"debian"* ]]; then
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
    python3-dev \
    build-essential \
    git \
    || true

echo ""
echo "Step 3: Upgrading pip, setuptools, and wheel..."
pip3 install --upgrade pip setuptools wheel

echo ""
echo "Step 4: Installing Python dependencies..."
pip3 install -r requirements.txt

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

# Test Python imports
python3 << 'PYEOF'
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
echo "✅ Made main.py executable"

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
echo "2. Run the application:"
echo "   python3 main.py"
echo ""
echo "3. On first run:"
echo "   - Accept the disclaimer"
echo "   - Select models to download (click 'Manage Models')"
echo "   - Models will download on first use (5-30 min depending on model)"
echo ""
echo "💡 Tips:"
echo "   - Use Phi-2 for fastest performance on slow machines"
echo "   - Keep other applications closed for better performance"
echo "   - Models are cached after first download"
echo ""
echo "⚠️  Remember: Developer accepts NO liability for misuse!"
echo ""
