import musicbrainzngs
import requests

# Configurer l'API MusicBrainz
musicbrainzngs.set_useragent("MonApp", "1.0", "monemail@example.com")

def get_album_artwork(artist, album):
    try:
        # Rechercher l'album
        result = musicbrainzngs.search_releases(artist=artist, release=album, limit=1)
        if not result['release-list']:
            print("Album non trouvé.")
            return None

        # Obtenir l'ID de la sortie
        release_id = result['release-list'][0]['id']
        print(f"Release ID trouvé : {release_id}")

        # Récupérer l'artwork via Cover Art Archive
        cover_art_url = f"https://coverartarchive.org/release/{release_id}/front"
        response = requests.get(cover_art_url)

        if response.status_code == 200:
            return response.url  # URL de l'image de la pochette
        else:
            print("Artwork non disponible.")
            return None

    except Exception as e:
        print(f"Erreur : {e}")
        return None

# Exemple d'utilisation
artist_name = "F.O.O.L."
album_name = "We Are (Original Mix)"
artwork_url = get_album_artwork(artist_name, album_name)

if artwork_url:
    print(f"URL de l'artwork : {artwork_url}")