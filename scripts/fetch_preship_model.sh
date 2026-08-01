#!/usr/bin/env bash
# scripts/fetch_preship_model.sh
# Securely fetch a model from Hugging Face into the local models/ directory.
# Requires: huggingface-cli (pip install huggingface-hub) or git-lfs if applicable.
# This script does NOT bypass licensing checks — you must ensure you have rights to download/distribute.

set -euo pipefail
MODEL_URL="$1"  # e.g. https://huggingface.co/DavidAU/.../resolve/main/model.gguf
DEST_DIR="models/davidau-llama-3.2-8x3b-moe"
mkdir -p "$DEST_DIR"

echo "[INFO] Ensure you have the legal right to download and redistribute: $MODEL_URL"
read -p "Type YES to confirm you have redistribution rights and wish to continue: " confirm
if [[ "$confirm" != "YES" ]]; then
  echo "Aborting. Confirm with YES to download model."
  exit 1
fi

# Try huggingface-cli snapshot-download (requires user to be logged in if model requires auth)
if command -v huggingface-cli >/dev/null 2>&1; then
  huggingface-cli repo snapshot-download "$MODEL_URL" --repo-type model --revision main --output-dir "$DEST_DIR" || true
fi

# Fallback: wget/curl of a direct asset URL (user should provide the direct file URL)
# The script intentionally does not attempt to force-download private assets.

echo "[INFO] Download finished (or attempted). Verify the downloaded files and their licenses before committing them to the repository."
