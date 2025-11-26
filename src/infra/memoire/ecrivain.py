import csv
import uuid
from pathlib import Path
from typing import Union

from mqc.ecrivain_sortie import EcrivainSortie, HorlogeSysteme


class EcrivainSortieDeTest(EcrivainSortie):
    def __init__(
        self,
        contenu_fichier_csv_resultat_collecte: str,
        racine: Path = Path("/tmp"),
        sous_dossier: Path = Path(),
    ) -> None:
        self.contenu_fichier_csv_resultat_collecte = (
            contenu_fichier_csv_resultat_collecte
        )
        repertoire_destination = racine.joinpath(str(uuid.uuid4()))
        repertoire_destination.mkdir(parents=True, exist_ok=True)
        super().__init__(repertoire_destination, sous_dossier, HorlogeSysteme())

    def ecrit_ligne_depuis_lecteur_csv(
        self, ligne: dict[str, Union[str, int, float]], prefixe: str
    ) -> Path:
        dossier = self._racine / self._sous_dossier
        dossier.mkdir(parents=True, exist_ok=True)
        self._chemin_courant = (dossier / self._nom_fichier(prefixe)).resolve()

        lignes = self.contenu_fichier_csv_resultat_collecte.split("\n")
        en_tete = lignes[0].split(",")
        resultat_premiere_ligne = lignes[1].split(",")
        with open(self._chemin_courant, "a", encoding="utf-8", newline="") as f:
            ecrivain = csv.writer(f)
            ecrivain.writerow(en_tete)
            ecrivain.writerow(resultat_premiere_ligne)
        return Path()

    def ecris_contenu(self):
        dossier = self._racine / self._sous_dossier
        dossier.mkdir(parents=True, exist_ok=True)
        prefixe = str(uuid.uuid4())
        self._chemin_courant = (dossier / self._nom_fichier(prefixe)).resolve()

        lignes = self.contenu_fichier_csv_resultat_collecte.split("\n")
        with open(self._chemin_courant, "a", encoding="utf-8", newline="") as f:
            ecrivain = csv.writer(f)
            for ligne in lignes:
                ecrivain.writerow(ligne.split(","))
