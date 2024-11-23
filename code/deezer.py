import requests

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

# Exemple d'utilisation
artist_name = "F.O.O.L"
track_name = "We Are (Original Mix)"
num_results = 3

artwork_urls = get_deezer_artworks(artist_name, track_name, num_results)

if artwork_urls:
    print("URLs des artworks :")
    for url in artwork_urls:
        print(url)