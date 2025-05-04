import requests
import os
import base64
import time
import random

github_token = ""

headers = {
    'Authorization': f'token {github_token}',
    'Accept': 'application/vnd.github.v3+json'
}

crypto_keywords = [
    'from quantcrypt.kdf import Argon2',
    'from quantcrypt.dss import Dilithium',
    'from quantcrypt.kem import Kyber'
]

DOWNLOAD_DIR = "downloaded_files"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def safe_filename(repo_full_name, file_name):
    repo_safe = repo_full_name.replace("/", "_")
    return f"{repo_safe}__{file_name}"

def has_acceptable_license(repo_full_name):
    url = f"https://api.github.com/repos/{repo_full_name}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        license_info = response.json().get("license", {})
        if license_info is None:
            return False
        spdx_id = license_info.get("spdx_id", "").lower()
        print(f"{repo_full_name} license - {spdx_id}")
        return spdx_id in ["mit", "apache-2.0"]
    return False

def search_and_download(keyword, max_pages=2):
    for page in range(1, max_pages + 1):
        print(f"\nSearching '{keyword}' - Page {page}")
        
        search_url = f"https://api.github.com/search/code?q={keyword}+language:Python&per_page=10&page={page}"
        response = requests.get(search_url, headers=headers)

        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break

        results = response.json().get('items', [])
        if not results:
            print("No results found.")
            break

        for item in results:
            file_name = item['name']
            repo_full_name = item['repository']['full_name']
            file_api_url = item['url']  

            print(f"Found file {file_name} in {repo_full_name}")

            if not has_acceptable_license(repo_full_name):
                print(f"Skipping {repo_full_name} due to unsupported license.")
                continue

            file_response = requests.get(file_api_url, headers=headers)
            if file_response.status_code == 200:
                file_json = file_response.json()
                if file_json.get('encoding') == 'base64':
                    try:
                        file_content = base64.b64decode(file_json['content']).decode('utf-8')
                    except Exception as e:
                        print(f"Decoding failed for {file_name}: {e}")
                        continue

                    safe_name = safe_filename(repo_full_name, file_name)
                    file_path = os.path.join(DOWNLOAD_DIR, safe_name)

                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)

                    print(f"Downloaded {file_name} as {safe_name}")
                else:
                    print(f"Unknown encoding for {file_name}")
            else:
                print(f"Failed to fetch file content for {file_name}")

            time.sleep(random.uniform(1, 3))

        time.sleep(random.uniform(5, 8))

# MAIN
if __name__ == "__main__":
    for keyword in crypto_keywords:
        search_and_download(keyword, max_pages=4)
        time.sleep(random.uniform(10, 15))
