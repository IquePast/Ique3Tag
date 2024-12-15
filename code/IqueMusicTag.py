class IqueMusicTag:
    def __init__(
        self,
        artiste=None,
        titre=None,
        artiste_display=None,
        artiste_remix=None,
        artiste_ft=None,
        artiste_all=None,
        annee=None,
        style=None,
        genre=None,
        disk=None,
        track=None,
        album=None,
        artiste_album=None,
        images_path=None,
    ):
        """
        Classe pour gérer les métadonnées des fichiers de musique.

        :param artiste: Nom de l'artiste principal.
        :param titre: Titre du morceau.
        :param artiste_display: Nom de l'artiste affiché.
        :param artiste_remix: Nom du remixeur.
        :param artiste_ft: Artiste(s) en featuring.
        :param artiste_all: Liste de tous les artistes impliqués.
        :param annee: Année de sortie.
        :param style: Style musical.
        :param genre: Genre musical.
        :param disk: Numéro du disque.
        :param track: Numéro de la piste.
        :param album: Nom de l'album.
        :param artiste_album: Artiste de l'album.
        :param images_path: Liste des chemins d'images associées.
        """
        self.artiste = artiste
        self.titre = titre
        self.artiste_display = artiste_display
        self.artiste_remix = artiste_remix
        self.artiste_ft = artiste_ft
        self.artiste_all = artiste_all
        self.annee = annee
        self.style = style
        self.genre = genre
        self.disk = disk
        self.track = track
        self.album = album
        self.artiste_album = artiste_album
        self.images_path = images_path

    def get(self, key):
        """
        Getter générique pour récupérer la valeur d'un attribut.
        :param key: Nom de l'attribut à récupérer.
        :return: La valeur de l'attribut ou None si l'attribut n'existe pas.
        """
        return getattr(self, key, None)