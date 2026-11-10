"""Download the GGUF models selected in models_config.json.

Every model with ``auto_install: true`` is downloaded into ``models/`` during
installation. Set ``filename`` in the config to choose a particular GGUF file;
otherwise the first GGUF file listed by Hugging Face is used.
"""

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "models_config.json"
ENV_PATH = REPO_ROOT / ".env"
MODELS_DIR = REPO_ROOT / "models"


def load_token():
    """Read an optional token from the environment or the project's .env file."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if token or not ENV_PATH.exists():
        return token

    for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith(("HF_TOKEN=", "HUGGINGFACE_HUB_TOKEN=")):
            _, value = line.split("=", 1)
            token = value.strip().strip("\"'")
            if token:
                return token
    return None


def update_env(entries):
    """Update model path entries without appending duplicate keys on reruns."""
    if not entries:
        return

    lines = ENV_PATH.read_text(encoding="utf-8").splitlines() if ENV_PATH.exists() else []
    for key, value in entries.items():
        replacement = f"{key}={value}"
        for index, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[index] = replacement
                break
        else:
            lines.append(replacement)
    ENV_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    if not CONFIG_PATH.exists():
        print(f"Model configuration not found: {CONFIG_PATH}", file=sys.stderr)
        return 1

    try:
        from huggingface_hub import HfApi, hf_hub_download
    except ImportError:
        print("huggingface_hub is required. Install requirements.txt first.", file=sys.stderr)
        return 1

    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Could not read {CONFIG_PATH}: {exc}", file=sys.stderr)
        return 1

    selected = [model for model in config.get("models", []) if model.get("auto_install")]
    if not selected:
        print("No models are selected for installation (auto_install=true).")
        return 0

    api = HfApi(token=load_token())
    env_entries = {}
    failures = []

    for model in selected:
        key = model.get("key", "unknown")
        repo_id = model.get("repo_id")
        if not repo_id:
            failures.append(f"{key}: missing repo_id in models_config.json")
            continue

        destination = MODELS_DIR / repo_id.replace("/", "_")
        destination.mkdir(parents=True, exist_ok=True)
        requested_filename = model.get("filename")
        print(f"\nDownloading selected model {model.get('name', key)} ({repo_id})", flush=True)

        try:
            if requested_filename:
                filename = requested_filename
            else:
                repo_files = api.list_repo_files(repo_id=repo_id, repo_type="model")
                gguf_files = sorted(name for name in repo_files if name.lower().endswith(".gguf"))
                if not gguf_files:
                    raise RuntimeError("The repository has no .gguf model files")
                filename = gguf_files[0]
                if len(gguf_files) > 1:
                    print(f"Found {len(gguf_files)} GGUF files; downloading {filename}. Set filename in models_config.json to choose another.")

            print(f"Downloading {filename} into {destination} ...", flush=True)
            downloaded = hf_hub_download(
                repo_id=repo_id,
                filename=filename,
                repo_type="model",
                local_dir=str(destination),
                token=load_token(),
            )
            model["local_path"] = os.path.relpath(downloaded, REPO_ROOT)
            env_entries[f"MODEL_PATH_{key}"] = model["local_path"]
            print(f"Downloaded {model['local_path']}", flush=True)
        except Exception as exc:
            failures.append(f"{key} ({repo_id}): {exc}")
            print(f"Download failed for {repo_id}: {exc}", file=sys.stderr, flush=True)

    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    update_env(env_entries)

    if failures:
        print("\nSome selected models could not be downloaded:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        print("Check your internet connection, available disk space, model access, and HF_TOKEN for gated models.", file=sys.stderr)
        return 1

    print("\nAll selected models are downloaded and ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
