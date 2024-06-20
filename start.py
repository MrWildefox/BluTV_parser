import csv
import os
import sys
import subprocess
import argparse

from scripts import download_mpd
from scripts import download_files
from scripts import decrypt_files
from scripts import convert_file

script_dir = os.path.join(os.getcwd(), 'scripts')
sys.path.append(script_dir)


def handle(folder_name, license_url, mpd_url, base_url):
    print("Download mpd:")
    download_mpd.download(folder_name, license_url, mpd_url)

    print("Download files:")
    download_files.download(folder_name, base_url)

    print("Decrypt files:")
    decrypt_files.decrypt(folder_name)

    print("Convert and merge files:")
    convert_file.convert_and_merge(folder_name)


def process_csv(file_path, delete_rows):
    temp_file_path = file_path + '.tmp'

    with open(file_path, 'r', newline='') as csvfile, open(temp_file_path, 'w', newline='') as temp_file:
        reader = csv.reader(csvfile, delimiter=';')
        writer = csv.writer(temp_file, delimiter=';')

        for row in reader:
            if len(row) < 4:  # Adjusted to include base_url
                continue

            folder_name, license_url, mpd_url, base_url = row
            path = os.path.join('files', folder_name)
            os.makedirs(path, exist_ok=True)
            handle(path, license_url, mpd_url, base_url)

            if not delete_rows:
                writer.writerow(row)

    if delete_rows:
        os.replace(temp_file_path, file_path)
    else:
        os.remove(temp_file_path)


def main():
    parser = argparse.ArgumentParser(description='Process a CSV file and execute commands.')
    parser.add_argument('csv_file', help='Path to the CSV file')
    parser.add_argument('-D', action='store_true', help='Delete rows after processing')

    args = parser.parse_args()
    process_csv(args.csv_file, args.D)


if __name__ == '__main__':
    main()
