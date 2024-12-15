import requests
from datetime import datetime
from IqueMusicTag import IqueMusicTag

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
                artwork_url = artwork_url.replace("100x100", "10000x10000")
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
                artwork_url = artwork_url.replace("100x100", "10000x10000")
                artwork_urls.append(artwork_url)

        return artwork_urls

    except Exception as e:
        print(f"Erreur : {e}")
        return []

def get_itunes_track_details(artist, track, num_results=1):
    """
    Récupère des informations détaillées sur une ou plusieurs pistes musicales via l'API iTunes.

    Arguments :
    - artist (str) : Nom de l'artiste.
    - track (str) : Nom de la piste.
    - num_results (int) : Nombre de résultats souhaités.

    Retourne :
    - Une liste contenant les détails des pistes.
    """
    base_url = "https://itunes.apple.com/search"
    params = {
        "term": f"{artist} {track}",
        "media": "music",
        "entity": "musicTrack",
        "limit": num_results
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()
        if data["resultCount"] == 0:
            print("Aucun morceau trouvé.")
            return []

        # Extraire les détails pour chaque piste
        tags = []
        for track_info in data["results"]:

            # Note : L'API ne fournit pas directement les artistes en featuring ou remix
            # Ces informations peuvent être présentes dans les noms des pistes (e.g., "feat." ou "remix")
            # On peut les extraire avec un traitement supplémentaire
            if "feat." in track_info.get("trackName", "").lower():
                featuring = track_info.get("trackName", "").lower().split("feat.")[1].split(")")[0].strip().title()
            else:
                featuring = ""
            if "remix" in track_info.get("trackName", "").lower():
                remixer = track_info.get("trackName", "").lower().split("remix")[0].strip()
            else:
                remixer = ""

            release_date = track_info.get("releaseDate")
            annee = datetime.strptime(release_date, "%Y-%m-%dT%H:%M:%SZ").year if release_date else None

            tag = IqueMusicTag(
                artiste=track_info.get("artistName", ""),
                titre=track_info.get("trackName", ""),
                artiste_display=track_info.get("artistName", ""),
                artiste_remix=remixer,
                artiste_ft=featuring,
                artiste_all="",
                annee=annee,
                style=None,
                genre=track_info.get("primaryGenreName"),
                disk=track_info.get("discNumber"),
                track=track_info.get("trackNumber"),
                album=track_info.get("collectionName"),
                artiste_album=None,
                images_path=track_info.get("artworkUrl100").replace("100x100", "3000x3000") if track_info.get(
                    "artworkUrl100") else None
            )

            tags.append(tag)

        return tags

    except Exception as e:
        return None

# Exemple d'utilisation
if __name__ == '__main__':
    artist_name = "Daft Punk"
    track_name = "Get Lucky"
    num_results = 15

    track_details = get_itunes_track_details(artist_name, track_name, num_results)

    if track_details:
        print("Détails des pistes trouvées :")
        for track in track_details:
            print(f"Artiste : {track.get('artiste')}")
            print(f"Titre : {track.get('titre')}")
            print(f"Album : {track.get('album')}")
            print(f"Numéro de piste : {track.get('album')}")
            print(f"Numéro de disque : {track.get('album')}")
            print(f"Genre : {track.get('genre')}")
            print(f"Année de sortie : {track.get('annee')}")
            print(f"Artwork : {track.get('images_path')}")
            print(f"featuring : {track.get('artiste_ft')}")
            print("-" * 40)

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