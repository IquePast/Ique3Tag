import requests
from IqueMusicTag import IqueMusicTag

def get_deezer_artworks(artist, track, num_results=1):
    """
    Récupère plusieurs URLs d'artworks associés à un artiste et une chanson via l'API Deezer.

    Arguments :
    - artist (str) : Nom de l'artiste.
    - track (str) : Nom du morceau.
    - num_results (int) : Nombre de résultats souhaités.

    Retourne :
    - Une liste contenant les URLs des artworks.
    """
    base_url = "https://api.deezer.com/search"
    params = {
        "q": f"{artist} {track}"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()
        if not data['data']:
            print("Aucun morceau trouvé.")
            return []

        # Extraire les URLs des artworks
        artwork_urls = []
        for result in data['data'][:num_results]:  # Limiter au nombre de résultats souhaités
            artwork_url = result['album']['cover_big']
            artwork_urls.append(artwork_url)

        return artwork_urls

    except Exception as e:
        print(f"Erreur : {e}")
        return []


def get_deezer_track_details(artist, track, num_results=1):
    """
    Récupère des informations détaillées sur une ou plusieurs pistes musicales via l'API Deezer.

    Arguments :
    - artist (str) : Nom de l'artiste.
    - track (str) : Nom de la piste.
    - num_results (int) : Nombre de résultats souhaités.

    Retourne :
    - Une liste contenant les détails des pistes.
    """
    base_url = "https://api.deezer.com/search"
    params = {
        "q": f"artist:'{artist}' track:'{track}'",
        "limit": num_results
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        data = response.json()
        if data.get("total", 0) == 0:
            print("Aucun morceau trouvé sur Deezer.")
            return []

        tags = []
        for track_info in data.get("data", []):
            contributors = [contributor["name"] for contributor in track_info.get("contributors", [])]
            contributors.append(track_info.get("artist", {}).get("name", ""))
            contributors = list(set(filter(None, contributors)))

            tag = IqueMusicTag(
                artiste=track_info.get("artist", {}).get("name", ""),
                titre=track_info.get("title", ""),
                artiste_display=track_info.get("artist", {}).get("name", ""),
                artiste_remix="",
                artiste_ft=", ".join(contributors),
                artiste_all=';'.join(contributors),
                annee=int(track_info.get("release_date", "0000")[:4]) if track_info.get("release_date") else None,
                style=track_info.get("genre_id", None),
                genre=track_info.get("genre_id", None),
                disk=None,
                track=track_info.get("track_position", None),
                album=track_info.get("album", {}).get("title", ""),
                artiste_album=track_info.get("album", {}).get("artist", {}).get("name", ""),
                images_path=track_info.get("album", {}).get("cover_big", None)
            )

            tags.append(tag)

        return tags

    except Exception as e:
        print(f"Erreur lors de la récupération des données Deezer : {e}")
        return []

# Exemple d'utilisation
if __name__ == '__main__':
    artist_name = "Gala"
    track_name = "Freed From desire"
    num_results = 3

    track_details = get_deezer_track_details(artist_name, track_name, num_results)

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