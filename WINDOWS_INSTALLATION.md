````markdown
# 🤖 Hugging Face Chat App - Windows Support

**An interactive GUI for running 6B parameter AI models locally on Windows with no GPU needed**

![Version](https://img.shields.io/badge/version-2.0+-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Windows](https://img.shields.io/badge/Windows-7%2F8%2F10%2F11-blue)

## ⚠️ Disclaimer

**The developer accepts NO responsibility for misuse and wrongful actions by this tool.**
Users are solely responsible for ensuring their use complies with all applicable laws and terms of service.

---

## 🎯 Features

✅ **6 Pre-Configured 6B Parameter Models** (CPU-optimized)
✅ **Choose Your Own Models** - Install only what you need
✅ **Local Inference** - No external API calls, full privacy
✅ **Interactive GUI** - Dark theme with neon styling
✅ **Chat History** - Auto-saves all conversations
✅ **Model Management** - Easy model selection and configuration
✅ **Windows Optimized** - Works on Windows 7, 8, 10, 11
✅ **Threading** - Responsive UI during model inference
✅ **Multiple Launchers** - `.bat`, `.ps1`, or command line

---

## 🤖 Available 6B Parameter Models

| Model | Size | RAM | Speed | Best For |
|-------|------|-----|-------|----------|
| **Phi-2** (Microsoft) | 5GB | 5GB | ⚡⚡⚡ Fastest | General purpose, fast responses |
| **OpenElm-6B** (Apple) | 12GB | 6GB | ⚡⚡ Fast | Efficient, balanced |
| **Falcon-7B** (UAE) | 13GB | 7GB | ⚡⚡ Fast | High quality output |
| **Mistral-7B-Instruct** | 13GB | 7GB | ⚡⚡ Fast | Instruction following |
| **Llama-2-7B** (Meta) | 13GB | 7GB | ⚡ Medium | Solid general purpose |
| **MPT-7B** (MosaicML) | 13GB | 7GB | ⚡ Medium | Long context |

---

## 🚀 Quick Start (Windows)

### Prerequisites
- **Python 3.8+** (download from https://www.python.org/downloads/)
- **8GB+ RAM** (16GB+ recommended)
- **50GB+ free disk space** (for AI models)
- **Windows 7, 8, 10, or 11**

### Installation - Method 1: Batch File (Easiest)

1. **Download the repository**
   ```cmd
   git clone https://github.com/kempdogg/huggingface-chat-app.git
   cd huggingface-chat-app
   ```

2. **Run the installer**
   - Double-click `install.bat`
   - Or from Command Prompt: `install.bat`

### Installation - Method 2: PowerShell

1. **Download the repository**
   ```powershell
   git clone https://github.com/kempdogg/huggingface-chat-app.git
   cd huggingface-chat-app
   ```

2. **Allow script execution** (one time only)
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Run the installer**
   ```powershell
   .\install.ps1
   ```

### Installation - Method 3: Manual

1. **Ensure Python 3.8+ is installed and in PATH**
   ```cmd
   python --version
   ```

2. **Download the repository**
   ```cmd
   git clone https://github.com/kempdogg/huggingface-chat-app.git
   cd huggingface-chat-app
   ```

3. **Install dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **(Optional) Configure Hugging Face token**
   - Copy `.env.example` to `.env`
   - Edit `.env` with your token from https://huggingface.co/settings/tokens

### Configuration

Edit the `.env` file (optional, only for gated models):
```
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
HUGGINGFACE_API_KEY=your_api_key_here
```

---

## 🎮 Running the App

### Option 1: Batch File (Easiest for Windows Users)
- Double-click `run.bat` in the repository folder
- The app will launch with a command window

### Option 2: PowerShell
```powershell
.\run.ps1
```

### Option 3: Command Prompt
```cmd
python main.py
```

### First Run
1. **Accept the disclaimer** - Read and confirm terms
2. **Select a model** - Click "Manage Models" to choose which models to download
3. **Wait for download** - First model download takes 5-30 minutes (depends on model size)
4. **Type your message** - Ask questions or give instructions
5. **Send** - Click "SEND CHAT" button
6. **View responses** - Scroll through chat history

---

## ⚡ Performance Tips

### For Slow Machines (8GB RAM)
- Use **Phi-2** (fastest, smallest - 5GB)
- Keep other apps closed
- Use shorter prompts
- Expect 15-30 seconds per response

### For Better Performance (16GB+ RAM)
- Try **Falcon-7B** or **Mistral-7B**
- Run multiple generations
- Use longer, detailed prompts
- Expect 10-20 seconds per response

### Optimization
```cmd
REM Set number of threads (adjust based on CPU cores)
set OMP_NUM_THREADS=4

REM For NUMA systems
set OPENBLAS_NUM_THREADS=4

python main.py
```

---

## 📁 Project Structure

```
huggingface-chat-app/
├── main.py                 # Main application
├── requirements.txt        # Python dependencies
├── install.bat            # Windows batch installer
├── install.ps1            # Windows PowerShell installer
├── run.bat                # Windows batch launcher
├── run.ps1                # Windows PowerShell launcher
├── chat_history.json      # Auto-saved conversations
├── models_config.json     # Model configuration
├── .env                   # Environment variables
└── README.md             # Original documentation
```

---

## 🔧 Troubleshooting

### "Python is not installed or not in PATH"
1. Download Python from https://www.python.org/downloads/
2. **Important:** During installation, check **"Add Python to PATH"**
3. Restart Command Prompt/PowerShell
4. Verify: `python --version`

### "Module not found" errors
```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### "tkinter not found" (Rare on Windows)
Python includes tkinter by default on Windows. If missing:
1. Go to Settings → Apps → Apps & features
2. Find "Python" → Modify
3. Check "tcl/tk and IDLE"
4. Complete the repair

### "Models won't download"
- Check internet connection
- Verify 50GB+ free disk space: `dir C:\`
- Check firewall/antivirus settings
- Try running Command Prompt as Administrator

### "Out of memory" errors
- Use smaller models (Phi-2)
- Close other applications (especially Chrome, Visual Studio, etc.)
- Increase virtual memory:
  - Right-click "This PC" → Properties
  - Advanced system settings → Performance → Settings
  - Advanced tab → Virtual memory → Change
  - Set custom size: Initial/Maximum = 8000-16000 MB

### "Slow responses"
- This is normal on CPU - first run downloads model (5-30 min)
- Subsequent runs use cached model (10-30 sec per response)
- Shorter prompts = faster responses
- Use Phi-2 for fastest performance

### Windows Defender Warning
Windows Defender may flag the installer. This is normal for Python scripts.
- Click "More info" → "Run anyway" to proceed
- Or disable scanning temporarily

---

## 🔐 Privacy & Security

✅ **All inference runs locally** - no data sent to external servers
✅ **Chat history saved locally** - only on your machine in `chat_history.json`
✅ **No telemetry** - app doesn't track usage
✅ **Optional API key** - only for gated models on Hugging Face

---

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| OS | Windows 7+ | Windows 10/11 |
| CPU | Quad-core | 8+ cores |
| RAM | 8GB | 16GB+ |
| Storage | 50GB | 100GB+ |
| Python | 3.8 | 3.10+ |
| GPU | Not required | Not used |

---

## 🎨 UI Features

- **Dark Terminal Theme** - Neon green text on black
- **Skull & Crossbones** - ☠️ Safety warnings
- **Model Info Display** - See specs before loading
- **Real-time Status** - Know what's happening
- **Scrollable Chat** - Full history with timestamps
- **Model Management** - Easy selection and configuration

---

## 📝 Chat History

Your conversations are automatically saved to `chat_history.json`:
- Timestamps for each message
- Model used for each response
- Easy to backup or transfer
- JSON format for easy parsing

---

## 🛠️ For Developers

### Custom Model Addition

Edit `AVAILABLE_MODELS` in `main.py`:
```python
AVAILABLE_MODELS = {
    "Your-Model": {
        "model_id": "huggingface/model-id",
        "description": "Description here",
        "size": "~5GB",
        "ram": "~5GB"
    },
    # ... more models
}
```

### Contributing

Feel free to fork and submit pull requests!

---

## ⚠️ Legal Notice

This tool uses AI models that may generate unpredictable or harmful content. Users are responsible for:
- Reviewing all AI-generated content
- Complying with local laws and regulations
- Respecting intellectual property rights
- Using responsibly and ethically

**The developer assumes NO liability for misuse.**

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- Hugging Face for the Transformers library
- Model creators: Microsoft, Apple, Meta, UAE, MosaicML
- Windows community for testing and feedback

---

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section above

---

**Made with ☠️ for penetration testers and ethical hackers**

```
    ☠️  ⚠️  USE AT YOUR OWN RISK  ⚠️  ☠️
```
````
