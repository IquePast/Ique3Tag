import os
import discogs_client
from IqueMusicTag import IqueMusicTag

from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Récupérer le token depuis l'environnement
my_discogs_user_token = os.getenv("DISCOGS_USER_TOKEN")

def clean_artist_name(artist_name):
    import re
    clean_name = re.sub(r'\s\(\d+\)$', '', artist_name)
    return clean_name

def search_track_in_tracklist(song, discogs_tracks):
    import difflib
    # Trouver la meilleure correspondance
    tracks = []

    search_song = song

    # Construire la liste des titres formatés avec artistes
    for discogs_track in discogs_tracks:
        track = ""
        # On verifie que ce n'est pas un separateur (titre de cd par exemple)
        if discogs_track.data['type_'] != 'index':
            try:
                for artist in discogs_track.data['artists']:
                    track = track + artist['name']
                    track = track + " "
                track = track + "- "
            except KeyError:
                search_song = song.split("-", 1)[1].strip()

            track = track + discogs_track.title

        tracks.append(track)

    matches = difflib.get_close_matches(search_song, tracks, n=1,
                                        cutoff=0.6)  # n=1 pour obtenir la meilleure correspondance

    # Retourner l'objet `discogs_track` correspondant à la meilleure correspondance
    if matches:
        best_match = matches[0]
        match_index = tracks.index(best_match)  # Trouver l'index de la correspondance
        return discogs_tracks[match_index]  # Retourner l'objet `discogs_track` correspondant


    # Si aucune correspondance n'est trouvée
    return None


def get_discogs_track_details(searched_song, num_results=1):
    """
    Récupère des informations détaillées sur une ou plusieurs pistes musicales via l'API discogs.

    Arguments :
    - artist (str) : Nom de l'artiste.
    - track (str) : Nom de la piste.
    - num_results (int) : Nombre de résultats souhaités.

    Retourne :
    - Une liste contenant les détails des pistes.
    """

    try:
        d = discogs_client.Client('ExampleApplication/0.1', user_token=my_discogs_user_token)
        releases = d.search(searched_song, type='release')

        i = 0
        tags = []
        for intermediate_release in releases:

            d = discogs_client.Client('ExampleApplication/0.1', user_token=my_discogs_user_token)
            release = d.release(intermediate_release.id)

            track = search_track_in_tracklist(searched_song, release.tracklist)

            if track is None:
                continue

            # Gestion de artiste

            # Savoir le type d'extraction
            songArt = []
            songRmx = []
            songFt = []
            songAll = []

            # main artist
            mainartist = ''
            try:
                for artist in track.data['artists']:
                    mainartist = mainartist + clean_artist_name(artist['name'])
                    if (artist['join'] != ''): mainartist = mainartist + ' ' + artist['join'] + ' '
                    if (clean_artist_name(artist['name']) in songAll) == False:
                        songAll.append(clean_artist_name(artist['name']))
            except KeyError:
                for artist in release.data['artists']:
                    mainartist = mainartist + clean_artist_name(artist['name'])
                    if (artist['join'] != ''): mainartist = mainartist + ' ' + artist['join'] + ' '
                    if (clean_artist_name(artist['name']) in songAll) == False:
                        songAll.append(clean_artist_name(artist['name']))

            if mainartist == '':
                mainartist = clean_artist_name(release.artists[0].name)
            if not (songAll):
                songAll.append(clean_artist_name(release.artists[0].name))

            # Credits - aditional artists
            try:
                for artist in track.data['extraartists']:
                    if artist['role'] == 'Featuring' and (artist['name'] in songFt) == False:
                        songFt.append(clean_artist_name(artist['name']))
                    elif artist['role'] == 'Remix' and (artist['name'] in songRmx) == False:
                        songRmx.append(clean_artist_name(artist['name']))

                    if (clean_artist_name(artist['name']) in songAll) == False:
                        songAll.append(clean_artist_name(artist['name']))
            except:
                pass

            # Featuring
            participant = ''
            numParticipant = 0
            for artists in songFt:
                if numParticipant > 0: participant = participant + ';'
                participant = participant + artists
                numParticipant = numParticipant + 1
            featuring = participant

            # Remix
            participant = ''
            numParticipant = 0
            for artists in songRmx:
                if numParticipant > 0: participant = participant + ';'
                participant = participant + artists
                numParticipant = numParticipant + 1
            remixer = participant

            # All credit
            participant = ''
            numParticipant = 0
            for artists in songAll:
                if numParticipant > 0: participant = participant + ';'
                participant = participant + artists
                numParticipant = numParticipant + 1

            # Album Artiste
            if release.artists[0].name == 'Various':
                album_artist = 'Various Artists'
            else:
                album_artist = clean_artist_name(release.artists[0].name)

            # Style
            listdesStyles = ''
            numStyle = 0
            try:
                for styleZik in release.styles:
                    if numStyle > 0: listdesStyles = listdesStyles + ';'
                    listdesStyles = listdesStyles + styleZik
                    numStyle = numStyle + 1
            except:
                listdesStyles = ''

            #CoverArt
            uri = None
            for image in release.images:
                if image['type'] == 'primary':
                    uri = image['uri']
                    break

            # Si aucune image 'primary' n'est trouvée, prendre la première image disponible
            if uri is None and release.images:
                uri = release.images[0]['uri']

            tag = IqueMusicTag(
                artiste=mainartist,
                titre=track.title,
                artiste_display=mainartist,
                artiste_remix=remixer,
                artiste_ft=featuring,
                artiste_all=participant,
                annee=str(release.year),
                style=listdesStyles,
                genre=release.genres[0],
                #disk=track_info.get("discNumber"),
                #track=track_info.get("trackNumber"),
                album=release.title,
                artiste_album=album_artist,
                images_path=uri,
            )
            tags.append(tag)
            i = i + 1
            if i == num_results:
                break
        return tags
    except Exception as e:
        return []

# Exemple d'utilisation
if __name__ == '__main__':
    track_name = "Gregoire - Toi + Moi"
    num_results = 3

    track_details = get_discogs_track_details(track_name, num_results)

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