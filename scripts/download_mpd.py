import requests as request
import os
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


def download(folder_name, license_url, mpd_url):
    response = request.get(mpd_url)
    response.raise_for_status()

    original_mpd_file = os.path.join(folder_name, 'dash.mpd')
    print(original_mpd_file)
    with open(original_mpd_file, 'wb') as file:
        file.write(response.content)

    parsed_url = urlparse(mpd_url)
    domain = f'{parsed_url.scheme}://{parsed_url.netloc}'

    root = ET.fromstring(response.content)
    namespace = {'ns0': 'urn:mpeg:dash:schema:mpd:2011', 'cenc': 'urn:mpeg:cenc:2013'}

    periods = root.findall('ns0:Period', namespace)
    print(f'Found {len(periods)} periods.')

    if len(periods) >= 1:
        # Use the first period if only one is present
        if len(periods) == 1:
            target_period = periods[0]
        else:
            target_period = periods[2]

        pssh_elements = target_period.findall('.//cenc:pssh', namespace)
        if pssh_elements:
            pssh = pssh_elements[-1].text
            pssh_file_path = os.path.join(folder_name, 'pssh.txt')
            with open(pssh_file_path, 'w') as pssh_file:
                pssh_file.write(pssh)
            print("pssh was successfully saved to pssh.txt.")

            api_url = "https://cdrm-project.com/"
            json_data = {
                "PSSH": pssh,
                "License URL": 'https://wdvn.blutv.com/',
                "Headers": "{'User-Agent': 'Mozilla/5.0'}",
                "JSON": "{}",
                "Cookies": "{}",
                "Data": "{}",
                "Proxy": ""
            }

            response = request.post(api_url, json=json_data)
            response.raise_for_status()
            response_data = response.json()['Message']
            keys = [line for line in response_data.strip().split('\n') if line]

            print(keys)

            if not keys:
                print("Error: No keys found.")
                sys.exit(1)

            with open(os.path.join(folder_name, 'keys.txt'), 'w') as file:
                for key in keys:
                    file.write(f"{key}\n")
        else:
            print("Tags <pssh> not found.")
            sys.exit(1)

        # If there are multiple periods, retain the third period
        if len(periods) > 1:
            for period in periods:
                root.remove(period)
            root.append(target_period)

            base_urls = target_period.findall('ns0:BaseURL', namespace)
            for base_url in base_urls:
                base_url.text = domain + base_url.text

            tree = ET.ElementTree(root)
            ET.register_namespace('', 'urn:mpeg:dash:schema:mpd:2011')

            new_mpd_file = os.path.join(folder_name, 'dest.mpd')
            tree.write(new_mpd_file, encoding='utf-8', xml_declaration=True)
            print("File was successfully saved.")
        else:
            print("Single period found, using original MPD file.")
            new_mpd_file = os.path.join(folder_name, 'dest.mpd')
            if os.path.exists(new_mpd_file):
                os.remove(new_mpd_file)
            os.rename(original_mpd_file, new_mpd_file)

            # Print URLs for debugging
            for adaptation_set in root.findall('.//ns0:AdaptationSet', namespace):
                for representation in adaptation_set.findall('ns0:Representation', namespace):
                    for base_url in representation.findall('ns0:BaseURL', namespace):
                        print(f"BaseURL: {base_url.text}")
    else:
        print("File contains no periods.")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python download_mpd.py <folder_name> <license_url> <mpd_url>")
        sys.exit(1)
    folder_name = sys.argv[1]
    license_url = sys.argv[2]
    mpd_url = sys.argv[3]
    download(folder_name, license_url, mpd_url)
