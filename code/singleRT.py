import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDateTime, Qt, QTimer, QSize
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
                             QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
                             QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy, QListWidget,
                             QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
                             QVBoxLayout, QWidget, QTableWidgetItem, QListWidgetItem, QCompleter)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QBuffer

import os
import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TRCK, TPOS, TCON,TDRC, TXXX, APIC

import re

#Discogs genre
DISCOGS_GENRE = ["", "Blues", "Brass & Military", "Children’s", "Classical", "Electronic", "Folk, World, & Country", "Funk / Soul", "Hip Hop", "Jazz", "Latin", "Non-Music", "Pop", "Reggae", "Rock", "Stage & Screen"]


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
        self.Images = []
        self.selectedIndices = []
        noneImage = ImageInList("None")
        self.Images.append(noneImage)

    def get_name_in_list(self):
        return self.old_file_name

    def extract_image(self):
        for tag in self.metadata.tags.values():
            if tag.FrameID == 'APIC':
                coverInSongFile = ImageInList("Cover in file")
                pixmap = QPixmap()
                pixmap.loadFromData(tag.data)
                coverInSongFile.set_pixmap(pixmap)
                self.Images.append(coverInSongFile)
                #pour qu'on selectionne de base cette image a la premiere ouverture
                self.selectedIndices.append(len(self.Images)-1)
                break

    def get_image_from_web(self):
        purged_name = self.old_file_name
        purged_name = purged_name.replace(purged_name[purged_name.find('myfreemp3'):purged_name.find('myfreemp3') + len('myfreemp3') + 4], '')
        purged_name = purged_name.replace('.mp3', '').replace('.flac', '')
        create_ImageInList_from_web(self.Images, purged_name, 10)
        create_ImageInList_from_web(self.Images, 'soundcloud' + purged_name, 4)
        create_ImageInList_from_web(self.Images, 'beatport' + purged_name, 4)

    def ImageViewer_save_selection(self, groupeImageViewer):
        self.selectedIndices = []
        for item in groupeImageViewer.ListImage.selectedIndexes():
            self.selectedIndices.append(item.row())

    def ImageViewer_restore_selection(self, groupeImageViewer):
        groupeImageViewer.ListImage.clearSelection()
        for index in self.selectedIndices:
            item = groupeImageViewer.ListImage.item(index)
            item.setSelected(True)
            # Mettre à jour explicitement currentItem
            groupeImageViewer.ListImage.setCurrentItem(item)

    def set_data_from_groupeediteurTag(self, groupeediteurTag, groupeImageViewer):
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

        self.ImageViewer_save_selection(groupeImageViewer)

        #selectedImage = get_object_from_list(groupeImageViewer.ListImage.currentItem(), self.Images)
        #if selectedImage is not None:
        #    pixmap = selectedImage.get_pixmap()
            #if pixmap is None:
                #self.groupeImageViewer.photoViewer.fill_with_blank()
                #self.groupeImageViewer.labelPictureInformation.setText("-")
            #else:
                #aspectRatioMode = Qt.KeepAspectRatio
                #pixmap_resized = pixmap.scaled(300, 300, aspectRatioMode)
                #self.groupeImageViewer.photoViewer.setPixmap(pixmap_resized)
                #self.groupeImageViewer.labelPictureInformation.setText(
                #    "" + str(pixmap.height()) + "x" + str(pixmap.width()))


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
        if self.selectedIndices:
            image_to_display = self.Images[self.selectedIndices[0]]

            if image_to_display is not None:
                if image_to_display.pixmap is not None:
                    image_mime = 'image/jpeg'
                    image_data = convert_qpixmap_to_bytes(image_to_display.pixmap, image_format=image_mime.split('/')[1].upper())
                    apic = APIC(
                        encoding=3,  # 3 = UTF-8
                        mime=image_mime,  # 'image/jpeg' ou 'image/png'
                        type=3,  # 3 = Cover (front)
                        desc=u'Cover',
                        data=image_data
                    )

                    audio.add(apic)

        audio.save()



def download_and_handle_image(url, i, images_list):
    from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
    from PyQt5.QtCore import QUrl, QEventLoop
    network_manager = QNetworkAccessManager()

    # Effectuer la requête pour télécharger l'image
    request = QNetworkRequest(QUrl(url))
    reply = network_manager.get(request)

    # Utiliser un QEventLoop pour attendre la fin du téléchargement
    loop = QEventLoop()
    reply.finished.connect(loop.quit)
    loop.exec_()

    if reply.error() == QNetworkReply.NoError:
        # Lire les données de l'image
        image_data = reply.readAll()

        # Créer un pixmap à partir des données de l'image
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)

        # Créer une instance de ImageInList
        image_from_web = ImageInList(str(url))
        image_from_web.set_pixmap(pixmap)

        # Ajouter l'image à la liste
        images_list.append(image_from_web)
    else:
        print("Erreur lors du téléchargement de l'image:", reply.errorString())

    # Fermer la réponse
    reply.deleteLater()


