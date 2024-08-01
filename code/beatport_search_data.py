import requests
from bs4 import BeautifulSoup
import time
import logging
import random

def search_beatport_track(title):
    search_url = f'https://www.beatport.com/search?q={title.replace(" ", "+")}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Chercher le premier résultat de piste
        track_link = soup.find('href', class_='container')
        if track_link:
            track_id = track_link.get('data-ec-id')
            return track_id
        else:
            print("Aucun résultat trouvé pour ce titre.")
            return None
    else:
        print(f"Échec de la requête : {response.status_code}")
        return None


def search_beatport_track2(title, delay=2, max_retries=3):
    search_url = f'https://www.beatport.com/search?q={title.replace(" ", "+")}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    for attempt in range(max_retries):
        try:
            response = requests.get(search_url, headers=headers)
            time.sleep(delay + random.uniform(0, 2))

            if response.status_code == 200:
                # Rechercher le track_id dans la réponse HTML
                if str(response.content).find('"track_id":') != -1:
                    track_id_index = str(response.content).find('"track_id":') + len('"track_id":')
                    track_id_end_index = str(response.content)[track_id_index:].find(',') + track_id_index
                    track_id = str(response.content)[track_id_index:track_id_end_index]
                    return track_id
                else:
                    logging.info(f"Aucun résultat trouvé pour le titre: {title}")
                    return None
            else:
                logging.warning(f"Échec de la requête ({response.status_code}): tentative {attempt + 1}")
        except Exception as e:
            logging.error(f"Erreur lors de la tentative {attempt + 1}: {e}")
            time.sleep(delay + random.uniform(0, 2))

    return None


if __name__ == '__main__':
    title = 'double touch felea'  # Remplacez par le titre de votre piste
    track_id = search_beatport_track2(title)
    print(f'Track ID: {track_id}')

