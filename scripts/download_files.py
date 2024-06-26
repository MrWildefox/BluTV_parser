import subprocess
import os
from pathlib import Path


def download(dir_path, base_url):
    import config
    print(f'Rate limit {config.rate_limit}')

    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, dir_path, "dest.mpd")

    if not os.path.exists(file_path):
        print(f"Error: {file_path} does not exist.")
        return

    file_url = Path(file_path).as_uri()

    if os.name == 'nt':
        yt_dlp_path = os.path.join(os.getcwd(), "bin/yt-dlp.exe")
    else:
        yt_dlp_path = os.path.join(os.getcwd(), "bin/yt-dlp")

    cmd = [
        yt_dlp_path,
        "--enable-file-urls",
        "--allow-unplayable-formats",
        "--no-warnings",
        "-F", file_url,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    print("Output:", result.stdout)
    if result.stderr:
        print("Error:", result.stderr)

    formats = ["video-0-4.mp4"]
    for fmt in formats:
        video_url = f"{base_url}/{fmt}"
        cmd = [
            yt_dlp_path,
            "--allow-unplayable-formats",
            "--no-warnings",
            "-f", "best",
            video_url,
            "--enable-file-urls",
            "-o", os.path.join(current_dir, dir_path, f"encrypted/{fmt}")
        ]

        if config.rate_limit:
            cmd.extend(['--limit-rate', config.rate_limit])

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading {fmt}: {e}")

    audio_url = f"{base_url}/audio-0-0.mp4"
    cmd = [
        yt_dlp_path,
        "--allow-unplayable-formats",
        "--no-warnings",
        "-f", "best",
        audio_url,
        "--enable-file-urls",
        "-o", os.path.join(current_dir, dir_path, "encrypted/audio-0-0.mp4")
    ]

    if config.rate_limit:
        cmd.extend(['--limit-rate', config.rate_limit])

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error downloading audio file: {e}")

    def download_subtitles(dir_path):
        # Перевірити, чи існує файл subs.txt
        subs_file_path = os.path.join(dir_path, 'subs.txt')
        if not os.path.exists(subs_file_path):
            print(f"Warning: {subs_file_path} does not exist. Skipping subtitle download.")
            return

        # Відкрити файл subs.txt для читання
        with open(subs_file_path, 'r') as file:
            lines = file.readlines()

        # Для кожного ря��ка в файлі
        for i, line in enumerate(lines):
            # Розділити рядок на мову та посилання
            lang, link = line.strip().split(': ')

            # Використати yt-dlp для завантаження субтитрів
            cmd = ['yt-dlp', '-o', os.path.join(dir_path, f'subtitles_{lang}.vtt'), link]
            subprocess.run(cmd, check=True)

    download_subtitles(dir_path)


if __name__ == "__main__":
    download()