def download_and_handle_image_MARCHE_PAS(url, i, images_list):
    from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
    from PyQt5.QtCore import QUrl, QEventLoop
    network_manager = QNetworkAccessManager()

    # Effectuer la requête pour télécharger l'image
    request = QNetworkRequest(QUrl(url))
    reply = network_manager.get(request)

    def handle_image_download():
        nonlocal reply  # Utilisé pour rendre reply accessible à l'intérieur de la fonction locale

        if reply.error() == QNetworkReply.NoError:
            # Lire les données de l'image
            image_data = reply.readAll()

            # Créer un pixmap à partir des données de l'image
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)

            # Créer une instance de ImageInList
            image_from_web = ImageInList(str(i))
            image_from_web.set_pixmap(pixmap)

            # Ajouter l'image à la liste
            images_list.append(image_from_web)
        else:
            print("Erreur lors du téléchargement de l'image:", reply.errorString())

        # Fermer la réponse
        reply.deleteLater()

    # Connecter le signal de fin du téléchargement à la fonction de traitement de l'image
    reply.finished.connect(handle_image_download)

def create_ImageInList_from_web(Images, query, number_of_image):
    from qwant_search_image import qwant_get_image_urls
    try:
        urls = qwant_get_image_urls(query, number_of_image)
    except:
        return

    i = 0
    for url in urls:
        try:
            download_and_handle_image(url, i, Images)
            i = i + 1
        except:
            pass



def get_object_from_list(item, object_list):
    if item is not None:
        for Objects in object_list:
            if item.text() == Objects.get_name_in_list():
                return Objects

