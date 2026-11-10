# 🤖 Hugging Face Chat App

**An interactive GUI for running AI models locally.**

## Quick start (Kali Linux / Debian)

```bash
git clone https://github.com/kempdogg/huggingface-chat-app.git
cd huggingface-chat-app
chmod +x install.sh
./install.sh
```

The installer installs the Python dependencies, downloads every model marked `auto_install: true` in `models_config.json`, and installs a `huggingface-chat-app` command. Start the application with:

```bash
huggingface-chat-app
```

Model files can be several gigabytes each, so allow time and disk space for the initial download. If a selected model is gated, put an authorized Hugging Face access token in `.env` as `HF_TOKEN=...` and rerun `./install.sh`. To choose a particular GGUF file from a repository containing several, set its `filename` in `models_config.json`; when it is `null`, setup downloads the first GGUF filename listed by Hugging Face.

The installer uses pip's `--break-system-packages` option for Debian/Kali's externally-managed system Python. The standalone `setup.sh` alternative installs Python dependencies into `.venv` and downloads the same selected models.

## Configuration

The model download list is `models_config.json`. Models with `auto_install: true` are downloaded during setup into `models/`; set it to `false` to skip a model. An optional Hugging Face token is read from `.env` for gated repositories.

## Notes

- Install Tkinter on Debian/Kali with `sudo apt-get install python3-tk` if it is missing.
- Model downloads require an internet connection and enough free storage.
- Review model licenses and use the models in accordance with their terms.
