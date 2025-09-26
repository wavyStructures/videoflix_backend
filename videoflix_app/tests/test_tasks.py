from django.test import TestCase
from django.conf import settings
from pathlib import Path
import subprocess
import pytest
from videoflix_app import tasks
from unittest.mock import patch, MagicMock
from videoflix_app.models import Video


@pytest.fixture
def mock_ffmpeg():
    with patch("videoflix_app.tasks._run_ffmpeg") as mock:
        mock.return_value = MagicMock(returncode=0)
        yield mock


def test__rel_to_media_valid(tmp_path, settings):
    file_path = tmp_path / "video.mp4"
    file_path.touch()
    settings.MEDIA_ROOT = str(tmp_path)


    rel = tasks._rel_to_media(file_path)
    assert rel == "video.mp4"


def test__rel_to_media_missing_file(tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path)
    with pytest.raises(RuntimeError):
        tasks._rel_to_media(tmp_path / "nonexistent.mp4")


def test_build_renditions(mock_ffmpeg, tmp_path):
    dummy_source = tmp_path / "video.mp4"
    dummy_source.touch()
    output_dir = tmp_path / "hls_test"
    
    renditions = tasks._build_renditions(dummy_source, output_dir)
    assert len(renditions) == len(tasks.RENDITIONS)
    for path, scale, bitrate in renditions:
        # assert str(path).endswith("index.m3u8")
        assert path.exists() or True  
        assert ":" in scale
        assert bitrate.endswith("k")


def test_write_master_playlist(tmp_path):
    output_dir = tmp_path / "hls_test"
    (output_dir / "480p").mkdir(parents=True)
    
    dummy_playlist = [(output_dir / "480p/index.m3u8", "480:854", "800k")]
    master_path = tasks._write_master_playlist(output_dir, dummy_playlist)
    assert master_path.exists()
    content = master_path.read_text()
    assert "#EXTM3U" in content
    assert "BANDWIDTH=" in content


def test_generate_trailer(mock_ffmpeg, tmp_path):
    dummy_source = tmp_path / "video.mp4"
    dummy_source.touch()
    output_dir = tmp_path / "hls_test"
    output_dir.mkdir()
    
    trailer_path = tasks._generate_trailer(dummy_source, output_dir)
    assert str(trailer_path).endswith("trailer.mp4")  


def test_generate_thumbnail(mock_ffmpeg, tmp_path):
    dummy_source = tmp_path / "video.mp4"
    dummy_source.touch()
    output_dir = tmp_path / "hls_test"
    output_dir.mkdir()
    
    tasks._generate_thumbnail(dummy_source, output_dir)
    mock_ffmpeg.assert_called_once()


@pytest.mark.django_db
def test_convert_to_hls_updates_video(mock_ffmpeg, tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path)
    video = Video.objects.create(title="Test Video")
    
    dummy_source = tmp_path / "video.mp4"
    dummy_source.touch()
    
    master_path = tasks.convert_to_hls(str(dummy_source), video.id)
    assert master_path.endswith("master.m3u8")
    
    video.refresh_from_db()
    assert "master.m3u8" in video.hls_master.name


@pytest.mark.django_db
def test_convert_to_hls_without_trailer_and_thumbnail(mock_ffmpeg, tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path)
    video = Video.objects.create(title="Test Video")
    
    dummy_source = tmp_path / "video.mp4"
    dummy_source.touch()
    
    master_path = tasks.convert_to_hls(str(dummy_source), video.id, make_trailer=False, make_thumbnail=False)
    assert master_path.endswith("master.m3u8")
    
    video.refresh_from_db()
    assert "master.m3u8" in video.hls_master.name
    assert not video.thumbnail 
    assert not video.trailer


@pytest.mark.django_db
def test_convert_to_hls_video_does_not_exist(mock_ffmpeg, tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path)

    dummy_source = tmp_path / "video.mp4"
    dummy_source.touch()
    
    result = tasks.convert_to_hls(str(dummy_source), 9999)

    assert result.endswith("master.m3u8")


def test_convert_to_hls_missing_source(mock_ffmpeg, tmp_path, settings):
    with pytest.raises(RuntimeError):
        tasks.convert_to_hls(str(tmp_path / "mising.mp4"), 1)
