import requests

def qwant_get_image_urls(query, count):
    try:
        r = requests.get("https://api.qwant.com/v3/search/images",
            params={
                'count': count,
                'q': query,
                't': 'images',
                'safesearch': 1,
                'locale': 'en_US',
                'offset': 0,
                'device': 'desktop'
            },
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
            }
        )

        r.raise_for_status()  # Raise an HTTPError for bad responses

        response_json = r.json()
        if 'data' in response_json and 'result' in response_json['data'] and 'items' in response_json['data']['result']:
            response = response_json['data']['result']['items']
            urls = [item.get('media') for item in response if item.get('media')]
            return urls
        else:
            print("No results found.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

if __name__ == '__main__':
    query = 'daso mein'
    count = 1
    urls = qwant_get_image_urls(query, count)
    for url in urls:
        print(url)