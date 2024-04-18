import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QDateTime, Qt, QTimer, QSize
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy, QListWidget,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QTableWidgetItem)
from PyQt5.QtGui import QPixmap

import os
import mutagen
from mutagen.id3 import ID3, TIT2, TPE1, TPE2, TALB, TRCK, TPOS, TCON,TDRC, TXXX, APIC

def extract_unitary(audio, string):
    try:
        return audio[string][0]
    except:
        return ''

def extractMP3(musiqueInfo):
    audio = ID3(musiqueInfo['old_file_name'])

    musiqueInfo['Titre'] = extract_unitary(audio, 'TIT2')
    musiqueInfo['Artiste'] = extract_unitary(audio, 'TPE1')
    musiqueInfo['ArtisteDisplay'] = musiqueInfo['Artiste']
    musiqueInfo['Artiste Album'] = extract_unitary(audio, 'TPE2')
    musiqueInfo['Album'] = extract_unitary(audio, 'TALB')
    musiqueInfo['Track'] = extract_unitary(audio, 'TRCK')
    musiqueInfo['Disk'] = extract_unitary(audio, 'TPOS')
    musiqueInfo['Genre'] = extract_unitary(audio, 'TCON')
    musiqueInfo['Annee'] = extract_unitary(audio, 'TDRC')
    # TODO faire les TXXX ??
    musiqueInfo['Style'] = ''
    musiqueInfo['ArtisteAll'] = ''
    musiqueInfo['ArtisteRemix'] = ''
    musiqueInfo['ArtisteFt'] = ''


