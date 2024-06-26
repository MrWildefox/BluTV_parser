import subprocess
import os
import shutil


def find_ffmpeg():
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    if os.name == 'nt':
        ffmpeg_path = os.path.join(os.getcwd(), "bin/ffmpeg.exe")
    else:
        ffmpeg_path = os.path.join(os.getcwd(), "bin/ffmpeg")
    if not os.path.exists(ffmpeg_path):
        raise FileNotFoundError("ffmpeg executable not found.")
    return ffmpeg_path


def convert_and_merge(folder_name):
    # Define paths
    audio_file = os.path.join(folder_name, 'audio-0-0.mp4')
    video_file = os.path.join(folder_name, 'video-0-4.mp4')
    audio_output_file = os.path.join(folder_name, 'film_audio.aac')
    merged_output_file = os.path.join(folder_name, f'{os.path.basename(folder_name)}.mp4')

    # Find ffmpeg
    ffmpeg_path = find_ffmpeg()

    # Extract audio from mp4 file without re-encoding
    extract_audio_cmd = [
        ffmpeg_path,
        '-i', audio_file,
        '-vn',  # No video
        '-acodec', 'copy',
        audio_output_file
    ]

    subprocess.run(extract_audio_cmd, check=True)
    print(f"Extracted audio from {audio_file} to {audio_output_file}")

    # Merge audio and video files without re-encoding
    merge_cmd = [
        ffmpeg_path,
        '-i', video_file,
        '-i', audio_output_file,
        '-c:v', 'copy',  # Copy video without re-encoding
        '-c:a', 'copy',  # Copy audio without re-encoding
        merged_output_file
    ]

    subprocess.run(merge_cmd, check=True)
    print(f"Merged {video_file} and {audio_output_file} into {merged_output_file}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python convert_files.py <folder_name>")
        exit(1)
    folder_name = sys.argv[1]
    convert_and_merge(folder_name)
