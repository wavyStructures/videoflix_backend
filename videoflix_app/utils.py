import os
from pathlib import Path
from django.conf import settings
from django.http import Http404


def safe_media_path(*parts: str) -> Path:
    """
    Build a path under MEDIA_ROOT and ensure the resolved path is inside MEDIA_ROOT.
    Raises Http404 if the candidate path is invalid or outside MEDIA_ROOT.
    """
    base = Path(settings.MEDIA_ROOT).resolve()
    candidate = (base.joinpath(*parts)).resolve(strict=False)  

    if os.path.commonpath([str(base), str(candidate)]) != str(base):
        raise Http404("Forbidden")
    return candidate


def validate_segment_name(segment: str) -> str:
    """
    Ensure the given segment is a safe filename (no path traversal or directories).
    """
    if Path(segment).name != segment or ".." in segment:
        raise Http404("Invalid segment name")
    return segment



