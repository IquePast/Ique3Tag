import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSize, QItemSelectionModel
from PyQt5.QtWidgets import (QApplication,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QProgressBar, QPushButton, QListWidget,
                             QTableWidget, QWidget, QTableWidgetItem, QAbstractItemView, QCompleter, QMenu, QAction,
                             )
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QBuffer

import os
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TRCK, TPOS, TCON,TDRC, TXXX, APIC

import re
import discogs_client

from dotenv import load_dotenv

#Discogs genre
DISCOGS_GENRE = ["", "Blues", "Brass & Military", "Children’s", "Classical", "Electronic", "Folk, World, & Country", "Funk / Soul", "Hip Hop", "Jazz", "Latin", "Non-Music", "Pop", "Reggae", "Rock", "Stage & Screen"]

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Récupérer le token depuis l'environnement
my_discogs_user_token = os.getenv("DISCOGS_USER_TOKEN")

def convert_qpixmap_to_bytes(qpixmap, image_format='JPEG'):
    # Convertir le QPixmap en bytes en utilisant QBuffer
    buffer = QBuffer()
    buffer.open(QBuffer.ReadWrite)
    qpixmap.save(buffer, image_format)
    return buffer.data().data()

def extract_unitary(audio, string):
    try:
        return str(audio[string][0])
    except:
        return ''

def extraire_tag_from_filename(chaine):
    """
    Traite une chaîne de texte pour extraire les informations de l'artiste, du titre,
    et des artistes participants (featuring).

    Args:
        chaine (str): La chaîne de texte à traiter.

    Returns:
        dict: Un dictionnaire contenant 'titre', 'artiste', 'artisteFeat', et 'artisteAll'.
    """
    # Traitement de "myfreemp3"
    chaine = re.sub(r'\s*myfreemp3\.\w+\s*(?=\.\w+$)', '', chaine)

    # Enlever l'extension
    chaine = chaine.replace(".mp3", "").replace(".flac", "")

    # Normaliser les termes de featuring
    chaine = chaine.replace("feat.", "ft.").replace("Feat.", "ft.").replace("Ft.", "ft.")\
                   .replace("Featuring", "ft.").replace("featuring", "ft.")

    # Assigner les parties aux variables artiste et titre
    parts = chaine.split(" - ", 1)
    if len(parts) == 2:
        artiste = parts[0].strip()  # Supprime les espaces avant/après
        titre = parts[1].strip()
    else:
        artiste = ""
        titre = chaine.strip()

    # Extraction des artistes "featuring"
    parts = re.split(r'\s*ft\.\s*', artiste)
    if len(parts) == 2:
        artisteAll = parts[0].strip()  # Supprime les espaces avant/après
        artisteFeat = parts[1].strip()
    else:
        artisteAll = artiste.strip()
        artisteFeat = ""

    # Nettoyage des artistes "featuring"
    parts = re.split(r'\s*,\s*|\s*&\s*', artisteFeat)
    artistes_feat_nettoyes = [artiste.strip() for artiste in parts]

    # Enlever les doublons tout en conservant l'ordre
    vue = set()
    artistes_feat_nettoyes_sans_doublons = [x for x in artistes_feat_nettoyes if not (x in vue or vue.add(x))]
    artisteFeat = ";".join(artistes_feat_nettoyes_sans_doublons)

    # Nettoyage des artistes "all"
    parts = re.split(r'\s*,\s*|\s*&\s*', artisteAll)
    artistes_all_nettoyes = [artiste.strip() for artiste in parts]

    if artistes_feat_nettoyes[0] != "":
        artistes_all_nettoyes.extend(artistes_feat_nettoyes)

    # Enlever les doublons tout en conservant l'ordre
    vue = set()
    artistes_all_nettoyes_sans_doublons = [x for x in artistes_all_nettoyes if not (x in vue or vue.add(x))]
    artisteAll = ";".join(artistes_all_nettoyes_sans_doublons)

    # Retourner les résultats dans un dictionnaire
    return {
        "titre": titre,
        "artiste": artiste,
        "artisteFeat": artisteFeat,
        "artisteAll": artisteAll
    }

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



#ICI
class MyTableWidget(QTableWidget):
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns, parent)
        self.selected_cells = {}  # Stocke la cellule sélectionnée pour chaque colonne

        # Permettre la sélection multiple
        self.setSelectionMode(QAbstractItemView.MultiSelection)

        # Connecter l'événement de clic sur les cellules
        self.cellClicked.connect(self.handle_cell_click)

        self.last_filled_row = -1  # Initialise à -1, car aucune ligne n'est remplie au départ

    def setPhotoViewer(self, photo_viewer):
        """Permet de définir le viewer pour afficher les images."""
        self.photo_viewer = photo_viewer

    def handle_cell_click(self, row, column):
        # Accéder au modèle de sélection
        selection_model = self.selectionModel()

        # Si la cellule est déjà sélectionnée, la désélectionner
        if (row, column) == self.selected_cells.get(column):
            index = self.model().index(row, column)
            selection_model.select(index, QItemSelectionModel.Deselect)
            del self.selected_cells[column]
        else:
            # Désélectionner la cellule précédemment sélectionnée dans cette colonne, le cas échéant
            if column in self.selected_cells:
                previous_row = self.selected_cells[column][0]
                previous_index = self.model().index(previous_row, column)
                selection_model.select(previous_index, QItemSelectionModel.Deselect)

            # Sélectionner la nouvelle cellule
            index = self.model().index(row, column)
            selection_model.select(index, QItemSelectionModel.Select)
            self.selected_cells[column] = (row, column)

        # Vérifier si la colonne est "Image Url"
        if column == 10 and self.photo_viewer:  # Index de la colonne "Image Url"
            item = self.item(row, column)
            if item:
                url = item.text()
                self.display_image_from_url(url)
            else:
                self.photo_viewer.fill_with_blank()

    def display_image_from_url(self, url):
        pixmap = create_pixmap_from_url(url)
        self.photo_viewer.update_from_pixmap(pixmap)

