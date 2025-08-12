# import subprocess

# def convert_480p(source):
#     target = source + '_480p.mp4'
#     cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac strict -2"{}"'.format(source, target)
#     subprocess.run(cmd)


import subprocess
import os

def convert_480p(input_path):
    # Create output path
    output_path = f"{input_path}_480p.mp4"

    try:
        subprocess.run([
            'ffmpeg',
            '-i', input_path,
            '-s', 'hd480',
            '-c:v', 'libx264',
            '-crf', '23',
            '-c:a', 'aac',
            '-strict', '-2',
            output_path
        ], check=True)
        print(f"✔ 480p conversion completed: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg conversion failed: {e}")
