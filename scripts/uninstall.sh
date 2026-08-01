#!/usr/bin/env bash
# scripts/uninstall.sh
# Safely remove downloaded preshipped models and generated artifacts created by the setup scripts.
# Usage:
#   ./scripts/uninstall.sh --model davidau-llama-3.2-8x3b-moe   # remove specific model directory
#   ./scripts/uninstall.sh --all                               # remove all files under models/ and audit logs
#   ./scripts/uninstall.sh --dry-run                           # show what would be removed
#
# WARNING: This permanently deletes files from disk. Verify backups and hashes before running.

set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [--model <model_id>] [--all] [--dry-run] [--yes]

Options:
  --model <model_id>   Remove the model directory under models/<model_id> (e.g. davidau-llama-3.2-8x3b-moe)
  --all                Remove all downloaded model directories under models/ and the audit log
  --dry-run            Show what would be removed without deleting anything
  --yes                Skip the interactive confirmation (use with caution)
  --help               Show this message

Examples:
  $0 --model davidau-llama-3.2-8x3b-moe
  $0 --all --dry-run
EOF
}

if [[ ${#@} -eq 0 ]]; then
  usage
  exit 1
fi

DRY_RUN=0
SKIP_CONFIRM=0
MODEL_ID=""
REMOVE_ALL=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      MODEL_ID="$2"
      shift 2
      ;;
    --all)
      REMOVE_ALL=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --yes)
      SKIP_CONFIRM=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1"
      usage
      exit 1
      ;;
  esac
done

ROOT_DIR="$(pwd)"
MODELS_DIR="$ROOT_DIR/models"
AUDIT_LOG="$ROOT_DIR/backend/logs/audit.log"

if [[ $REMOVE_ALL -eq 0 && -z "$MODEL_ID" ]]; then
  echo "Error: must specify --model or --all"
  usage
  exit 1
fi

# Build list of targets to remove
TARGETS=()
if [[ $REMOVE_ALL -eq 1 ]]; then
  if [[ -d "$MODELS_DIR" ]]; then
    for d in "$MODELS_DIR"/*; do
      [[ -d "$d" ]] || continue
      TARGETS+=("$d")
    done
  fi
  # Add audit log if present
  if [[ -f "$AUDIT_LOG" ]]; then
    TARGETS+=("$AUDIT_LOG")
  fi
else
  # Specific model
  MODEL_DIR="$MODELS_DIR/$MODEL_ID"
  if [[ ! -d "$MODEL_DIR" ]]; then
    echo "Model directory does not exist: $MODEL_DIR"
    exit 1
  fi
  TARGETS+=("$MODEL_DIR")
fi

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "Nothing to remove. Targets list is empty."
  exit 0
fi

# Safety: ensure every target is under MODELS_DIR or backend/logs
for t in "${TARGETS[@]}"; do
  real=$(realpath "$t")
  if [[ $real != "$MODELS_DIR"* && $real != "$(realpath "$ROOT_DIR/backend/logs")"* ]]; then
    echo "Refusing to remove target outside of expected directories: $real"
    exit 1
  fi
done

echo "The following paths will be removed:"
for t in "${TARGETS[@]}"; do
  echo "  - $t"
done

if [[ $DRY_RUN -eq 1 ]]; then
  echo "Dry-run mode: no files will be deleted."
  exit 0
fi

if [[ $SKIP_CONFIRM -eq 0 ]]; then
  read -p "Type YES to permanently delete these files: " conf
  if [[ "$conf" != "YES" ]]; then
    echo "Aborted by user."
    exit 1
  fi
fi

# Perform deletions
for t in "${TARGETS[@]}"; do
  if [[ -d "$t" ]]; then
    echo "Removing directory: $t"
    rm -rf "$t"
  elif [[ -f "$t" ]]; then
    echo "Removing file: $t"
    rm -f "$t"
  else
    echo "Skipping missing target: $t"
  fi
done

echo "Uninstall complete. If you removed model weights, verify any dependent services or caches are refreshed."
