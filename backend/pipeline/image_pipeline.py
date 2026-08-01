"""
backend/pipeline/image_pipeline.py
High-level image evidence pipeline (selection of image-capable models, run visual taggers, run face detector, aggregate results).
This file contains safe, pluggable entry points that call local model wrappers. The heavy ML implementations are expected to be behind safe adapters.

Important: This pipeline explicitly does NOT include any identity-resolution code (no face recognition against a database). It only returns bounding boxes and non-identifying attributes.
"""
import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, Any

from backend.models.manifest_loader import load_manifest
from backend.audit.logger import audit_log
from backend.extractors.exif_tool import extract_metadata

LOG = logging.getLogger(__name__)


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def select_model_for_task(manifest: dict, modalities_required=('image',)) -> Dict[str, Any]:
    """Select a model that supports the desired modalities. Returns manifest entry or raises RuntimeError."""
    candidates = []
    for m in manifest.get('models', []):
        if all(mod in m.get('modalities', []) for mod in modalities_required):
            candidates.append(m)
    if not candidates:
        raise RuntimeError('No image-capable models available in manifest')
    # Prefer non-preship, stable models first or pick by explicit priority if present
    return candidates[0]


# Placeholder wrappers for image models. Implementations must be provided by the runtime.

def run_clip_image_tags(model_entry: dict, image_path: str) -> dict:
    """Return visual tags and confidence scores using CLIP/embedding-based classifiers.
    This is a placeholder. The actual runtime should call the proper model-serving code.
    """
    # Example return format
    return {
        'visual_tags': [
            {'tag': 'outdoor', 'confidence': 0.92},
            {'tag': 'car', 'confidence': 0.78}
        ],
        'model_id': model_entry.get('id')
    }


def run_blip_caption(model_entry: dict, image_path: str) -> dict:
    return {
        'caption': 'A street with parked cars and a storefront.',
        'confidence': 0.88,
        'model_id': model_entry.get('id')
    }


def run_face_detector(image_path: str) -> dict:
    """Run a face detector and return bounding boxes + non-identifying attributes.
    The detector MUST NOT return identity labels. Only return attributes like age_range, pose, expression.
    """
    # Example placeholder
    return {
        'faces': [
            {'bbox': [100, 80, 200, 220], 'confidence': 0.99, 'age_range': '25-35', 'expression': 'neutral'}
        ]
    }


def aggregate_evidence(image_path: str, operator: str, manifest_path: Path) -> dict:
    manifest = load_manifest(manifest_path)
    image_path = str(image_path)
    image_hash = sha256_of_file(Path(image_path))

    # Extract EXIF/IPTC with exiftool wrapper
    metadata = extract_metadata(image_path)

    # Select image-capable model
    try:
        model_entry = select_model_for_task(manifest, modalities_required=('image',))
    except RuntimeError:
        model_entry = None

    visual = {}
    if model_entry:
        visual.update(run_clip_image_tags(model_entry, image_path))
        visual.update(run_blip_caption(model_entry, image_path))

    faces = run_face_detector(image_path)

    evidence = {
        'image_hash': image_hash,
        'operator': operator,
        'metadata': metadata,
        'visual': visual,
        'faces': faces,
        'model_used': model_entry.get('id') if model_entry else None
    }

    # Audit log the operation
    audit_log('image_analysis', operator=operator, details={'image_hash': image_hash, 'model': evidence['model_used']})

    return evidence


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('image')
    p.add_argument('--operator', default='unknown')
    p.add_argument('--manifest', default='backend/models/manifest.json')
    args = p.parse_args()
    ev = aggregate_evidence(args.image, args.operator, Path(args.manifest))
    print(json.dumps(ev, indent=2))
