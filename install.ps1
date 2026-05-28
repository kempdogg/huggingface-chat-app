# Hugging Face Chat App Installation Script for Windows (PowerShell)
# Run with: powershell -ExecutionPolicy Bypass -File install.ps1

param(
    [switch]$SkipPauseOnError = $false
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Hugging Face Chat App - Windows Setup (PowerShell)  ║" -ForegroundColor Cyan
Write-Host "║   Python AI Models - Local Inference on CPU            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 Please install Python from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: During installation, check 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host ""
    if (-not $SkipPauseOnError) { Read-Host "Press Enter to exit" }
    exit 1
}

# Check Python version (3.8+)
try {
    python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: Python 3.8+ is required" -ForegroundColor Red
        Write-Host ""
        Write-Host "Your Python version: $pythonVersion" -ForegroundColor Yellow
        Write-Host "Please upgrade from: https://www.python.org/downloads/" -ForegroundColor Yellow
        Write-Host ""
        if (-not $SkipPauseOnError) { Read-Host "Press Enter to exit" }
        exit 1
    }
} catch {
    Write-Host "⚠️  Warning: Could not verify Python version" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 1: Upgrading pip, setuptools, and wheel..." -ForegroundColor Cyan
python -m pip install --upgrade pip setuptools wheel
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to upgrade pip" -ForegroundColor Red
    if (-not $SkipPauseOnError) { Read-Host "Press Enter to exit" }
    exit 1
}
Write-Host "✅ pip, setuptools, and wheel upgraded" -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Installing Python dependencies..." -ForegroundColor Cyan
Write-Host "This may take several minutes on first run..." -ForegroundColor Yellow
Write-Host ""
python -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Yellow
    Write-Host "- Check your internet connection" -ForegroundColor Yellow
    Write-Host "- Try running PowerShell as Administrator" -ForegroundColor Yellow
    Write-Host "- Clear pip cache: pip cache purge" -ForegroundColor Yellow
    Write-Host ""
    if (-not $SkipPauseOnError) { Read-Host "Press Enter to exit" }
    exit 1
}
Write-Host "✅ Python dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Creating configuration files..." -ForegroundColor Cyan

if (-not (Test-Path ".env.example")) {
    @"
# Hugging Face API Token (optional - only for gated models)
# Get your token from: https://huggingface.co/settings/tokens
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx

# Legacy API key (optional)
HUGGINGFACE_API_KEY=your_api_key_here
"@ | Out-File -FilePath ".env.example" -Encoding UTF8
    Write-Host "✅ Created .env.example" -ForegroundColor Green
} else {
    Write-Host "✅ .env.example already exists" -ForegroundColor Green
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Created .env (copy of .env.example)" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Edit .env and add your Hugging Face token (optional)" -ForegroundColor Yellow
    Write-Host "   notepad .env" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 4: Verifying installation..." -ForegroundColor Cyan
Write-Host ""

$verificationScript = @"
import sys
print(f"✅ Python version: {sys.version}")
print()

try:
    import tkinter
    print("✅ tkinter: OK")
except ImportError:
    print("❌ tkinter: FAILED - Included with Python on Windows")
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

try:
    import numpy
    print(f"✅ numpy: {numpy.__version__}")
except ImportError:
    print("❌ numpy: FAILED")
    sys.exit(1)

try:
    import scipy
    print(f"✅ scipy: {scipy.__version__}")
except ImportError:
    print("❌ scipy: FAILED")
    sys.exit(1)

print()
print("✅ All dependencies verified!")
"@

python -c $verificationScript
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "❌ Dependency verification failed" -ForegroundColor Red
    if (-not $SkipPauseOnError) { Read-Host "Press Enter to exit" }
    exit 1
}

Write-Host ""
Write-Host "Step 5: Creating convenient launchers..." -ForegroundColor Cyan

# Create run.bat
if (-not (Test-Path "run.bat")) {
    @"
@echo off
title Hugging Face Chat App
python main.py
pause
"@ | Out-File -FilePath "run.bat" -Encoding ASCII
    Write-Host "✅ Created run.bat launcher" -ForegroundColor Green
} else {
    Write-Host "✅ run.bat already exists" -ForegroundColor Green
}

# Create run.ps1
if (-not (Test-Path "run.ps1")) {
    @"
# Hugging Face Chat App Launcher (PowerShell)
python main.py
Write-Host "Press Enter to exit..." -ForegroundColor Yellow
Read-Host
"@ | Out-File -FilePath "run.ps1" -Encoding UTF8
    Write-Host "✅ Created run.ps1 launcher" -ForegroundColor Green
} else {
    Write-Host "✅ run.ps1 already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✅ Installation Complete! ✅              ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. (Optional) Configure your Hugging Face token:" -ForegroundColor Yellow
Write-Host "   notepad .env" -ForegroundColor White
Write-Host ""
Write-Host "2. Run the application - Choose ONE option:" -ForegroundColor Yellow
Write-Host "   Option A: Double-click 'run.bat'" -ForegroundColor White
Write-Host "   Option B: .\run.ps1 (from PowerShell)" -ForegroundColor White
Write-Host "   Option C: python main.py (from Command Prompt or PowerShell)" -ForegroundColor White
Write-Host ""
Write-Host "3. On first run:" -ForegroundColor Yellow
Write-Host "   - Read and accept the disclaimer" -ForegroundColor White
Write-Host "   - Select models to download (click 'Manage Models')" -ForegroundColor White
Write-Host "   - Models will download on first use (5-30 min depending on model)" -ForegroundColor White
Write-Host ""
Write-Host "💡 Performance Tips:" -ForegroundColor Cyan
Write-Host "   - Use Phi-2 for fastest performance on slower machines" -ForegroundColor White
Write-Host "   - Use 8GB+ RAM for best results (16GB+ recommended)" -ForegroundColor White
Write-Host "   - Keep other applications closed while running" -ForegroundColor White
Write-Host "   - First model download takes 5-30 minutes (cached after)" -ForegroundColor White
Write-Host ""
Write-Host "💾 System Requirements:" -ForegroundColor Cyan
Write-Host "   - Windows 7, 8, 10, or 11" -ForegroundColor White
Write-Host "   - Python 3.8 or higher" -ForegroundColor White
Write-Host "   - 8GB+ RAM (16GB+ recommended)" -ForegroundColor White
Write-Host "   - 50GB+ free disk space (for AI models)" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Remember: Developer accepts NO liability for misuse!" -ForegroundColor Yellow
Write-Host ""