class photoViewer:
    def __init__(self):
        self.Image = ImageLabel()
        self.pixmap_original = None
        self.labelPictureInformation = QLabel("-")
        self.labelPictureInformation.setAlignment(Qt.AlignCenter)
        self.labelPictureInformation.mousePressEvent = self.on_label_click  # Connecter l'événement de clic

        # Connexion du menu contextuel
        self.Image.setContextMenuPolicy(Qt.CustomContextMenu)
        self.Image.customContextMenuRequested.connect(self.show_context_menu)

    def update_from_pixmap(self, pixmap):
        """Met à jour le viewer avec le pixmap téléchargé."""
        if pixmap is None:
            self.Image.fill_with_blank()
            self.pixmap_original = None
            self.labelPictureInformation.setText("-")
        else:
            aspect_ratio_mode = Qt.KeepAspectRatio
            self.pixmap_original = pixmap
            pixmap_resized = pixmap.scaled(300, 300, aspect_ratio_mode)
            self.Image.setPixmap(pixmap_resized)
            self.labelPictureInformation.setText(
                "" + str(pixmap.height()) + "x" + str(pixmap.width()))

    def fill_with_blank(self):
        self.Image.fill_with_blank()
        self.labelPictureInformation.setText("-")
        self.pixmap_original = None

    def get_pixmap_original(self):
        return self.pixmap_original

    def show_context_menu(self, pos):
        """Affiche le menu contextuel pour supprimer ou ajouter une image."""
        context_menu = QMenu(self.Image)

        # Option pour supprimer l'image
        remove_action = QAction("Remove Image", self.Image)
        remove_action.triggered.connect(self.remove_image)
        context_menu.addAction(remove_action)

        # Option pour ajouter une image depuis le presse-papier
        add_action = QAction("Add Image", self.Image)
        add_action.triggered.connect(self.add_image_from_clipboard)
        context_menu.addAction(add_action)

        # Afficher le menu à la position du clic
        context_menu.exec_(self.Image.mapToGlobal(pos))

    def remove_image(self):
        """Supprime l'image affichée."""
        self.Image.fill_with_blank()
        self.pixmap_original = None
        self.labelPictureInformation.setText("-")

    def add_image_from_clipboard(self):
        """Ajoute une image depuis le presse-papier."""
        clipboard = QApplication.clipboard()
        pixmap = clipboard.pixmap()

        if not pixmap.isNull():
            self.update_from_pixmap(pixmap)
        else:
            # Si le presse-papier ne contient pas d'image, vérifier si le texte est une URL.
            clipboard_text = clipboard.text()

            # Vérifier si le texte du presse-papier est une URL valide
            if clipboard_text.startswith("http://") or clipboard_text.startswith("https://"):
                pixmap_from_url = create_pixmap_from_url(clipboard_text)
                if not pixmap_from_url.isNull():
                    self.update_from_pixmap(pixmap_from_url)

    def on_label_click(self, event):
        """Ouvre la fenêtre avec l'image originale lorsque le label est cliqué."""
        if self.pixmap_original is not None:
            self.open_image_window(self.pixmap_original)

    def open_image_window(self, pixmap):
        """Crée une fenêtre pour afficher l'image à sa taille originale."""
        image_window = QDialog()
        image_label = QLabel(image_window)
        image_label.setPixmap(pixmap)
        image_window.setWindowTitle("Image Originale")
        image_window.setGeometry(100, 100, pixmap.width(), pixmap.height())
        image_window.exec_()


class ImageInList:
    def __init__(self, nameInlist):
        super().__init__()

        self.nameInList = nameInlist
        self.pixmap = None
        self.filename_with_path = None

    def set_filename_with_path(self, filename_with_path):
        self.filename_with_path = filename_with_path

    def set_pixmap(self, pixmap):
        self.pixmap = pixmap

    def get_name_in_list(self):
        return self.nameInList

    def get_pixmap(self):
        return self.pixmap

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.fill_with_blank()

    def fill_with_blank(self):
        self.setText('\n\n No image to display \n\n')
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')

    def setPixmap(self, image):
        super().setPixmap(image)




