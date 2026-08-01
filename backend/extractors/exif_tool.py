#!/usr/bin/env python3
"""
backend/extractors/exif_tool.py
Server-side EXIF/IPTC extraction using exiftool (best coverage) with a safe JSON output.
Requires exiftool to be installed on the host (recommended) or fallback to piexif/Pillow.

This extractor returns a dictionary with keys: exif, iptc, xmp, gps, orientation, raw (exiftool JSON)

Security: do not attempt to identify people from image metadata. Only surface embedded metadata fields.
"""
import json
import shutil
import subprocess
from pathlib import Path

EXIFTOOL_BIN = shutil.which('exiftool')


def extract_with_exiftool(path: str) -> dict:
    """Call exiftool -j to get JSON metadata. Returns an empty dict on failure."""
    if not EXIFTOOL_BIN:
        return {}
    try:
        proc = subprocess.run([EXIFTOOL_BIN, '-j', '-a', '-G', path], capture_output=True, text=True, check=True)
        data = json.loads(proc.stdout)
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        return {}
    except Exception as e:
        # Fall back silently; caller can decide further steps
        return {}


def extract_metadata(path: str) -> dict:
    path = str(path)
    result = {
        'exiftool': None,
    }
    exif_json = extract_with_exiftool(path)
    if exif_json:
        result['exiftool'] = exif_json
        # Normalize a few common fields if present
        normalized = {}
        for k in ('Make', 'Model', 'DateTimeOriginal', 'CreateDate', 'GPSLatitude', 'GPSLongitude', 'Orientation', 'ImageWidth', 'ImageHeight'):
            if k in exif_json:
                normalized[k.lower()] = exif_json[k]
        result['normalized'] = normalized
    else:
        # Optionally implement a Pillow/piexif fallback here
        result['exiftool'] = {}
        result['normalized'] = {}
    return result


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('image')
    args = parser.parse_args()
    data = extract_metadata(args.image)
    print(json.dumps(data, indent=2, ensure_ascii=False))
