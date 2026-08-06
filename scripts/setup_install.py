"""scripts/setup_install.py
Performs the heavy lifting for setup.sh: reads models_config.json, downloads auto_install models,
updates models_config.json with local_path, and appends MODEL_PATH_<key> entries to .env.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "models_config.json"
ENV_PATH = REPO_ROOT / ".env"
DOWNLOAD_SCRIPT = REPO_ROOT / "download_model.sh"


def run(cmd, **kw):
    print("RUN:", " ".join(cmd))
    subprocess.check_call(cmd, **kw)


def main():
    if not CONFIG_PATH.exists():
        print("models_config.json not found; exiting.")
        sys.exit(1)

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    any_changes = False
    env_lines = []

    for m in cfg.get("models", []):
        key = m.get("key")
        repo_id = m.get("repo_id")
        filename = m.get("filename")
        auto = m.get("auto_install", False)

        if not auto:
            print(f"Skipping {key} (auto_install=false)")
            continue

        print(f"Processing model {key}: {repo_id}")

        dest_dir = REPO_ROOT / "models" / repo_id.replace("/", "_")
        dest_dir.mkdir(parents=True, exist_ok=True)

        cmd = [str(DOWNLOAD_SCRIPT), repo_id]
        if filename:
            cmd.append(filename)
        cmd.append(str(dest_dir))

        try:
            run(["chmod", "+x", str(DOWNLOAD_SCRIPT)])
            run(cmd)
        except subprocess.CalledProcessError:
            print(f"Failed to download {repo_id}; continue to next model")
            continue

        # find the first .gguf file in dest_dir
        ggufs = list(dest_dir.glob("**/*.*gguf")) + list(dest_dir.glob("**/*.gguf"))
        if not ggufs:
            # try any file >100MB as fallback
            candidates = [p for p in dest_dir.iterdir() if p.is_file() and p.stat().st_size > 100 * 1024 * 1024]
            if candidates:
                chosen = candidates[0]
            else:
                print(f"No model file found in {dest_dir}")
                continue
        else:
            chosen = ggufs[0]

        rel = os.path.relpath(chosen, REPO_ROOT)
        print(f"Detected model file: {rel}")

        if m.get("local_path") != rel:
            m["local_path"] = rel
            any_changes = True

        env_key = f"MODEL_PATH_{key}"
        env_lines.append(f"{env_key}={rel}\n")

    if any_changes:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
        print(f"Updated {CONFIG_PATH}")

    # append to .env
    if env_lines:
        with open(ENV_PATH, "a", encoding="utf-8") as f:
            f.write('\n# Added by setup_install.py\n')
            for l in env_lines:
                f.write(l)
        print(f"Appended MODEL_PATH entries to {ENV_PATH}")


if __name__ == '__main__':
    main()
