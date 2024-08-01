import requests
from bs4 import BeautifulSoup
import re
import json


def google_get_image_urls(query, count):
    try:
        url = "https://www.google.com/search"
        params = {
            'q': query,
            'tbm': 'isch',  # Search for images
            'ijn': 0  # Page number
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses

        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')

        image_urls = []

        for script in scripts:
            if "AF_initDataCallback" in script.text:
                json_text = re.search(r"AF_initDataCallback\((.+)\);", script.string)
                if json_text:
                    json_data = json.loads(json_text.group(1))
                    if 'data' in json_data:
                        data = json_data['data']
                        if isinstance(data, list):
                            for item in data:
                                if isinstance(item, list):
                                    for subitem in item:
                                        if isinstance(subitem, list):
                                            for image_info in subitem:
                                                if isinstance(image_info, str) and image_info.startswith('http'):
                                                    image_urls.append(image_info)
                                                    if len(image_urls) >= count:
                                                        return image_urls
        print("No results found.")
        return []

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []


if __name__ == '__main__':
    query = 'daso mein'
    count = 1
    urls = google_get_image_urls(query, count)
    for url in urls:
        print(url)
