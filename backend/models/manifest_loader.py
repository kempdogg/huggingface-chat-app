"""
backend/models/manifest_loader.py
Simple manifest loader for the models/manifest.json file.
"""
import json
from pathlib import Path


def load_manifest(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)
