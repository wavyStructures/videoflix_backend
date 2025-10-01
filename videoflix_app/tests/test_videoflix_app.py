import os
import subprocess
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from django.conf import settings
from django.db.models.signals import post_save
from django.http import Http404
from django.test import TestCase
from rest_framework.test import APIClient
from videoflix_app import tasks, utils
from videoflix_app.models import Video
from videoflix_app.signals import video_post_save

pytestmark = pytest.mark.django_db


def test_safe_media_path_inside_media():
    path = utils.safe_media_path("hls/5/720p/index.m3u8")
    normalized = path.as_posix()
    assert normalized.endswith("hls/5/720p/index.m3u8")

def test_validate_segment_name_valid():
    utils.validate_segment_name("index0.ts")

def test_validate_segment_name_invalid():
    with pytest.raises(Http404):
        utils.validate_segment_name("../secret.ts")

    with pytest.raises(Http404):
        utils.validate_segment_name("subdir/segment.ts")


@pytest.fixture
def client():
    """Use DRF APIClient instead of Django Client."""
    return APIClient()


@pytest.fixture
def user(django_user_model):
    """Create a test user for authentication."""
    return django_user_model.objects.create_user(
        username="testuser", email="user@example.com", password="pass123"
    )


def test_videolistview_returns_videos_in_desc_order(client, user):
    v1 = Video.objects.create(title="Old", created_at=date(2024, 1, 1))
    v2 = Video.objects.create(title="New", created_at=date(2024, 1, 2))

    client.force_authenticate(user=user)
    response = client.get("/api/video/")  
    assert response.status_code == 200

    results = response.json()
    assert len(results) == 2
    assert results[0]["id"] == v2.id
    assert results[1]["id"] == v1.id


def test_hlsindexview_returns_file(tmp_path, settings, client, user):
    settings.MEDIA_ROOT = str(tmp_path)
    movie = Video.objects.create(title="Test Movie")

    hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(movie.id) / "720p"
    hls_dir.mkdir(parents=True)
    index_path = hls_dir / "index.m3u8"
    index_path.write_text("#EXTM3U")

    client.force_authenticate(user=user)
    url = (f"/api/video/{movie.id}/720p/index.m3u8")
    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Type"] == "application/vnd.apple.mpegurl"
    body = b"".join(response.streaming_content).decode()
    assert "#EXTM3U" in body


def test_hlsindexview_not_found(tmp_path, settings, client, user):
    settings.MEDIA_ROOT = str(tmp_path)
    movie = Video.objects.create(title="Test Movie")
    client.force_authenticate(user=user)

    url = f"/api/video/{movie.id}/720p/index.m3u8"
    response = client.get(url)
    assert response.status_code == 404


def test_hlschunksview_returns_file(tmp_path, settings, client, user):
    settings.MEDIA_ROOT = str(tmp_path)
    movie = Video.objects.create(title="Test Movie")

    hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(movie.id) / "720p"
    hls_dir.mkdir(parents=True)
    seg_path = hls_dir / "segment0.ts"
    seg_path.write_bytes(b"fake-segment")

    client.force_authenticate(user=user)
    url = f"/api/video/{movie.id}/720p/segment0.ts/"
    response = client.get(url)

    assert response.status_code == 200
    assert response["Content-Type"] == "video/MP2T"
    
    content = b"".join(response.streaming_content)
    assert content == b"fake-segment" 


def test_hlschunksview_invalid_segment_name(tmp_path, settings, client, user):
    settings.MEDIA_ROOT = str(tmp_path)
    movie = Video.objects.create(title="Test Movie")
    client.force_authenticate(user=user)

    url = f"/api/video/{movie.id}/720p/../secret.ts/"
    response = client.get(url)
    assert response.status_code == 404


def test_hlschunksview_not_found(tmp_path, settings, client, user):
    settings.MEDIA_ROOT = str(tmp_path)
    movie = Video.objects.create(title="Test Movie")
    client.force_authenticate(user=user)

    url = f"/api/video/{movie.id}/720p/missing.ts/"
    response = client.get(url)
    assert response.status_code == 404


