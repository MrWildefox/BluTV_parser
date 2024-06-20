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

    if len(periods) > 1:
        for period in periods:
            root.remove(period)

        pssh_elements = periods[2].findall('.//cenc:pssh', namespace)
        if pssh_elements:
            pssh = pssh_elements[-1].text
            pssh_file_path = os.path.join(folder_name, 'pssh.txt')
            with open(pssh_file_path, 'w') as pssh_file:
                pssh_file.write(pssh)
            print("pssh was successfully saved to pssh.txt.")

            api_url = "https://cdrm-project.com/"
            json_data = {
                "PSSH": pssh,
                "License URL": license_url,
                "Headers": "{'User-Agent': 'Mozilla/5.0'}",
                "JSON": "{}",
                "Cookies": "{}",
                "Data": "{}",
                "Proxy": ""
            }

            response = request.post(api_url, json=json_data)
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

        root.append(periods[2])

        base_urls = periods[2].findall('ns0:BaseURL', namespace)
        for base_url in base_urls:
            base_url.text = domain + base_url.text

        tree = ET.ElementTree(root)
        ET.register_namespace('', 'urn:mpeg:dash:schema:mpd:2011')

        new_mpd_file = os.path.join(folder_name, './dest.mpd')
        tree.write(new_mpd_file, encoding='utf-8', xml_declaration=True)
        print("File was successfully saved.")
    elif len(periods) == 1:
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
    download()
