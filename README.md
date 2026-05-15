# 🤖 Hugging Face Chat App

**An interactive GUI for running 6B parameter AI models locally on Kali Linux with no GPU needed**

![Version](https://img.shields.io/badge/version-2.0-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

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
✅ **Kali Linux Optimized** - Works with `python3-tk` from apt
✅ **Threading** - Responsive UI during model inference

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

## 🚀 Quick Start (Kali Linux)

### Prerequisites
- Python 3.8+
- 8GB+ RAM (16GB+ recommended)
- 50GB+ free disk space (for models)

### Installation

**Option 1: Automated (Recommended)**
```bash
git clone https://github.com/kempdogg/huggingface-chat-app.git
cd huggingface-chat-app
chmod +x install.sh
./install.sh
```

**Option 2: Manual**
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-tk python3-pip

# Install Python packages
pip3 install -r requirements.txt

# Optional: Get Hugging Face token for gated models
# Visit https://huggingface.co/settings/tokens
```

### Configuration

Create a `.env` file:
```bash
nano .env
```

Add your Hugging Face token (optional, only for gated models):
```
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
HUGGINGFACE_API_KEY=your_api_key_here
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

### Running the App

```bash
python3 main.py
```

---

## 🎮 Usage

1. **Launch the app** - `python3 main.py`
2. **Accept the disclaimer** - Read and confirm terms
3. **Select a model** - Choose from dropdown menu
4. **Type your message** - Ask questions or give instructions
5. **Send** - Click "SEND CHAT" button
6. **View responses** - Scroll through chat history

### Managing Models

Click **"⚙️ Manage Models"** to:
- Select which models to pre-install
- View model specifications
- Save configuration

Models download automatically on first use.

---

## ⚡ Performance Tips

### For Slow Machines (8GB RAM)
- Use **Phi-2** (fastest, smallest)
- Keep other apps closed
- Use shorter prompts
- Expect 15-30 seconds per response

### For Better Performance (16GB+ RAM)
- Try **Falcon-7B** or **Mistral-7B**
- Run multiple generations
- Use longer, detailed prompts
- Expect 10-20 seconds per response

### Optimization
```bash
# Set number of threads (adjust based on CPU cores)
export OMP_NUM_THREADS=4

# For NUMA systems
export OPENBLAS_NUM_THREADS=4

python3 main.py
```

---

## 📁 Project Structure

```
huggingface-chat-app/
├── main.py                 # Main application
├── requirements.txt        # Python dependencies
├── install.sh             # Installation script
├── chat_history.json      # Auto-saved conversations
├── models_config.json     # Model configuration
├── .env                   # Environment variables
└── README.md             # This file
```

---

## 🔧 Troubleshooting

### "tkinter not found"
```bash
sudo apt-get install python3-tk
```

### "Models won't download"
- Check internet connection
- Verify you have 50GB+ free space
- Check firewall settings

### "Out of memory"
- Use smaller models (Phi-2)
- Close other applications
- Increase swap space:
  ```bash
  sudo fallocate -l 4G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  ```

### "Slow responses"
- This is normal on CPU - first run downloads model (5-30 min)
- Subsequent runs use cached model (10-30 sec per response)
- Shorter prompts = faster responses

---

## 🔐 Privacy & Security

✅ **All inference runs locally** - no data sent to external servers
✅ **Chat history saved locally** - only on your machine
✅ **No telemetry** - app doesn't track usage
✅ **Optional API key** - only for gated models on Hugging Face

---

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | Quad-core | 8+ cores |
| RAM | 8GB | 16GB+ |
| Storage | 50GB | 100GB+ |
| Python | 3.8 | 3.10+ |

---

## 🎨 UI Features

- **Dark Terminal Theme** - Neon green text on black
- **Skull & Crossbones** - ☠️ Safety warnings
- **Model Info Display** - See specs before loading
- **Real-time Status** - Know what's happening
- **Scrollable Chat** - Full history with timestamps

---

## 📝 Chat History

Your conversations are automatically saved to `chat_history.json`:
- Timestamps for each message
- Model used for each response
- Easy to backup or transfer

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
- Kali Linux community

---

**Made with ☠️ for penetration testers and ethical hackers**

```
    ☠️  ⚠️  USE AT YOUR OWN RISK  ⚠️  ☠️
```
