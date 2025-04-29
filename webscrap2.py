import requests
import os


github_token = ""

headers = {
    'Authorization': f'token {github_token}',
    'Accept': 'application/vnd.github.v3+json'
}

crypto_keywords = [
    'import cryptography', 
    'from cryptography', 
    'import Crypto', 
    'from Crypto',
    'import nacl',
    'from nacl',
    'import quantcrypt',
    'import cryptodome',
    'from cryptodome',
    'from quantcrypt'
]

def search_and_download(keyword, max_pages=2):
    for page in range(1, max_pages + 1):
        print(f"\n Searching '{keyword}' - Page {page}")
        
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
            file_api_url = item['url']  # <--- Use this, not download_url

            print(f" Found file {file_name} in {repo_full_name}")

            save_dir = repo_full_name.replace("/", "_")
            os.makedirs(save_dir, exist_ok=True)

            # Fetch the file content manually
            file_response = requests.get(file_api_url, headers=headers)
            if file_response.status_code == 200:
                file_json = file_response.json()
                if file_json.get('encoding') == 'base64':
                    import base64
                    file_content = base64.b64decode(file_json['content']).decode('utf-8')
                    
                    file_path = os.path.join(save_dir, file_name)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)
                    
                    print(f"Downloaded {file_name} from {repo_full_name}")
                else:
                    print(f"Unknown encoding for {file_name}")
            else:
                print(f"Failed to fetch file content for {file_name}")

# MAIN
if __name__ == "__main__":
    for keyword in crypto_keywords:
        search_and_download(keyword, max_pages=3)  # Scan 3 pages per keyword