class MusiqueFile:
    def __init__(self, old_file_name, path):
        super().__init__()
        self.audio_file = None
        self.metadata = None
        self.old_file_name = old_file_name
        self.old_file_name_with_path = path + r'\\' + old_file_name
        self.file_type = None
        self.Artiste = None
        self.Titre = None
        self.ArtisteDisplay = None
        self.ArtisteRemix = None
        self.ArtisteFt = None
        self.ArtisteAll = None
        self.Annee = None
        self.Style = None
        self.Genre = None
        self.Disk = None
        self.Track = None
        self.Album = None
        self.ArtisteAlbum = None
        self.Image = None        # image qu'on a choisi
        self.tracks_info = []    # data trouvé sur internet

    def get_name_in_list(self):
        return self.old_file_name

    def extract_image(self):
        for tag in self.metadata.tags.values():
            if tag.FrameID == 'APIC':
                pixmap = QPixmap()
                pixmap.loadFromData(tag.data)
                self.Image = pixmap
                break

    def get_image_from_web(self):
        purged_name = self.old_file_name
        purged_name = purged_name.replace(purged_name[purged_name.find('myfreemp3'):purged_name.find('myfreemp3') + len('myfreemp3') + 4], '')
        purged_name = purged_name.replace('.mp3', '').replace('.flac', '')
        create_ImageInList_from_web(self.Images, purged_name, 10)
        create_ImageInList_from_web(self.Images, 'soundcloud' + purged_name, 4)
        create_ImageInList_from_web(self.Images, 'beatport' + purged_name, 4)

    def get_tracks_info_from_web(self):
        purged_name = self.old_file_name
        purged_name = purged_name.replace(purged_name[purged_name.find('myfreemp3'):purged_name.find('myfreemp3') + len('myfreemp3') + 4], '')
        purged_name = purged_name.replace('.mp3', '').replace('.flac', '')
        song_info_from_extract = extraire_tag_from_filename(purged_name)
        if self.ArtisteDisplay == '':
            artiste = song_info_from_extract["artiste"]
        else:
            artiste = self.ArtisteDisplay

        if self.ArtisteDisplay == '':
            titre = song_info_from_extract["titre"]
        else:
            titre = self.Titre
        self.tracks_info.extend(self.get_tracks_info_from_all_bdd(artiste, titre))

    def get_tracks_info_from_all_bdd(self, artiste, titre):
        track_info = []
        track_info.extend(self.get_tracks_info_from_discogs_query(artiste, titre))
        track_info.extend(self.get_tracks_info_from_applemusic_query(artiste, titre))
        track_info.extend(self.get_tracks_info_from_deezer_query(artiste, titre))
        return track_info

    def get_tracks_info_from_discogs_query(self, artiste, titre):
        from discogs import get_discogs_track_details
        searched_song = artiste + " - " + titre
        tracks_info = get_discogs_track_details(searched_song, 5)
        return tracks_info

    def get_tracks_info_from_applemusic_query(self, artiste, titre):
        from apple_music import get_itunes_track_details
        tracks_info = get_itunes_track_details(artiste, titre, 5)
        return tracks_info

    def get_tracks_info_from_deezer_query(self, artiste, titre):
        from deezer import get_deezer_track_details
        tracks_info = get_deezer_track_details(artiste, titre, 3)
        return tracks_info

    def get_image_from_url(self, url):
        create_ImageInList_from_Url(self.Images, url)

    def set_data_from_groupeediteurTag(self, groupeediteurTag):
        self.Artiste = groupeediteurTag.zoneTextTitre.text()
        self.Titre = groupeediteurTag.zoneTextTitre.text()
        self.ArtisteDisplay = groupeediteurTag.zoneTextArtistAsDisplay.text()
        self.ArtisteRemix = groupeediteurTag.zoneTextArtistRemix.text()
        self.ArtisteFt = groupeediteurTag.zoneTextArtistFeaturing.text()
        self.ArtisteAll = groupeediteurTag.zoneTextArtistAll.text()
        self.Annee = groupeediteurTag.zoneTextAnnee.text()
        self.Style = groupeediteurTag.zoneTextStyle.text()
        self.Genre = groupeediteurTag.zoneTextGenre.text()
        self.Disk = groupeediteurTag.zoneTextDisc.text()
        self.Track = groupeediteurTag.zoneTextNum.text()
        self.Album = groupeediteurTag.zoneTextAlbum.text()
        self.ArtisteAlbum = groupeediteurTag.zoneTextAlbumArtist.text()
        self.Image = groupeediteurTag.photoViewer.get_pixmap_original()

class FlacFile(MusiqueFile):
    def __init__(self, old_file_name, path):
        super().__init__(old_file_name, path)
        self.old_file_name = old_file_name
        self.old_file_name_with_path = path + r'\\' + old_file_name
        self.file_type = 'flac'

    def extract_tag(self):
        from mutagen.flac import FLAC
        audio = FLAC(self.old_file_name_with_path)
        self.audio_file = audio
        self.metadata = mutagen.File(self.old_file_name_with_path)
        self.Titre = extract_unitary(audio, 'title')

        self.Artiste = extract_unitary(audio, 'artist')
        self.ArtisteAll = extract_unitary(audio, 'artists (All)')
        self.ArtisteRemix = extract_unitary(audio, 'Artist Remix')
        self.ArtisteFt = extract_unitary(audio, 'artist ft')
        self.ArtisteDisplay = self.Artiste

        self.ArtisteAlbum = extract_unitary(audio, 'albumartist')
        self.Album = extract_unitary(audio, 'Album')
        self.Track = extract_unitary(audio, 'tracknumber')
        self.Disk = extract_unitary(audio, 'discnumber')
        self.Genre = extract_unitary(audio, 'genre')
        self.Style = extract_unitary(audio, 'style')
        self.Annee = extract_unitary(audio, 'date')
        self.extract_image()

    def saveTag(self):
        from mutagen.flac import FLAC, Picture
        audio = FLAC(self.old_file_name_with_path)
        audio["title"] = self.Titre
        audio["artist"] = self.ArtisteDisplay
        audio["albumartist"] = self.ArtisteAlbum
        audio["album artist"] = self.ArtisteAlbum
        audio["artists (All)"] = self.ArtisteAll
        audio["Artist Remix"] = self.ArtisteRemix
        audio["artist ft"] = self.ArtisteFt
        audio["album"] = self.Album
        audio["tracknumber"] = self.Track
        audio["discnumber"] = self.Disk
        audio["genre"] = self.Genre
        audio["style"] = self.Style
        audio["date"] = self.Annee

        # Créer un objet Picture
        #picture = Picture()
        #picture.data = image_data
        #picture.type = image_type  # 3 correspond à "Cover (front)"
        #picture.mime = "image/jpeg"  # Ou "image/png" selon le type d'image
        #picture.desc = "Cover"

        # Ajouter l'image aux blocs de métadonnées du fichier FLAC
        #audio.add_picture(picture)

        audio.save()

