# helper to load GGUF models via llama-cpp-python
# Usage:
#   from scripts.load_gguf import load_model
#   llm = load_model(key="llama_dark_champion")

import json
import os
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "models_config.json"


def _get_model_path(key: Optional[str], model_path: Optional[str]) -> str:
    # priority: explicit model_path arg > MODEL_PATH_<key> env var > models_config.json local_path
    if model_path:
        return model_path

    if key:
        env_key = f"MODEL_PATH_{key}"
        if env_key in os.environ:
            return os.environ[env_key]

    # fall back to reading models_config.json
    if CONFIG_PATH.exists():
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        for m in cfg.get("models", []):
            if key and m.get("key") == key:
                lp = m.get("local_path")
                if lp:
                    return lp
            # if no key provided, return first installed model
        if not key:
            for m in cfg.get("models", []):
                if m.get("local_path"):
                    return m.get("local_path")

    raise FileNotFoundError("Model path not found. Pass model_path or set MODEL_PATH_<key> in .env or run setup.sh to download models.")


def load_model(key: Optional[str] = None, model_path: Optional[str] = None, **llama_kwargs):
    """Load a GGUF model using llama-cpp-python.

    Parameters:
      key: optional model key as defined in models_config.json (e.g. 'llama_dark_champion')
      model_path: explicit path to the GGUF file (overrides key)
      llama_kwargs: passed to Llama(...)

    Returns:
      An instance of llama_cpp.Llama

    Raises:
      RuntimeError if llama-cpp-python is not installed.
    """
    path = _get_model_path(key, model_path)

    # normalize path relative to repo root
    p = Path(path)
    if not p.is_absolute():
        p = (REPO_ROOT / p).resolve()

    if not p.exists():
        raise FileNotFoundError(f"Model file not found: {p}")

    try:
        from llama_cpp import Llama
    except Exception as e:
        raise RuntimeError("Please install llama-cpp-python (pip install llama-cpp-python)") from e

    # default deterministic settings can be set here (but can be overridden at create time)
    return Llama(model=str(p), **llama_kwargs)
