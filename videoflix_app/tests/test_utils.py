from django.test import TestCase
from django.conf import settings
from pathlib import Path
import pytest
from django.http import Http404
from videoflix_app import utils

def test_safe_media_path_inside_media():
    path = utils.safe_media_path("hls/5/720p/index.m3u8")
    normalized = path.as_posix()
    assert normalized.endswith("hls/5/720p/index.m3u8")

def test_validate_segment_name_valid():
    utils.validate_segment_name("index0.ts")

def test_validate_segment_name_invalid():
    with pytest.raises(Http404):
        utils.validate_segment_name("../secret.ts")