class Mp3File(MusiqueFile):
    def __init__(self, old_file_name, path):
        super().__init__(old_file_name, path)
        self.old_file_name = old_file_name
        self.old_file_name_with_path = path + r'\\' + old_file_name
        self.file_type = 'mp3'

    def extract_tag(self):
        self.metadata = mutagen.File(self.old_file_name_with_path)
        audio = ID3(self.old_file_name_with_path)
        self.audio_file = audio
        self.Titre = extract_unitary(audio, 'TIT2')
        self.Artiste = extract_unitary(audio, 'TPE1')
        self.ArtisteDisplay = self.Artiste
        self.ArtisteAlbum = extract_unitary(audio, 'TPE2')
        self.Album = extract_unitary(audio, 'TALB')
        self.Track = extract_unitary(audio, 'TRCK')
        self.Disk = extract_unitary(audio, 'TPOS')
        self.Genre = extract_unitary(audio, 'TCON')
        self.Annee = extract_unitary(audio, 'TDRC')

        # TXXX
        self.Style = ''
        self.ArtisteAll = ''
        self.ArtisteRemix = ''
        self.ArtisteFt = ''

        audio = MP3(self.old_file_name_with_path, ID3=ID3)
        for tag in audio.tags.getall('TXXX'):
            if tag.desc == 'Style':
                self.Style = tag.text[0]
            if tag.desc == 'Artists (All)':
                self.ArtisteAll = tag.text[0]
            if tag.desc == 'Artist Remix':
               self.ArtisteRemix = tag.text[0]
            if tag.desc == 'Artist ft':
                self.ArtisteFt = tag.text[0]

        self.extract_image()

    def saveTag(self):
        audio = ID3(self.old_file_name_with_path)
        audio.add(TIT2(encoding=3, text=self.Titre))
        audio.add(TPE1(encoding=3, text=self.ArtisteDisplay))
        audio.add(TPE2(encoding=3, text=self.ArtisteAlbum))
        audio.add(TXXX(encoding=3, desc='Artists (All)', text=self.ArtisteAll))
        audio.add(TXXX(encoding=3, desc='Artist Remix', text=self.ArtisteRemix))
        audio.add(TXXX(encoding=3, desc='Artist ft', text=self.ArtisteFt))
        audio.add(TALB(encoding=3, text=self.Album))
        audio.add(TRCK(encoding=3, text=self.Track))
        audio.add(TPOS(encoding=3, text=self.Disk))
        audio.add(TCON(encoding=3, text=self.Genre))
        audio.add(TXXX(encoding=3, desc='Style', text=self.Style))
        audio.add(TDRC(encoding=3, text=self.Annee))

        # Enleve les images existantes
        apic_tags = [tag for tag in audio.keys() if tag.startswith('APIC')]
        for tag in apic_tags:
            audio.delall(tag)

        # Créer un objet APIC pour l'image
        if self.Image:
            image_mime = 'image/jpeg'
            image_data = convert_qpixmap_to_bytes(self.Image,
                                                  image_format=image_mime.split('/')[1].upper())
            apic = APIC(
                encoding=3,  # 3 = UTF-8
                mime=image_mime,  # 'image/jpeg' ou 'image/png'
                type=3,  # 3 = Cover (front)
                desc=u'Cover',
                data=image_data
            )

            audio.add(apic)
        audio.save()




def create_pixmap_from_url(url):
    """
    Télécharge une image à partir d'une URL et retourne un QPixmap.

    Args:
        url (str): L'URL de l'image.

    Returns:
        QPixmap | None: Le QPixmap de l'image téléchargée, ou None en cas d'erreur.
    """
    from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
    from PyQt5.QtCore import QUrl, QEventLoop
    from PyQt5.QtGui import QPixmap
    if not url or not isinstance(url, str):
        print("URL invalide.")
        return None

    try:
        # Vérification de l'URL
        qurl = QUrl(url)
        if not qurl.isValid() and not qurl.isLocalFile() and not qurl.isRelative():
            print(f"URL non valide : {url}")
            return None

        # Gestionnaire réseau
        network_manager = QNetworkAccessManager()
        request = QNetworkRequest(qurl)

        # Envoyer la requête
        reply = network_manager.get(request)

        # Attendre la fin de la requête avec un QEventLoop
        loop = QEventLoop()
        reply.finished.connect(loop.quit)
        loop.exec_()

        # Vérifier les erreurs de réseau
        if reply.error() != QNetworkReply.NoError:
            print(f"Erreur réseau : {reply.errorString()}")
            return None

        # Lire les données
        image_data = reply.readAll()
        if not image_data:
            print("Les données de l'image sont vides.")
            return None

        # Créer le QPixmap
        pixmap = QPixmap()
        if not pixmap.loadFromData(image_data):
            print("Impossible de charger l'image à partir des données.")
            return None

        return pixmap

    except Exception as e:
        print(f"Une erreur inattendue s'est produite : {e}")
        return None

    finally:
        # Nettoyer
        reply.deleteLater()

def download_and_handle_image(url, images_list):
    pixmap = create_pixmap_from_url(url)
    if pixmap is not None:
        image_from_web = ImageInList(str(url))
        image_from_web.set_pixmap(pixmap)
        return image_from_web
    else:
        return None


def create_ImageInList_from_web(Images, query, number_of_image):
    from qwant_search_image import qwant_get_image_urls
    try:
        urls = qwant_get_image_urls(query, number_of_image)
    except:
        return

    for url in urls:
        try:
            download_and_handle_image(url, Images)
        except:
            pass

def create_ImageInList_from_Url(Images, url):
    try:
        download_and_handle_image(url, Images)
    except:
        pass


def get_object_from_list(item, object_list):
    if item is not None:
        for Objects in object_list:
            if item.text() == Objects.get_name_in_list():
                return Objects

