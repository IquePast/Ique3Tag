import requests

def get_apple_music_artworks(artist, album, num_results=1):
    """
    Récupère plusieurs URLs d'artworks associés à un artiste et un album.

    Arguments :
    - artist (str) : Nom de l'artiste.
    - album (str) : Nom de l'album.
    - num_results (int) : Nombre de résultats souhaités.

    Retourne :
    - Une liste contenant les URLs des artworks.
    """
    # Préparation de l'URL pour l'API iTunes Search
    base_url = "https://itunes.apple.com/search"
    params = {
        "term": f"{artist} {album}",
        "media": "music",
        "entity": "album",
        "limit": num_results
    }

    try:
        # Effectuer la requête à l'API
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Vérifier si la requête a réussi

        # Analyser la réponse JSON
        data = response.json()
        if data["resultCount"] == 0:
            print("Aucun album trouvé.")
            return []

        # Extraire les URLs des artworks
        artwork_urls = []
        for album_info in data["results"]:
            artwork_url = album_info.get("artworkUrl100")
            if artwork_url:
                # Remplacer "100x100" par une taille plus grande (ex. : 600x600)
                artwork_url = artwork_url.replace("100x100", "600x600")
                artwork_urls.append(artwork_url)

        return artwork_urls

    except Exception as e:
        print(f"Erreur : {e}")
        return []

def get_song_artworks(artist, track, num_results=1):
    """
    Récupère plusieurs URLs d'œuvres d'art associées à un artiste et une chanson.

    Arguments :
    - artist (str) : Nom de l'artiste.
    - track (str) : Nom de la chanson.
    - num_results (int) : Nombre de résultats souhaités.

    Retourne :
    - Une liste contenant les URLs des artworks.
    """
    # Préparation de l'URL pour l'API iTunes Search
    base_url = "https://itunes.apple.com/search"
    params = {
        "term": f"{artist} {track}",
        "media": "music",
        "entity": "musicTrack",
        "limit": num_results
    }

    try:
        # Effectuer la requête à l'API
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Vérifier si la requête a réussi

        # Analyser la réponse JSON
        data = response.json()
        if data["resultCount"] == 0:
            print("Aucun titre trouvé.")
            return []

        # Extraire les URLs des artworks
        artwork_urls = []
        for track_info in data["results"]:
            artwork_url = track_info.get("artworkUrl100")
            if artwork_url:
                # Remplacer "100x100" par une taille plus grande (ex. : 600x600)
                artwork_url = artwork_url.replace("100x100", "600x600")
                artwork_urls.append(artwork_url)

        return artwork_urls

    except Exception as e:
        print(f"Erreur : {e}")
        return []

# Exemple d'utilisation
artist = "Coldplay"
track = "Yellow"
num_results = 5

artworks = get_song_artworks(artist, track, num_results)
print(artworks)

# Exemple d'utilisation
artist = "Coldplay"
album = "Parachutes"
num_results = 5

artworks = get_apple_music_artworks(artist, album, num_results)
print(artworks)