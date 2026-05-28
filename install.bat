@echo off
REM Hugging Face Chat App Installation Script for Windows
REM This script sets up the environment and installs all dependencies

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Hugging Face Chat App - Windows Setup               ║
echo ║   Python AI Models - Local Inference on CPU            ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python is not installed or not in PATH
    echo.
    echo 📥 Please install Python from: https://www.python.org/downloads/
    echo.
    echo ⚠️  IMPORTANT: During installation, check "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python version: %PYTHON_VERSION%
echo.

REM Check Python version (3.8+)
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python 3.8+ is required
    echo.
    echo Your Python version is %PYTHON_VERSION%
    echo Please upgrade from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo.
echo Step 1: Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo ❌ Failed to upgrade pip
    pause
    exit /b 1
)
echo ✅ pip, setuptools, and wheel upgraded

echo.
echo Step 2: Installing Python dependencies...
echo This may take several minutes on first run...
echo.
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ Failed to install dependencies
    echo.
    echo Troubleshooting tips:
    echo - Check your internet connection
    echo - Try running as Administrator
    echo - Clear pip cache: pip cache purge
    echo.
    pause
    exit /b 1
)
echo ✅ Python dependencies installed

echo.
echo Step 3: Creating configuration files...

if not exist ".env.example" (
    (
        echo # Hugging Face API Token (optional - only for gated models^)
        echo # Get your token from: https://huggingface.co/settings/tokens
        echo HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
        echo.
        echo # Legacy API key (optional^)
        echo HUGGINGFACE_API_KEY=your_api_key_here
    ) > .env.example
    echo ✅ Created .env.example
) else (
    echo ✅ .env.example already exists
)

if not exist ".env" (
    copy .env.example .env >nul
    echo ✅ Created .env (copy of .env.example^)
    echo.
    echo ⚠️  IMPORTANT: Edit .env and add your Hugging Face token (optional^)
    echo    You can use Notepad: notepad .env
) else (
    echo ✅ .env already exists
)

echo.
echo Step 4: Verifying installation...
echo.

python << 'PYEOF'
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
PYEOF

if errorlevel 1 (
    echo.
    echo ❌ Dependency verification failed
    pause
    exit /b 1
)

echo.
echo Step 5: Creating convenient launcher...

if not exist "run.bat" (
    (
        echo @echo off
        echo title Hugging Face Chat App
        echo python main.py
        echo pause
    ) > run.bat
    echo ✅ Created run.bat launcher
) else (
    echo ✅ run.bat already exists
)

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║              ✅ Installation Complete! ✅              ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 📋 Next steps:
echo.
echo 1. (Optional) Configure your Hugging Face token:
echo    notepad .env
echo.
echo 2. Run the application - Choose ONE option:
echo    Option A: Double-click "run.bat"
echo    Option B: python main.py
echo    Option C: python -m main
echo.
echo 3. On first run:
echo    - Read and accept the disclaimer
echo    - Select models to download (click "Manage Models")
echo    - Models will download on first use (5-30 min depending on model)
echo.
echo 💡 Performance Tips:
echo    - Use Phi-2 for fastest performance on slower machines
echo    - Use 8GB+ RAM for best results (16GB+ recommended)
echo    - Keep other applications closed while running
echo    - First model download takes 5-30 minutes (cached after)
echo.
echo 💾 System Requirements:
echo    - Windows 7, 8, 10, or 11
echo    - Python 3.8 or higher
echo    - 8GB+ RAM (16GB+ recommended)
echo    - 50GB+ free disk space (for AI models)
echo.
echo ⚠️  Remember: Developer accepts NO liability for misuse!
echo.
pause
