import os
import subprocess
from django.conf import settings


FFMPEG_BIN = "ffmpeg"  
# FFMPEG_BIN = r"C:\ffmpeg\bin\ffmpeg.exe"

def convert_480p(input_path: str):
    """
    Convert a video to 480p resolution using ffmpeg.
    Saves the new file alongside the original, with `_480p` suffix.
    """

    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_480p{ext}"

    try:
        subprocess.run([
            FFMPEG_BIN,
            "-i", input_path,
            "-s", "hd480",
            "-c:v", "libx264",
            "-crf", "23",
            "-c:a", "aac",
            "-strict", "-2",
            output_path
        ], check=True)

        print(f"✔ 480p conversion completed: {output_path}")
        return output_path

    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg conversion failed: {e}")
        return None



def convert_to_hls(input_file, output_dir, base_name):
    """
    Convert a video file to HLS (.m3u8 + segments)
    input_file: full path to uploaded file
    output_dir: directory where HLS files will go
    base_name: name for the output (without extension)
    """
    os.makedirs(output_dir, exist_ok=True)
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
