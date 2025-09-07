import os
import subprocess
from pathlib import Path
from django.conf import settings
from django.db import transaction
from django.core.cache import cache
from .models import Video


# FFMPEG_BIN = "ffmpeg"  
# FFMPEG_BIN = r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_BIN = getattr(settings, "FFMPEG_BIN", "ffmpeg")  
HLS_SEG_DUR = int(getattr(settings, "HLS_SEG_DUR", 4))

RENDITIONS = [
    {"name": "480p", "scale": "854:480",  "bitrate": "800k",  "maxrate": "856k",  "bufsize": "1200k"},
    {"name": "720p", "scale": "1280:720", "bitrate": "1400k", "maxrate": "1498k", "bufsize": "2100k"},
    {"name": "1080p","scale": "1920:1080","bitrate": "3000k", "maxrate": "3210k", "bufsize": "4500k"},
]


def _run_ffmpeg(command: list[str]):
    
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
    return os.path.relpath(p.as_posix(), settings.MEDIA_ROOT).replace("\\", "/")

def convert_to_hls(source_path: str, video_id: int, make_trailer: bool = True, make_thumbnail: bool = True) -> str:
    """
    Convert a video file to HLS (.m3u8 + segments)
    """
    source = Path(source_path)
    if not source.exists():
        raise RuntimeError(f"File {source} does not exist")

    output_dir = os.path.join(settings.MEDIA_ROOT, "hls", str(video_id))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    variant_playlists: list[tuple[Path, str, str]] = []
    
    #1) build renditions
    for rendition in RENDITIONS:
        stream_dir = output_dir / rendition["name"]
        stream_dir.mkdir(parents=True, exist_ok=True)
        
        variant_playlists.append((stream_dir / f"{rendition['name']}.m3u8", rendition["scale"], rendition["bitrate"]))
        
        segment_template = (stream_dir / "%d.ts").as_posix()
        width, height = rendition["scale"].split(":")
        
        command = [
            FFMPEG_BIN, 
            "-i", source.as_posix(),
            "-vf", f"scale=w={width}:h={height}:force_original_aspect_ratio=decrease,"
                   f"pad=w=ceil(iw/2)*2:h=ceil(ih/2)*2",
            
            "-hls_time", "10",            
            "-hls_list_size", "0",        
            "-f", "hls",
            segment_template,
        ]
        _run_ffmpeg(command)
        subprocess.run(command, check=True)
        
        #2) write master playlist
        master_path = output_dir / "master.m3u8"
        with master_path.open("w", encoding="utf-8") as m3u8:
            m3u8.write("#EXTM3U\n")
        for vp, bitrate, scale in variant_playlists:
            w, h = scale.split(":")
            # BANDWIDTH expects an integer in bits/sec; we approximate from '800k' -> 800000
            m3u8.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate[:-1]}000,RESOLUTION={w}x{h}\n")
            rel = vp.relative_to(output_dir)
            m3u8.write(f"{rel.as_posix()}\n")

        # 3) trailer and thumbnail
        trailer_path = output_dir / "trailer.mp4"
        if make_trailer:
            _run_ffmpeg([
                FFMPEG_BIN, "-y",
                "-i", source.as_posix(),
                "-ss", "00:00:05", "-t", "5",
                "-c:v", "libx264", "-c:a", "aac",
                trailer_path.as_posix()
            ])

        thumb_path = output_dir / "thumbnail.jpg"
        if make_thumbnail:
            _run_ffmpeg([
                FFMPEG_BIN, "-y",
                "-ss", "00:00:01",  # seek first for faster thumb
                "-i", source.as_posix(),
                "-frames:v", "1",
                thumb_path.as_posix()
            ])
        
        
        # 4) update DB fields atomically
        with transaction.atomic():
            v = Video.objects.select_for_update().get(pk=video_id)
            if hasattr(v, "hls_master"):
                v.hls_master = _rel_to_media(master_path)
            else:
                v.video_file = _rel_to_media(master_path)

            if trailer_path.exists() and hasattr(v, "trailer"):
                v.trailer = _rel_to_media(trailer_path)
            if thumb_path.exists() and hasattr(v, "thumbnail"):
                v.thumbnail = _rel_to_media(thumb_path)
            v.save()

        # 5) best-effort cache clear (harmless if no cache backend)
        try:
            cache.clear()
        except Exception:
            pass

        return master_path.as_posix()
    
    
    
    
            
            
            
            
            
            
            
                            
                
    hls_path = os.path.join(output_dir, f"{base_name}.m3u8")

    # FFmpeg command for HLS
    command = [
        "ffmpeg",
        "-i", input_file,
        "-profile:v", "baseline",
        "-level", "3.0",
        "-start_number", "0",
        "-hls_time", "10",            
        "-hls_list_size", "0",        
        "-f", "hls",
        hls_path
    ]
    subprocess.run(command, check=True)
    return hls_path

def generate_thumbnail(input_file, output_file, time="00:00:01"):
    """
    Grab a frame from the video as a thumbnail
    """
    command = [
        "ffmpeg",
        "-i", input_file,
        "-ss", time,           
        "-vframes", "1",
        output_file
    ]
    subprocess.run(command, check=True)
    return output_file
