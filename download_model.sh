#!/usr/bin/env bash
set -euo pipefail

# download_model.sh
# Usage: ./download_model.sh <repo-id> [filename] [dest-dir]
# Example:
# ./download_model.sh DavidAU/Llama-3.2-8X3B-MOE-Dark-Champion-Instruct-uncensored-abliterated-18.4B-GGUF

REPO_ID="${1:-}"
FILENAME="${2:-}"
DEST_DIR="${3:-}"

if [ -z "$REPO_ID" ]; then
  echo "Usage: $0 <repo-id> [filename] [dest-dir]"
  exit 2
fi

if [ -z "$DEST_DIR" ]; then
  DEST_DIR="./models/$(echo "$REPO_ID" | tr '/' '_')"
fi

mkdir -p "$DEST_DIR"

if [ -z "${HUGGINGFACE_HUB_TOKEN:-}" ]; then
  echo "Warning: HUGGINGFACE_HUB_TOKEN not set. If the model is gated, run 'huggingface-cli login' or export HUGGINGFACE_HUB_TOKEN."
fi

python - <<PY
import os, sys
from huggingface_hub import list_repo_files, hf_hub_download

repo_id = os.environ.get('REPO_ID') or "$REPO_ID"
token = os.environ.get('HUGGINGFACE_HUB_TOKEN')
dest = os.path.abspath(os.environ.get('DEST_DIR') or "$DEST_DIR")
filename = os.environ.get('FILENAME') or ("$FILENAME" or None)

print('Inspecting repo:', repo_id)
files = list_repo_files(repo_id, token=token)
# prefer files that look like GGUF
ggufs = [f for f in files if f.lower().endswith('.gguf') or '.gguf' in f.lower()]
if not ggufs and not filename:
    print('No .gguf files found in the repo. Files:', files, file=sys.stderr)
    sys.exit(2)

if filename:
    if filename not in files:
        print(f"Requested filename '{filename}' not found in repo files.", file=sys.stderr)
        sys.exit(3)
else:
    filename = ggufs[0]
    print('Auto-selected gguf file:', filename)

print('Downloading', filename, 'to', dest)
out = hf_hub_download(repo_id=repo_id, filename=filename, cache_dir=dest, token=token)
print('Downloaded to:', out)
PY

echo "Download complete."