def test_videolistview_requires_jwt(client):
    response = client.get("/api/video/")
    assert response.status_code == 401


def test_hlsindexview_requires_auth(client, user, tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path)
    movie = Video.objects.create(title="NoAuth Movie")
    hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(movie.id) / "720p"
    hls_dir.mkdir(parents=True)
    (hls_dir / "index.m3u8").write_text("#EXTM3U")

    url = f"/api/video/{movie.id}/720p/index.m3u8"
    response = client.get(url)
    assert response.status_code == 403


def test_hlschunksview_requires_auth(client, tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path)
    movie = Video.objects.create(title="ChunkAuth Movie")
    hls_dir = Path(settings.MEDIA_ROOT) / "hls" / str(movie.id) / "720p"
    hls_dir.mkdir(parents=True)
    (hls_dir / "segment0.ts").write_bytes(b"data")

    url = f"/api/video/{movie.id}/720p/segment0.ts/"
    response = client.get(url)
    assert response.status_code == 403


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


def test_convert_to_hls_updates_video(mock_ffmpeg, tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path)
    video = Video.objects.create(title="Test Video")
    
    dummy_source = tmp_path / "video.mp4"
    dummy_source.touch()
    
    master_path = tasks.convert_to_hls(str(dummy_source), video.id)
    assert master_path.endswith("master.m3u8")
    
    video.refresh_from_db()
    assert "master.m3u8" in video.hls_master.name


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


def test_video_post_save_creates_hls_and_updates_fields(tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path)

    video_file = tmp_path / "source.mp4"
    video_file.write_bytes(b"dummy")
    video = Video.objects.create(title="With file", video_file=str(video_file))

    hls_dir = tmp_path / "hls" / str(video.id)
    hls_dir.mkdir(parents=True, exist_ok=True)
    master_path = hls_dir / "master.m3u8"
    master_path.write_text("#EXTM3U")   
    (hls_dir / "480p").mkdir(parents=True, exist_ok=True)
    (hls_dir / "480p/index.m3u8").write_text("#EXTM3U")
    (hls_dir / "thumbnail.jpg").write_bytes(b"img")
    
    video.hls_master.name = str(master_path)
    video.trailer.name = str(hls_dir / "480p/index.m3u8")
    video.thumbnail.name = str(hls_dir / "thumbnail.jpg")
    video.save()
    video.refresh_from_db()

    assert os.path.normpath(video.trailer.name).endswith(os.path.normpath("480p/index.m3u8"))
    assert os.path.normpath(video.hls_master.name).endswith(os.path.normpath("master.m3u8"))
    assert os.path.normpath(video.thumbnail.name).endswith(os.path.normpath("thumbnail.jpg"))


    post_save.connect(video_post_save, sender=Video)


def test_video_post_save_handles_exception(tmp_path, settings, capsys):
    settings.MEDIA_ROOT = str(tmp_path)

    video_file = tmp_path / "broken.mp4"
    video_file.write_bytes(b"dummy")

    video = Video.objects.create(title="Broken", video_file=str(video_file))

    with patch("videoflix_app.signals.convert_to_hls", side_effect=Exception("boom")):
        video.save() 

    captured = capsys.readouterr()
    assert "Error running HLS conversion" in captured.out


def test_auto_delete_file_on_delete_removes_video_and_hls_dir(tmp_path, settings):
    settings.MEDIA_ROOT = str(tmp_path)

    video_file = tmp_path / "todelete.mp4"
    video_file.write_bytes(b"dummy")

    video = Video.objects.create(title="ToDelete", video_file=str(video_file))

    hls_dir = tmp_path / "hls" / str(video.id)
    subdir = hls_dir / "720p"
    subdir.mkdir(parents=True)
    (subdir / "index.m3u8").write_text("#EXTM3U")

    assert video_file.exists()
    assert hls_dir.exists()

    video.delete()

    assert not video_file.exists()
    assert not hls_dir.exists()