class DiscogsListWindow(QWidget):
    # Constantes pour les colonnes
    COL_DISCOGS_TITRE = 0
    COL_DISCOGS_ARTISTE_AS_DISPLAY = 1
    COL_DISCOGS_ARTISTE_FEAT = 2
    COL_DISCOGS_ARTISTE_REMIX = 3
    COL_DISCOGS_ARTISTE_ALL = 4
    COL_DISCOGS_GENRE = 5
    COL_DISCOGS_STYLE = 6
    COL_DISCOGS_ANNEE = 7
    COL_DISCOGS_ALBUM = 8
    COL_DISCOGS_ALBUM_ARTIST = 9
    COL_ARTWORK_URL = 10

    def __init__(self, main_window, song_info):
        super().__init__()

        def createTableurDiscogs(self):
            self.ListDiscogs = QWidget()
            self.ListDiscogs.tableWidget = MyTableWidget(100, 11)
            self.ListDiscogs.tableWidget.setRowCount(100)
            self.ListDiscogs.tableWidget.setColumnCount(11)
            self.ListDiscogs.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.ListDiscogs.tableWidget.setHorizontalHeaderLabels(
                ['Titre', 'Artiste As Display', 'Artiste Featuring', 'Artiste Remix', 'Artiste All', 'Genre', 'Style', 'Annee', 'Album', 'Artist Album', 'Image Url'])
            # Définir des largeurs spécifiques pour les colonnes
            column_widths = [100, 100, 80, 80, 150, 100, 100, 80, 100, 100, 250]  # Largeurs personnalisées
            for col, width in enumerate(column_widths):
                self.ListDiscogs.tableWidget.setColumnWidth(col, width)

            tab1hbox = QHBoxLayout()
            tab1hbox.setContentsMargins(5, 5, 5, 5)
            tab1hbox.addWidget(self.ListDiscogs.tableWidget)
            #
            item = QTableWidgetItem()
            self.ListDiscogs.tableWidget.setItem(0, 1, item)
            self.ListDiscogs.setLayout(tab1hbox)

        def createImageViewer(self):
            self.groupeImageViewer = QGroupBox("Cover")
            self.groupeImageViewer.photoViewer = photoViewer()

            gridImageViewer = QGridLayout()
            gridImageViewer.addWidget(self.groupeImageViewer.photoViewer.Image, 0, 0, 10, 3)
            gridImageViewer.addWidget(self.groupeImageViewer.photoViewer.labelPictureInformation, 10, 0, 1, 3)
            self.groupeImageViewer.setLayout(gridImageViewer)

        def createRechercheManuel(self):
            self.groupeRecherche = QGroupBox("Recherche manuelle")
            # Creation Bouton search
            labelArtist = QLabel("Artist")
            self.groupeRecherche.zone_texte_Artiste = QLineEdit(self)
            labelTitre = QLabel("Titre")
            self.groupeRecherche.zone_texte_Titre = QLineEdit(self)
            discogs_search = QPushButton("Recherche", self)
            discogs_search.clicked.connect(self.search_track_info_from_internet_query_from_zone_texte_recherche)

            gridRecherche = QGridLayout()
            gridRecherche.addWidget(labelArtist, 0, 0)
            gridRecherche.addWidget(self.groupeRecherche.zone_texte_Artiste, 0, 1)
            gridRecherche.addWidget(labelTitre, 0, 2)
            gridRecherche.addWidget(self.groupeRecherche.zone_texte_Titre, 0, 3)
            gridRecherche.addWidget(discogs_search, 0, 4)
            self.groupeRecherche.setLayout(gridRecherche)

        # Référence à la fenêtre principale
        self.main_window = main_window
        self.song_info = song_info

        # Configuration de la nouvelle fenêtre
        self.setWindowTitle("Remplissage via Discogs")
        self.setMinimumSize(1700, 500)

        #Creation de la zone de recherche manuelle
        createRechercheManuel(self)
        #Creation du tableaur discogs
        createTableurDiscogs(self)
        # Creation Image viewer
        createImageViewer(self)

        self.ListDiscogs.tableWidget.setPhotoViewer(self.groupeImageViewer.photoViewer)

        # Creation Bouton Appliquer
        discogs_valider = QPushButton("Appliquer", self)
        discogs_valider.clicked.connect(self.write_to_main_window)  # Connecter le bouton à la méthode d'écriture

        # Layout pour le bouton dans la nouvelle fenêtre
        grid = QGridLayout()
        grid.addWidget(self.groupeRecherche, 0, 0)
        grid.addWidget(self.ListDiscogs, 1, 0, 5, 10)
        grid.addWidget(discogs_valider, 6, 0)
        grid.addWidget(self.groupeImageViewer, 0, 11, 7, 1)  # Étendre sur toutes les lignes (1 colonne à droite)

        # Définition des ratios d'étirement des colonnes
        grid.setColumnStretch(0, 3)  # Deux tiers pour la partie gauche
        grid.setColumnStretch(11, 1)  # Un tiers pour la partie droite
        self.setLayout(grid)

        #remplissage
        if self.song_info is not None:
            song_info_from_extract = extraire_tag_from_filename(self.song_info.old_file_name)
            self.groupeRecherche.zone_texte_Artiste.setText(song_info_from_extract["artiste"])
            self.groupeRecherche.zone_texte_Titre.setText(song_info_from_extract["titre"])

            self.fill_discogs_table_from_internet_query()

    def setListDiscogsTableur(self, track_info):
        """
        Remplit une ligne spécifique avec les données fournies dans le dictionnaire TrackInfo.

        :param ligne: Indice de la ligne à remplir.
        :param track_info: Dictionnaire contenant les informations d'une piste.
        """
        # Mappage entre les colonnes et les clés du dictionnaire TrackInfo
        column_mapping = {
            self.COL_DISCOGS_TITRE: track_info.get("titre"),
            self.COL_DISCOGS_ARTISTE_AS_DISPLAY: track_info.get("artiste"),
            self.COL_DISCOGS_ARTISTE_REMIX: track_info.get("artiste_remix"),
            self.COL_DISCOGS_ARTISTE_FEAT: track_info.get("artiste_ft"),
            self.COL_DISCOGS_ARTISTE_ALL: track_info.get("artiste_all"),
            self.COL_DISCOGS_GENRE: track_info.get("genre"),
            self.COL_DISCOGS_STYLE: track_info.get("style"),
            self.COL_DISCOGS_ANNEE: str(track_info.get("annee")),
            self.COL_DISCOGS_ALBUM: track_info.get("album"),
            self.COL_DISCOGS_ALBUM_ARTIST: track_info.get("artiste_album"),
            self.COL_ARTWORK_URL: track_info.get("images_path"),
        }

        ligne = self.ListDiscogs.tableWidget.last_filled_row + 1

        # Remplit les cellules correspondantes
        for colonne, textAecrire in column_mapping.items():
            if textAecrire is not None:  # Évite les valeurs None
                item = QTableWidgetItem()
                item.setText(textAecrire)
                self.ListDiscogs.tableWidget.setItem(ligne, colonne, item)

        self.ListDiscogs.tableWidget.last_filled_row = ligne

    def fill_discogs_table_from_discogs_query(self, searched_song):
        from discogs import get_discogs_track_details
        tracks_info = get_discogs_track_details(searched_song, 5)
        for track_info in tracks_info:
            self.setListDiscogsTableur(track_info)

    def fill_discogs_table_from_applemusic_query(self, artist, tracks):
        from apple_music import get_itunes_track_details
        tracks_info = get_itunes_track_details(artist, tracks, 5)
        for track_info in tracks_info:
            self.setListDiscogsTableur(track_info)

    def fill_discogs_table_from_internet_query(self):
        self.ListDiscogs.tableWidget.clearContents()
        self.ListDiscogs.tableWidget.last_filled_row = -1
        if self.song_info is not None:
            for track_info in self.song_info.tracks_info:
                self.setListDiscogsTableur(track_info)

    def search_track_info_from_internet_query_from_zone_texte_recherche(self):
        artiste = self.groupeRecherche.zone_texte_Artiste.text()
        titre = self.groupeRecherche.zone_texte_Titre.text()
        if artiste == '' or titre == '' or self.song_info is None:
            return

        self.song_info.tracks_info.extend(self.song_info.get_tracks_info_from_all_bdd(artiste, titre))
        self.ListDiscogs.tableWidget.clearContents()
        self.ListDiscogs.tableWidget.last_filled_row = -1
        if self.song_info is not None:
            for track_info in self.song_info.tracks_info:
                self.setListDiscogsTableur(track_info)

    def write_to_main_window(self):
        # Dictionnaire associant les colonnes aux champs de groupeediteurTag
        column_to_field = {
            self.COL_DISCOGS_TITRE: self.main_window.groupeediteurTag.zoneTextTitre,
            self.COL_DISCOGS_ARTISTE_AS_DISPLAY: self.main_window.groupeediteurTag.zoneTextArtistAsDisplay,
            self.COL_DISCOGS_ARTISTE_FEAT: self.main_window.groupeediteurTag.zoneTextArtistFeaturing,
            self.COL_DISCOGS_ARTISTE_REMIX: self.main_window.groupeediteurTag.zoneTextArtistRemix,
            self.COL_DISCOGS_ARTISTE_ALL: self.main_window.groupeediteurTag.zoneTextArtistAll,
            self.COL_DISCOGS_GENRE: self.main_window.groupeediteurTag.zoneTextGenre,
            self.COL_DISCOGS_STYLE: self.main_window.groupeediteurTag.zoneTextStyle,
            self.COL_DISCOGS_ANNEE: self.main_window.groupeediteurTag.zoneTextAnnee,
            self.COL_DISCOGS_ALBUM: self.main_window.groupeediteurTag.zoneTextAlbum,
            self.COL_DISCOGS_ALBUM_ARTIST: self.main_window.groupeediteurTag.zoneTextAlbumArtist,
            self.COL_ARTWORK_URL: self.main_window.groupeediteurTag.photoViewer,
        }

        # Boucle sur chaque colonne et champ associé
        for column, field in column_to_field.items():
            # Vérifier si une cellule est sélectionnée dans cette colonne
            selected_cell = self.ListDiscogs.tableWidget.selected_cells.get(column)
            if selected_cell:
                row, _ = selected_cell
                # Obtenir l'objet QTableWidgetItem
                item = self.ListDiscogs.tableWidget.item(row, column)
                if item is not None:
                    # Obtenir le texte de la cellule et l'écrire dans le champ correspondant
                    cell_value = item.text()
                    if column != self.COL_ARTWORK_URL:
                        field.setText(cell_value)
                    else:
                        pixmap = create_pixmap_from_url(cell_value)
                        field.update_from_pixmap(pixmap)

