import subprocess
import os

# Optional: absolute path to ffmpeg if it's not in PATH
FFMPEG_BIN = "ffmpeg"  
# On Windows you might need:
# FFMPEG_BIN = r"C:\ffmpeg\bin\ffmpeg.exe"

def convert_480p(input_path: str):
    """
    Convert a video to 480p resolution using ffmpeg.
    Saves the new file alongside the original, with `_480p` suffix.
    """

    # Build output filename correctly: video.mp4 -> video_480p.mp4
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





# # def convert_480p(source):
# #     target = source + '_480p.mp4'
# #     cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac strict -2"{}"'.format(source, target)
# #     subprocess.run(cmd)
# import subprocess
# import os

# def convert_480p(input_path):
#     base, ext = os.path.splitext(input_path)
#     output_path = f"{base}_480p{ext}"

#     FFMPEG_BIN = r"C:\ffmpeg\bin\ffmpeg.exe"
        
#     try:
#         subprocess.run([
#             FFMPEG_BIN,
#             '-i', input_path,
#             '-s', 'hd480',
#             '-c:v', 'libx264',
#             '-crf', '23',
#             '-c:a', 'aac',
#             '-strict', '-2',
#             output_path
#         ], check=True)
#         print(f"✔ 480p conversion completed: {output_path}")
#     except subprocess.CalledProcessError as e:
#         print(f"❌ FFmpeg conversion failed: {e}")

    
    