def set_Musique(item, object_list):
    if item is not None:
        for Objects in object_list:
            if item.text() == Objects.get_name_in_list():
                return Objects


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
                musique_file.extract_image()
                self.groupeListPistes.Pistes.append(musique_file)
                self.groupeListPistes.ListPistes.addItem(files)

    def clickMethodSearchOneSongImage(self):
        song_info = get_object_from_list(self.groupeListPistes.ListPistes.currentItem(), self.groupeListPistes.Pistes)
        song_info.get_image_from_web()
        self.fill_groupeImageViewer_from_song_info(self.groupeImageViewer, song_info)

    def clickMethodSearchAllImage(self):
        for index in range(self.groupeListPistes.ListPistes.count()):
            item = self.groupeListPistes.ListPistes.item(index)
            song_info = get_object_from_list(item, self.groupeListPistes.Pistes)
            song_info.get_image_from_web()

        song_info = get_object_from_list(self.groupeListPistes.ListPistes.currentItem(), self.groupeListPistes.Pistes)
        self.fill_groupeImageViewer_from_song_info(self.groupeImageViewer, song_info)

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
         # self.ArtisteAlbum = None

    def fill_groupeImageViewer_from_song_info(self, groupeImageViewer, song_info):
        groupeImageViewer.ListImage.clear()
        for ImageToAppendInThelist in song_info.Images:
            nametoplot = ImageToAppendInThelist.get_name_in_list()
            groupeImageViewer.ListImage.addItem(nametoplot)
        song_info.ImageViewer_restore_selection(groupeImageViewer)

    def clickMethodListePiste(self):

        if self.groupeListPistes.previousPiste is not None:
            # Sauvegarde de ce qui a été rempli dans l'editeur de tag
            song_info = get_object_from_list(self.groupeListPistes.previousPiste, self.groupeListPistes.Pistes)
            song_info.set_data_from_groupeediteurTag(self.groupeediteurTag, self.groupeImageViewer)

        self.groupeListPistes.previousPiste = self.groupeListPistes.ListPistes.currentItem()

        #ecriture des infos du nouveau selectionne
        song_info = get_object_from_list(self.groupeListPistes.ListPistes.currentItem(), self.groupeListPistes.Pistes)
        self.fill_groupeediteurTag_from_song_info(self.groupeediteurTag, song_info)
        self.fill_groupeImageViewer_from_song_info(self.groupeImageViewer, song_info)
        self.clickMethodListeImage()

    def clickMethodListeImage(self):
        song_info = get_object_from_list(self.groupeListPistes.ListPistes.currentItem(), self.groupeListPistes.Pistes)
        image_to_display = get_object_from_list(self.groupeImageViewer.ListImage.currentItem(), song_info.Images)
        if image_to_display is None:
            self.groupeImageViewer.photoViewer.fill_with_blank()
            self.groupeImageViewer.labelPictureInformation.setText("-")
        else:
            pixmap = image_to_display.get_pixmap()
            if pixmap is None:
                self.groupeImageViewer.photoViewer.fill_with_blank()
                self.groupeImageViewer.labelPictureInformation.setText("-")
            else:
                aspectRatioMode = Qt.KeepAspectRatio
                pixmap_resized = pixmap.scaled(300, 300, aspectRatioMode)
                self.groupeImageViewer.photoViewer.setPixmap(pixmap_resized)
                self.groupeImageViewer.labelPictureInformation.setText(
                    "" + str(pixmap.height()) + "x" + str(pixmap.width()))

    def clickMethodValider(self):
        if self.groupeListPistes.ListPistes.currentItem() is not None:
            song_info = get_object_from_list(self.groupeListPistes.ListPistes.currentItem(), self.groupeListPistes.Pistes)
            song_info.set_data_from_groupeediteurTag(self.groupeediteurTag, self.groupeImageViewer)
        for index in range(self.groupeListPistes.ListPistes.count()):
            item = self.groupeListPistes.ListPistes.item(index)
            song_info = get_object_from_list(item, self.groupeListPistes.Pistes)
            song_info.saveTag()

    def clickMethodAutoAnalyse(self):
        # Expression régulière pour trouver et enlever "myfreemp3.xxx" si ce n'est pas à la fin de la chaîne
        chaine = self.groupeediteurTag.zoneTextFileName.text()
        #traitement myfreemp3
        chaine = re.sub(r'\s*myfreemp3\.\w+\s*(?=\.\w+$)', '', chaine)
        # Enlever l'extension
        chaine = chaine.replace(".mp3", "").replace(".flac", "")
        # Enlever l'extension
        chaine = chaine.replace("feat.", "ft.").replace("Feat.", "ft.").replace("Ft.", "ft.").replace("Featuring", "ft.").replace("featuring", "ft.")
        # Assigner les parties aux variables artiste et titre
        parts = chaine.split(" - ", 1)
        if len(parts) == 2:
            artiste = parts[0].strip()  # Supprime les espaces avant/après
            titre = parts[1].strip()
        else:
            artiste = ""
            titre = chaine.strip()

        self.groupeediteurTag.zoneTextTitre.setText(titre)
        self.groupeediteurTag.zoneTextArtistAsDisplay.setText(artiste)

        parts = re.split(r'\s*feat.\s*|\s*ft.\s*|\s*Ft.\s*', artiste)
        if len(parts) == 2:
            artisteAll = parts[0].strip()  # Supprime les espaces avant/après
            artisteFeat = parts[1].strip()
        else:
            artisteAll = artiste.strip()
            artisteFeat = ""

        parts = re.split(r'\s*,\s*|\s*&\s*', artisteFeat)
        artistes_feat_nettoyes = [artiste.strip() for artiste in parts]
        # Enlever les doublons tout en conservant l'ordre avec un set
        vue = set()
        artistes_feat_nettoyes_sans_doublons = [x for x in artistes_feat_nettoyes if not (x in vue or vue.add(x))]

        artisteFeat = ";".join(artistes_feat_nettoyes_sans_doublons)

        parts = re.split(r'\s*,\s*|\s*&\s*', artisteAll)
        artistes_all_nettoyes = [artiste.strip() for artiste in parts]

        if artistes_feat_nettoyes[0] != "":
            artistes_all_nettoyes.extend(artistes_feat_nettoyes)
        # Enlever les doublons tout en conservant l'ordre avec un set
        vue = set()
        artistes_all_nettoyes_sans_doublons = [x for x in artistes_all_nettoyes if not (x in vue or vue.add(x))]

        artisteAll = ";".join(artistes_all_nettoyes_sans_doublons)


        self.groupeediteurTag.zoneTextArtistFeaturing.setText(artisteFeat)
        self.groupeediteurTag.zoneTextArtistAll.setText(artisteAll)

        #parts = chaine.split(" & ", 1)
        #self.Titre = groupeediteurTag.zoneTextTitre.text()
        #self.ArtisteRemix = groupeediteurTag.zoneTextArtistRemix.text()

        #self.Annee = groupeediteurTag.zoneTextAnnee.text()
        #self.Style = groupeediteurTag.zoneTextStyle.text()
        #self.Genre = groupeediteurTag.zoneTextGenre.text()
        #self.Disk = groupeediteurTag.zoneTextDisc.text()
        #self.Track = groupeediteurTag.zoneTextNum.text()
        #self.Album = groupeediteurTag.zoneTextAlbum.text()
        #self.ArtisteAlbum = groupeediteurTag.zoneTextAlbumArtist.text()


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

    def createImageViewer(self):
        # self.groupeediteurTag.createImageViewer()
        self.groupeImageViewer = QGroupBox("Cover")
        self.groupeImageViewer.Images = []
        self.groupeImageViewer.ListImage = QListWidget(self)
        self.groupeImageViewer.ListImage.selectionModel().selectionChanged.connect(self.clickMethodListeImage)
        self.groupeImageViewer.selectedIndices = []
        boutonValider = QPushButton('Image du web', self)
        boutonValider.clicked.connect(self.clickMethodSearchOneSongImage)
        boutonValider2 = QPushButton('toutes les musiques', self)
        boutonValider2.clicked.connect(self.clickMethodSearchAllImage)
        self.groupeImageViewer.photoViewer = ImageLabel()
        self.groupeImageViewer.labelPictureInformation = QLabel("-")
        self.groupeImageViewer.labelPictureInformation.setAlignment(Qt.AlignCenter)
        gridImageViewer = QGridLayout()
        gridImageViewer.addWidget(self.groupeImageViewer.ListImage, 0, 0, 10, 2)
        gridImageViewer.addWidget(boutonValider, 10, 0, 1, 1)
        gridImageViewer.addWidget(boutonValider2, 10, 1, 1, 1)
        gridImageViewer.addWidget(self.groupeImageViewer.photoViewer, 0, 2, 10, 3)
        gridImageViewer.addWidget(self.groupeImageViewer.labelPictureInformation, 10, 2, 1, 3)
        self.groupeImageViewer.setLayout(gridImageViewer)

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

        grid = QGridLayout()
        line = 1
        grid.addWidget(labelFileName, line, 0, 1, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextFileName, line, 2, 1, 9)
        line = line+1
        grid.addWidget(labelTitre, line, 0, 1, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextTitre, line, 2, 1, 9)
        line = line+1
        grid.addWidget(labelArtistAsDisplay, line, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextArtistAsDisplay, line, 2, 1, 9)
        line = line+1
        grid.addWidget(labelArtistFeaturing, line, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextArtistFeaturing, line, 2, 1, 9)
        line = line+1
        grid.addWidget(labelArtistRemix, line, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextArtistRemix, line, 2, 1, 9)
        line = line+1
        grid.addWidget(labelArtistAll, line, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextArtistAll, line, 2, 1, 9)
        line = line+1
        grid.addWidget(labelAlbumArtist, line, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextAlbumArtist, line, 2, 1, 9)
        line = line + 1
        grid.addWidget(labelAlbum, line, 0, 1, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextAlbum, line, 1, 1, 3)
        line = line + 1
        grid.addWidget(labelGenre, line, 0, 1, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextGenre, line, 1, 1, 3)
        grid.addWidget(labelStyle, line, 4)
        grid.addWidget(self.groupeediteurTag.zoneTextStyle, line, 5, 1, 5)
        line = line + 1
        grid.addWidget(labelAnnee, line, 0)
        grid.addWidget(self.groupeediteurTag.zoneTextAnnee, line, 1)
        grid.addWidget(labelDisc, line, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextDisc, line, 3)
        grid.addWidget(labelNum, line, 4)
        grid.addWidget(self.groupeediteurTag.zoneTextNum, line, 5)
        line = line + 1
        bouton_AutoAnalyse = QPushButton('Auto-analyse', self)
        bouton_AutoAnalyse.clicked.connect(self.clickMethodAutoAnalyse)
        grid.addWidget(bouton_AutoAnalyse, line, 0)

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

        self.setMinimumSize(QSize(1350, 900))

        self.createParcourir()
        self.createListePistes()
        self.createImageViewer()
        self.createEditeurTag()
        self.createValider()


        main_layout = QGridLayout()
        main_layout.addWidget(self.groupeParcourir, 0, 0, 1, 2)
        main_layout.addWidget(self.groupeListPistes, 1, 0, 6, 2)

        main_layout.addWidget(self.groupeImageViewer, 0, 2, 3, 5)
        main_layout.addWidget(self.groupeediteurTag, 3, 2, 3, 5)
        main_layout.addWidget(self.groupeValider, 6, 2, 1, 5)

        self.setLayout(main_layout)




if __name__ == '__main__':
    app = QApplication([])#= ApplicationContext()
    gallery = MainWindow()
    gallery.show()
    app.exec_()