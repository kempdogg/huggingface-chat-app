# 🤖 Hugging Face Chat App

A Tkinter desktop chat app for Hugging Face Transformers models, with optional Hugging Face router support and GGUF download/loading utilities.

## Requirements

- Python 3.9 or newer
- Kali/Debian: `python3-tk`, `python3-venv` (for the virtual environment path), `python3-dev`, and `build-essential`
- Disk and memory appropriate for the model you choose; model downloads can be many gigabytes

## Install

Choose one installation path:

### Kali/Debian system install

`install.sh` installs Python dependencies into the system interpreter. On Kali it always supplies `--break-system-packages` to pip as requested. This overrides the OS package manager's protection, so the isolated environment below is the safer option for most users.

```bash
sudo apt-get update
sudo apt-get install -y python3-tk python3-pip python3-dev build-essential
chmod +x install.sh
./install.sh
```

Manual Kali pip installation must use the same option:

```bash
pip3 install --break-system-packages -r requirements.txt
```

`--break-system-packages` is a pip command-line option, not a package requirement, so it belongs in the install command/script rather than as a line in `requirements.txt`.

### Virtual environment and GGUF setup

This path keeps Python packages isolated. `setup.sh` creates `.venv`, installs the requirements and runs the configured GGUF model downloader. On Kali it also passes the requested pip option to its pip commands.

```bash
sudo apt-get update
sudo apt-get install -y python3-tk python3-venv python3-dev build-essential
chmod +x setup.sh
./setup.sh
source .venv/bin/activate
python main.py
```

`models_config.json` controls GGUF downloads. Large model files are stored under `models/` and are intentionally not committed. The GGUF helper is available in `scripts/load_gguf.py`; the current Tkinter chat generation path in `main.py` uses Transformers, so the helper and GUI are not yet a unified GGUF chat backend.

### Other operating systems

Create a virtual environment and use pip normally (do not use `--break-system-packages`):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install Tkinter through your operating system's package manager if it is missing.

## Configure and run

1. Copy `.env.example` to `.env` if it does not already exist.
2. Add `HF_TOKEN` only if you need gated model access or Hugging Face router access. Keep the token private; do not commit `.env`.
3. Launch the application with the same Python environment where the dependencies were installed:

```bash
python main.py
```

4. Accept the disclaimer, choose a configured model, enter a prompt, and select **SEND CHAT**. Use **Manage Models** to change the configured model list.

Custom Hugging Face model IDs can be entered in the custom model field. The model must be compatible with Transformers' text-generation pipeline. Gated models require an authorized token.

## GGUF models

The optional GGUF download workflow reads `models_config.json` and downloads entries marked `auto_install: true` when `./setup.sh` runs. `scripts/load_gguf.py` loads a downloaded file through `llama-cpp-python`; callers can pass `n_gpu_layers` and other supported `llama_cpp.Llama` options for their hardware. A compatible GPU-enabled `llama-cpp-python` build may require platform-specific installation rather than the default PyPI wheel.

## Troubleshooting

- **`tkinter` import error:** install the OS package, e.g. `sudo apt-get install python3-tk`.
- **Cannot create `.venv`:** install `python3-venv` and the matching version-specific venv package on Debian/Kali.
- **PEP 668 / externally-managed environment:** on Kali use `install.sh` or the explicit `pip3 install --break-system-packages -r requirements.txt` command; preferably use `setup.sh` to isolate dependencies.
- **GGUF package/build errors:** `llama-cpp-python` may need a compiler toolchain and platform-specific GPU build settings. Check the package's installation guidance for your CUDA/Metal/CPU setup.
- **Model download/auth errors:** check network access, repository ID/filename in `models_config.json`, and Hugging Face token permissions for gated repositories.
- **Out of memory or slow generation:** use a smaller or more heavily quantized model, reduce context/generation length, or use a compatible GPU-backed runtime.

## Privacy

Local Transformers and GGUF inference run on your machine. Hugging Face downloads and optional router requests require network access; router prompts and images are sent to the selected hosted provider. Review the model and provider terms before use.

## Disclaimer

Models can produce inaccurate or inappropriate output. Review generated content and comply with applicable laws and model/provider terms.
