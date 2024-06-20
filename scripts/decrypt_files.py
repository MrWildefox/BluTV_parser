import os
import subprocess
import shutil


def decrypt(folder_name):
    directory = os.path.join(folder_name, "encrypted")
    keys_file = os.path.join(folder_name, "keys.txt")

    if os.name == 'nt':
        mp4decrypt_path = os.path.join(os.getcwd(), "bin/mp4decrypt.exe")
    else:
        mp4decrypt_path = 'mp4decrypt'

    if not os.path.exists(keys_file):
        print("Error: keys.txt not found.")
        exit(1)

    with open(keys_file, 'r') as file:
        keys = file.readlines()
    keys = [key.strip() for key in keys if key.strip()]
    if not keys:
        print("Error: No keys found in keys.txt.")
        exit(1)

    def decrypt_file(input_file, output_file, keys):
        command = [mp4decrypt_path]
        for key in keys:
            command.extend(["--key", key])
        command.extend([input_file, output_file])
        subprocess.run(command)

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith((".mp4", ".m4a")):
                input_file = os.path.join(root, file)
                parent_dir = os.path.dirname(root)
                output_file = os.path.join(parent_dir, file)
                print(f"Decrypting {input_file} to {output_file}")
                decrypt_file(input_file, output_file, keys)

    print("Decryption process completed.")
    shutil.rmtree(directory)
    print(f"Directory {directory} has been removed.")


if __name__ == "__main__":
    decrypt()
