from django.test import TestCase
from django.conf import settings
from pathlib import Path


from videoflix_app import utils

def test_safe_media_path_inside_media(self):
    path = utils.test_safe_media_path("hls/5/720p/index.m3u8")
    self.assertTrue(str(path).startswith(str(settings.MEDIA_ROOT)))

def test_validate_segment_name_valid(self):
    utils.validate_segment_name("index0.ts")

def test_validate_segment_name_invalid(self):
    with self.assertRaises(Http404):
        utils._validate_segment_name("../secret")
