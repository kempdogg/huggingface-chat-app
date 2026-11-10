# 🤖 Hugging Face Chat App

A graphical chat app for working with AI models, plus a simple GUI for selecting and downloading GGUF models from Hugging Face.

## Quick start (Kali Linux / Debian)

```bash
git clone https://github.com/kempdogg/huggingface-chat-app.git
cd huggingface-chat-app
chmod +x install.sh
./install.sh
```

The installer installs the Python dependencies, downloads every model marked `auto_install: true` in `models_config.json`, and installs two commands:

- `huggingface-chat-app` — launch the chat application.
- `huggingface-chat-models` — open the friendly GGUF model manager.

The model manager lets you browse GGUF models on Hugging Face, paste a model page URL or `owner/model` ID, choose which models should be downloaded, and start the download. Newly added models are selected for download by default. Downloaded model files may be several GB each, so allow enough time and disk space.

If a selected model is gated, add an authorized Hugging Face access token to the project `.env` file as `HF_TOKEN=...`. To pick a specific GGUF file from a repository with multiple files, enter the filename in the model manager before adding the repository. If left blank, setup downloads the first `.gguf` file listed by Hugging Face.

The installer uses pip's `--break-system-packages` option for Debian/Kali's externally managed system Python. The standalone `setup.sh` alternative installs Python dependencies into `.venv` and downloads the models selected in `models_config.json`.

## Notes

- Install Tkinter on Debian/Kali with `sudo apt-get install python3-tk` if it is missing.
- Downloads require an internet connection and enough free storage.
- Review model licenses and use models in accordance with their terms.