def extractFLAC(musiqueInfo):
    from mutagen.flac import FLAC
    audio = FLAC(musiqueInfo['old_file_name'])

    musiqueInfo['Titre'] = extract_unitary(audio, 'title')

    musiqueInfo['Artiste'] = extract_unitary(audio, 'artist')
    musiqueInfo['ArtisteAll'] = extract_unitary(audio, 'artists (All)')
    musiqueInfo['ArtisteRemix'] = extract_unitary(audio, 'Artist Remix')
    musiqueInfo['ArtisteFt'] = extract_unitary(audio, 'artist ft')
    musiqueInfo['ArtisteDisplay'] = musiqueInfo['Artiste']

    musiqueInfo['Artiste Album'] = extract_unitary(audio, 'albumartist')
    musiqueInfo['Album'] = extract_unitary(audio, 'Album')
    musiqueInfo['Track'] = extract_unitary(audio, 'tracknumber')
    musiqueInfo['Disk'] = extract_unitary(audio, 'discnumber')
    musiqueInfo['Genre'] = extract_unitary(audio, 'genre')
    musiqueInfo['Style'] = extract_unitary(audio, 'style')
    musiqueInfo['Annee'] = extract_unitary(audio, 'date')

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
                break

    def get_image_from_web(self):
        create_ImageInList_from_web(self.Images, self.old_file_name, 10)


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
        # TODO faire les TXXX ??
        # musiqueInfo['Style'] = ''
        # musiqueInfo['ArtisteAll'] = ''
        # musiqueInfo['ArtisteRemix'] = ''
        # musiqueInfo['ArtisteFt'] = ''



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
        image_from_web = ImageInList(str(i))
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
    urls = qwant_get_image_urls(query, number_of_image)
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
                musique_file.get_image_from_web()
                self.groupeListPistes.Pistes.append(musique_file)
                self.groupeListPistes.ListPistes.addItem(files)

    def fill_groupeediteurTag_from_song_info(self, groupeediteurTag, song_info):
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

    def clickMethodListePiste(self):
        song_info = get_object_from_list(self.groupeListPistes.ListPistes.currentItem(), self.groupeListPistes.Pistes)
        self.fill_groupeediteurTag_from_song_info(self.groupeediteurTag, song_info)
        self.fill_groupeImageViewer_from_song_info(self.groupeImageViewer, song_info)
        self.clickMethodListeImage()

    def clickMethodListeImage(self):
        song_info = get_object_from_list(self.groupeListPistes.ListPistes.currentItem(), self.groupeListPistes.Pistes)
        ImageToAppendInThelist = get_object_from_list(self.groupeImageViewer.ListImage.currentItem(), song_info.Images)
        if ImageToAppendInThelist is None:
            self.groupeImageViewer.photoViewer.fill_with_blank()
            self.groupeImageViewer.labelPictureInformation.setText("-")
        else:
            pixmap = ImageToAppendInThelist.get_pixmap()
            if pixmap is None:
                self.groupeImageViewer.photoViewer.fill_with_blank()
                self.groupeImageViewer.labelPictureInformation.setText("-")
            else:
                aspectRatioMode = Qt.KeepAspectRatio
                pixmap_resized = pixmap.scaled(300, 300, aspectRatioMode)
                self.groupeImageViewer.photoViewer.setPixmap(pixmap_resized)
                self.groupeImageViewer.labelPictureInformation.setText(
                    "" + str(pixmap.height()) + "x" + str(pixmap.width()))

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
        self.groupeImageViewer.photoViewer = ImageLabel()
        self.groupeImageViewer.labelPictureInformation = QLabel("-")
        self.groupeImageViewer.labelPictureInformation.setAlignment(Qt.AlignCenter)

        gridImageViewer = QGridLayout()
        gridImageViewer.addWidget(self.groupeImageViewer.ListImage, 0, 0, 11, 2)
        gridImageViewer.addWidget(self.groupeImageViewer.photoViewer, 0, 2, 10, 3)
        gridImageViewer.addWidget(self.groupeImageViewer.labelPictureInformation, 10, 2, 1, 3)
        self.groupeImageViewer.setLayout(gridImageViewer)

    def createEditeurTag(self):
        self.groupeediteurTag = QGroupBox("Editeur ID3tag")

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
        grid.addWidget(labelTitre, 1, 0, 1, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextTitre, 1, 2, 1, 9)

        grid.addWidget(labelArtistAsDisplay, 2, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextArtistAsDisplay, 2, 2, 1, 9)
        grid.addWidget(labelArtistFeaturing, 3, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextArtistFeaturing, 3, 2, 1, 9)
        grid.addWidget(labelArtistRemix, 4, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextArtistRemix, 4, 2, 1, 9)
        grid.addWidget(labelArtistAll, 5, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextArtistAll, 5, 2, 1, 9)
        grid.addWidget(labelAlbumArtist, 6, 0, 1, 3)
        grid.addWidget(self.groupeediteurTag.zoneTextAlbumArtist, 6, 2, 1, 9)

        grid.addWidget(labelGenre, 8, 0, 1, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextGenre, 8, 1, 1, 3)
        grid.addWidget(labelStyle, 8, 4)
        grid.addWidget(self.groupeediteurTag.zoneTextStyle, 8, 5, 1, 5)

        grid.addWidget(labelAlbum, 7, 0, 1, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextAlbum, 7, 1, 1, 3)

        grid.addWidget(labelAnnee, 9, 0)
        grid.addWidget(self.groupeediteurTag.zoneTextAnnee, 9, 1)
        grid.addWidget(labelDisc, 9, 2)
        grid.addWidget(self.groupeediteurTag.zoneTextDisc, 9, 3)
        grid.addWidget(labelNum, 9, 4)
        grid.addWidget(self.groupeediteurTag.zoneTextNum, 9, 5)

        self.groupeediteurTag.setLayout(grid)


        grid = QGridLayout()


    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setMinimumSize(QSize(1350, 900))

        self.createParcourir()
        self.createListePistes()
        self.createImageViewer()
        self.createEditeurTag()


        main_layout = QGridLayout()
        main_layout.addWidget(self.groupeParcourir, 0, 0, 1, 2)
        main_layout.addWidget(self.groupeListPistes, 1, 0, 5, 2)

        main_layout.addWidget(self.groupeImageViewer, 0, 2, 3, 5)
        main_layout.addWidget(self.groupeediteurTag, 3, 2, 3, 5)


        self.setLayout(main_layout)




if __name__ == '__main__':
    app = QApplication([])#= ApplicationContext()
    gallery = MainWindow()
    gallery.show()
    app.exec_()