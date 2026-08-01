# tests/test_exif.py
# Basic unit tests for EXIF extractor using mocking to avoid binary assets.
import pytest
from unittest.mock import patch
from backend.extractors import exif_tool


def test_extract_metadata_no_exif(monkeypatch):
    monkeypatch.setattr(exif_tool, 'EXIFTOOL_BIN', None)
    res = exif_tool.extract_metadata('nonexistent.jpg')
    assert 'normalized' in res
    assert isinstance(res['normalized'], dict)

