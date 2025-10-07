import os
import subprocess
from pathlib import Path
from django.conf import settings
from .models import Video


FFMPEG_BIN = "ffmpeg"  
HLS_SEG_DUR = int(getattr(settings, "HLS_SEG_DUR", 4))

RENDITIONS = [
    {"name": "480p", "scale": "854:480",  "bitrate": "800k",  "maxrate": "856k",  "bufsize": "1200k"},
    {"name": "720p", "scale": "1280:720", "bitrate": "1400k", "maxrate": "1498k", "bufsize": "2100k"},
    {"name": "1080p","scale": "1920:1080","bitrate": "3000k", "maxrate": "3210k", "bufsize": "4500k"},
]


def _run_ffmpeg(command: list[str]):
    """Run an FFmpeg command and raise error on failure."""
    
    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg exited with code {process.returncode}")

    return process


def _rel_to_media(p: Path):
    """Return path relative to MEDIA_ROOT (for storing in FileFields)."""

    if not p or not p.exists():
        raise RuntimeError(f"Cannot calculate relative path, file does not exist: {p}")
    return os.path.relpath(p.as_posix(), settings.MEDIA_ROOT).replace("\\", "/")


def _build_renditions(source: Path, output_dir: Path) -> list[tuple[Path, str, str]]:
    """Generate HLS renditions (480p, 720p, 1080p)."""

    variant_playlists = []
    for rendition in RENDITIONS:
        stream_dir = output_dir / rendition["name"]
        stream_dir.mkdir(parents=True, exist_ok=True)

        playlist_path = stream_dir / "index.m3u8"
        scale = rendition["scale"]
        bitrate = rendition["bitrate"]
        width, height = scale.split(":")

        command = [
            FFMPEG_BIN,
            "-i", source.as_posix(),
            "-vf", f"scale=w={width}:h={height}:force_original_aspect_ratio=decrease,"
                   f"pad=w=ceil(iw/2)*2:h=ceil(ih/2)*2",
            "-b:v", bitrate,
            "-hls_time", str(HLS_SEG_DUR),
            "-hls_list_size", "0",
            "-f", "hls",
            playlist_path.as_posix()
        ]
        _run_ffmpeg(command)
        variant_playlists.append((playlist_path, rendition['scale'], bitrate))
    return variant_playlists


def _write_master_playlist(output: Path, variant_playlists: list[tuple [Path, str, str]]):
    """Write the master.m3u8 playlist pointing to all renditions."""

    master_path = output / "master.m3u8"
    with master_path.open("w", encoding="utf-8") as m3u8:
        m3u8.write("#EXTM3U\n")
        for playlist_path, scale, bitrate in variant_playlists:
            w, h = scale.split(":")
            bw_int = int(bitrate.rstrip("k")) * 1000
            m3u8.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bw_int},RESOLUTION={w}x{h}\n")
            rel = playlist_path.relative_to(output)
            m3u8.write(f"{rel.as_posix()}\n")
    return master_path


def _generate_trailer(source: Path, output_dir: Path):
    trailer_path = output_dir / "trailer.mp4"
    _run_ffmpeg([
        FFMPEG_BIN, "-y",
        "-i", source.as_posix(),
        "-ss", "00:00:05", "-t", "5",
        "-c:v", "libx264", "-c:a", "aac",
        trailer_path.as_posix()
    ])
    return trailer_path
        

def _generate_thumbnail(source: Path, output_dir: Path):
    thumb_path = output_dir / "thumbnail.jpg"
    _run_ffmpeg([
        FFMPEG_BIN, "-y",
        "-ss", "00:00:01",
        "-i", source.as_posix(),
        "-frames:v", "1",
        thumb_path.as_posix()
    ])
    return thumb_path


def run_hls_pipeline(video_id, source_path):
    """Background task to convert uploaded video to HLS + trailer + thumbnail."""

    try:
        video = Video.objects.get(id=video_id)

        master_path = convert_to_hls(
            source_path=source_path,
            video_id=video.id,
            make_trailer=True,
            make_thumbnail=True,
        )

        if master_path and os.path.exists(master_path):
            video.hls_master.name = os.path.relpath(master_path, settings.MEDIA_ROOT)

        video.save(update_fields=["hls_master", "trailer", "thumbnail"])
        print(f"[RQ] Finished HLS pipeline for video {video.id}")

    except Exception as e:
        print(f"Error running HLS conversion for video {video_id}: {e}")


def convert_to_hls(source_path: str, video_id: int, make_trailer: bool = True, make_thumbnail: bool = True) -> str:
    """Convert a video file to HLS (.m3u8 + segments). Returns the path to the master playlist."""

    source = Path(source_path)
    if not source.exists():
        raise RuntimeError(f"File {source} does not exist")
   
    output_dir = Path(settings.MEDIA_ROOT) / "hls" / str(video_id)
    output_dir.mkdir(parents=True, exist_ok=True)

    variant_playlists = _build_renditions(source, output_dir)
    master_path = _write_master_playlist(output_dir, variant_playlists)

    trailer_path = None
    thumb_path = None

    if make_trailer:
        trailer_path = _generate_trailer(source, output_dir)
    if make_thumbnail:
        thumb_path = _generate_thumbnail(source, output_dir)

    
    try:
        video = Video.objects.get(pk=video_id)
        video.hls_master = _rel_to_media(master_path)
        if trailer_path:
            video.trailer = _rel_to_media(trailer_path)            
        if thumb_path: 
            video.thumbnail = _rel_to_media(thumb_path)
        video.save(update_fields=["hls_master", "trailer", "thumbnail"])
    except Video.DoesNotExist:
        pass

    return master_path.as_posix()


def generate_thumbnail(input_file, output_file, time="00:00:01"):
    """Grab a frame from the video as a thumbnail."""

    _run_ffmpeg ([
        FFMPEG_BIN,
        "-i", input_file,
        "-ss", time,           
        "-vframes", "1",
        output_file
    ])
    return output_file