class MainWindow(QDialog):
    def clickMethodOpenBrowser(self):
        # folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder', r'\\Freebox_server\DDext_4To\Musique')
        folderpath = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder', r'C:\0Martin\Musique\renomme music v2\musique_essai\ml7')
        self.groupeParcourir.zoneText.setText(folderpath)

    def clickMethodParcourir(self):
        path = self.groupeParcourir.zoneText.text()
        files_in_directory = os.listdir(path)
        for files in files_in_directory:
            if files[-3:] == 'mp3' or files[-3:] == 'MP3' or files[-4:] == 'flac' or files[-4:] == 'FLAC':
                if files[-3:] == 'mp3' or files[-3:] == 'MP3':
                    musique_file = Mp3File(files, path)
                if files[-3:] == 'flac' or files[-3:] == 'FLAC':
                    musique_file = FlacFile(files, path)
                musique_file.extract_tag()
                self.groupeListPistes.Pistes.append(musique_file)
                self.groupeListPistes.ListPistes.addItem(files)

    def clickMethodSearchAllsongInfo(self):
        from PyQt5.QtWidgets import QProgressBar
        # Initialisation de la barre de progression
        count = self.groupeListPistes.ListPistes.count()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(count)
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        for index in range(count):
            item = self.groupeListPistes.ListPistes.item(index)
            song_info = get_object_from_list(item, self.groupeListPistes.Pistes)
            song_info.get_tracks_info_from_web()

            # Mise à jour de la barre de progression
            self.progress_bar.setValue(index + 1)
            QApplication.processEvents()  # Permet de rafraîchir l'interface graphique

    def fill_groupeediteurTag_from_song_info(self, groupeediteurTag, song_info):
        groupeediteurTag.zoneTextFileName.setText(song_info.old_file_name)
        groupeediteurTag.zoneTextTitre.setText(song_info.Titre)
        groupeediteurTag.zoneTextArtistAsDisplay.setText(song_info.ArtisteDisplay)
        groupeediteurTag.zoneTextArtistFeaturing.setText(song_info.ArtisteFt)
        groupeediteurTag.zoneTextArtistRemix.setText(song_info.ArtisteRemix)
        groupeediteurTag.zoneTextArtistAll.setText(song_info.ArtisteAll)
        groupeediteurTag.zoneTextGenre.setText(song_info.Genre)
        groupeediteurTag.zoneTextStyle.setText(song_info.Style)
        groupeediteurTag.zoneTextAnnee.setText(str(song_info.Annee))
        groupeediteurTag.zoneTextAlbum.setText(song_info.Album)
        groupeediteurTag.zoneTextDisc.setText(str(song_info.Disk))
        groupeediteurTag.zoneTextNum.setText(str(song_info.Track))
        groupeediteurTag.zoneTextAlbumArtist.setText(song_info.ArtisteAlbum)

        groupeediteurTag.photoViewer.update_from_pixmap(song_info.Image)

    def clickMethodListePiste(self):

        if self.groupeListPistes.previousPiste is not None:
            # Sauvegarde de ce qui a été rempli dans l'editeur de tag
            song_info = get_object_from_list(self.groupeListPistes.previousPiste, self.groupeListPistes.Pistes)
            song_info.set_data_from_groupeediteurTag(self.groupeediteurTag)

        self.groupeListPistes.previousPiste = self.groupeListPistes.ListPistes.currentItem()

        #ecriture des infos du nouveau selectionne
        song_info = get_object_from_list(self.groupeListPistes.ListPistes.currentItem(), self.groupeListPistes.Pistes)
        self.fill_groupeediteurTag_from_song_info(self.groupeediteurTag, song_info)

    def clickMethodValider(self):
        if self.groupeListPistes.ListPistes.currentItem() is not None:
            song_info = get_object_from_list(self.groupeListPistes.ListPistes.currentItem(), self.groupeListPistes.Pistes)
            song_info.set_data_from_groupeediteurTag(self.groupeediteurTag)
        for index in range(self.groupeListPistes.ListPistes.count()):
            item = self.groupeListPistes.ListPistes.item(index)
            song_info = get_object_from_list(item, self.groupeListPistes.Pistes)
            song_info.saveTag()

    def clickMethodAutoAnalyse(self):
        chaine = self.groupeediteurTag.zoneTextFileName.text()
        song_info_from_extract = extraire_tag_from_filename(chaine)

        self.groupeediteurTag.zoneTextTitre.setText(song_info_from_extract["titre"])
        self.groupeediteurTag.zoneTextArtistAsDisplay.setText(song_info_from_extract["artiste"])
        self.groupeediteurTag.zoneTextArtistFeaturing.setText(song_info_from_extract["artisteFeat"])
        self.groupeediteurTag.zoneTextArtistAll.setText(song_info_from_extract["artisteAll"])

    def clickMethodRemplissageAllArtists(self):
        chaine = self.groupeediteurTag.zoneTextFileName.text()

    def open_new_window(self):
        # Créer et afficher la nouvelle fenêtre
        song_info = get_object_from_list(self.groupeListPistes.ListPistes.currentItem(), self.groupeListPistes.Pistes)
        self.discogs_window = DiscogsListWindow(self, song_info)
        self.discogs_window.show()

    def createParcourir(self):
        self.groupeParcourir = QGroupBox("Parcourir")

        boutonParcourir = QPushButton('browse', self)
        boutonParcourir.clicked.connect(self.clickMethodOpenBrowser)
        self.groupeParcourir.zoneText = QLineEdit(self)

        valider = QPushButton('OK', self)
        valider.clicked.connect(self.clickMethodParcourir)

        grid = QGridLayout()
        grid.addWidget(self.groupeParcourir.zoneText, 0, 0, 1, 4)
        grid.addWidget(boutonParcourir, 0, 4, 1, 1)
        grid.addWidget(valider, 1, 0, 1, 5)

        self.groupeParcourir.setLayout(grid)

    def createListePistes(self):
        self.groupeListPistes = QGroupBox("Liste des Pistes")
        self.groupeListPistes.Pistes = []
        self.groupeListPistes.previousPiste = None
        self.groupeListPistes.ListPistes = QListWidget(self)
        self.groupeListPistes.ListPistes.selectionModel().selectionChanged.connect(self.clickMethodListePiste)
        grid = QGridLayout()
        grid.addWidget(self.groupeListPistes.ListPistes, 0, 0)
        self.groupeListPistes.setLayout(grid)

    def create_groupe_action(self):
        self.groupeAction = QGroupBox("Action")

        #Bouton pour rechercher les information
        bouton_valider2 = QPushButton('Rech. Auto. tt Musique', self)
        bouton_valider2.clicked.connect(self.clickMethodSearchAllsongInfo)

        grid_groupe_action = QGridLayout()
        grid_groupe_action.addWidget(bouton_valider2, 0, 0)

        # Barre de progression
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)  # Affiche le pourcentage

        # Layout
        grid_groupe_action = QGridLayout()
        grid_groupe_action.addWidget(bouton_valider2, 0, 0)  # Bouton à gauche
        grid_groupe_action.addWidget(self.progress_bar, 0, 1)  # Barre à droite

        self.groupeAction.setLayout(grid_groupe_action)

    def createEditeurTag(self):
        self.groupeediteurTag = QGroupBox("Editeur ID3tag")

        labelFileName= QLabel("FileName")
        self.groupeediteurTag.zoneTextFileName = QLineEdit(self)
        labelTitre = QLabel("Titre")
        self.groupeediteurTag.zoneTextTitre = QLineEdit(self)
        labelArtistAsDisplay = QLabel("Artist As Display")
        self.groupeediteurTag.zoneTextArtistAsDisplay = QLineEdit(self)
        labelArtistFeaturing = QLabel("Artist Featuring")
        self.groupeediteurTag.zoneTextArtistFeaturing = QLineEdit(self)
        labelArtistRemix = QLabel("Artist Remix")
        self.groupeediteurTag.zoneTextArtistRemix = QLineEdit(self)
        labelArtistAll = QLabel("Artist All")
        self.groupeediteurTag.zoneTextArtistAll = QLineEdit(self)
        labelAlbumArtist = QLabel("Album Artist")
        self.groupeediteurTag.zoneTextAlbumArtist = QLineEdit(self)

        labelGenre = QLabel("Genre")
        self.groupeediteurTag.zoneTextGenre = QLineEdit(self)
        # Création du QCompleter avec la liste de mots
        completer = QCompleter(DISCOGS_GENRE)
        self.groupeediteurTag.zoneTextGenre.setCompleter(completer)

        labelStyle = QLabel("Style")
        self.groupeediteurTag.zoneTextStyle = QLineEdit(self)
        labelAnnee = QLabel("Annee")
        self.groupeediteurTag.zoneTextAnnee = QLineEdit(self)

        labelAlbum = QLabel("Album")
        self.groupeediteurTag.zoneTextAlbum = QLineEdit(self)
        labelDisc = QLabel("Disc")
        self.groupeediteurTag.zoneTextDisc = QLineEdit(self)
        labelNum = QLabel("#")
        self.groupeediteurTag.zoneTextNum = QLineEdit(self)

        self.groupeediteurTag.photoViewer = photoViewer()

        grid = QGridLayout()
        line = 0
        grid.addWidget(labelFileName, line, 0, 1, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextFileName, line, 1, 1, 5)
        line = line+1
        grid.addWidget(labelTitre, line, 0, 1, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextTitre, line, 1, 1, 5)
        line = line+1
        grid.addWidget(labelArtistAsDisplay, line, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextArtistAsDisplay, line, 1, 1, 5)
        line = line+1
        grid.addWidget(labelArtistFeaturing, line, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextArtistFeaturing, line, 1, 1, 5)
        line = line+1
        grid.addWidget(labelArtistRemix, line, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextArtistRemix, line, 1, 1, 5)
        line = line+1
        grid.addWidget(labelArtistAll, line, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextArtistAll, line, 1, 1, 5)
        line = line+1
        grid.addWidget(labelAlbumArtist, line, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextAlbumArtist, line, 1, 1, 5)
        line = line + 1
        grid.addWidget(labelAlbum, line, 0, 1, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextAlbum, line, 1, 1, 5)

        line = line + 1
        grid.addWidget(labelGenre, line, 0, 1, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextGenre, line, 1, 1, 1)
        grid.addWidget(labelStyle, line, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextStyle, line, 3, 1, 3)

        line = line + 1
        grid.addWidget(labelAnnee, line, 0)
        grid.addWidget(self.groupeediteurTag.zoneTextAnnee, line, 1)
        grid.addWidget(labelDisc, line, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextDisc, line, 3)
        grid.addWidget(labelNum, line, 4)
        grid.addWidget(self.groupeediteurTag.zoneTextNum, line, 5)
        line = line + 1

        grid.addWidget(self.groupeediteurTag.photoViewer.Image, 0, 6, 10, 1)
        grid.addWidget(self.groupeediteurTag.photoViewer.labelPictureInformation, 10, 6, 1, 1)

        line = line + 1
        #Bouton action
        actions = [
            ('Auto-analyse', "Extrait les informations à partir du titre", self.clickMethodAutoAnalyse),
            ('Internet BDD', "Remplissage à partir des BDD internet", self.open_new_window),
            ('All Artist', "Remplit le champ all artiste à partir des autres", self.clickMethodRemplissageAllArtists)
        ]

        for text, tooltip, callback in actions:
            bouton = QPushButton(text, self)
            bouton.clicked.connect(callback)
            label = QLabel(tooltip)
            grid.addWidget(bouton, line, 0)
            grid.addWidget(label, line, 1)
            line += 1


        grid.setColumnStretch(0, 4)
        grid.setColumnStretch(1, 6)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 6)
        grid.setColumnStretch(4, 1)
        grid.setColumnStretch(5, 2)
        grid.setColumnStretch(6, 10)



        self.groupeediteurTag.setLayout(grid)

    def createValider(self):
        self.groupeValider = QGroupBox("Valider")

        boutonValider = QPushButton('Valider', self)
        boutonValider.clicked.connect(self.clickMethodValider)

        grid = QGridLayout()
        grid.addWidget(boutonValider, 5, 4, 1, 1)


        self.groupeValider.setLayout(grid)


    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setMinimumSize(QSize(1350, 700))

        self.createParcourir()
        self.createListePistes()
        self.create_groupe_action()
        self.createEditeurTag()
        self.createValider()


        main_layout = QGridLayout()
        main_layout.addWidget(self.groupeParcourir, 0, 0, 1, 1)
        main_layout.addWidget(self.groupeListPistes, 1, 0, 4, 1)
        main_layout.addWidget(self.groupeAction, 0, 1, 1, 1)

        main_layout.addWidget(self.groupeediteurTag, 1, 1, 3, 1)
        main_layout.addWidget(self.groupeValider, 4, 1, 1, 1)

        main_layout.setColumnStretch(0, 1)
        main_layout.setColumnStretch(1, 4)

        self.setLayout(main_layout)




if __name__ == '__main__':
    app = QApplication([])#= ApplicationContext()
    gallery = MainWindow()
    gallery.show()
    app.exec_()