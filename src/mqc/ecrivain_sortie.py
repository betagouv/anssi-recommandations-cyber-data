import csv
import datetime as dt
import re
from pathlib import Path
from typing import Union


class HorlogeSysteme:
    def aujourd_hui(self) -> str:
        return str(dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))


class EcrivainSortie:
    """Écrit un CSV horodaté dans un sous-dossier de sortie."""

    def __init__(
        self, racine: Path, sous_dossier: Path, horloge: HorlogeSysteme
    ) -> None:
        self._racine = racine
        self._sous_dossier = sous_dossier
        self._horloge: HorlogeSysteme = horloge if horloge else HorlogeSysteme()
        self._chemin_courant: Path | None = None

    @staticmethod
    def _desinfecte_prefixe(prefixe: str) -> str:
        return re.sub(r"[^A-Za-z0-9_-]", "_", prefixe)

    def _nom_fichier(self, prefixe: str) -> str:
        nettoye = self._desinfecte_prefixe(prefixe)
        return f"{nettoye}_{self._horloge.aujourd_hui()}.csv"

    def ecrit_ligne_depuis_lecteur_csv(
        self, ligne: dict[str, Union[str, int, float]], prefixe: str
    ) -> Path:
        if self._chemin_courant is None:
            dossier = self._racine / self._sous_dossier
            dossier.mkdir(parents=True, exist_ok=True)
            self._chemin_courant = (dossier / self._nom_fichier(prefixe)).resolve()
            if dossier not in self._chemin_courant.parents:
                raise ValueError("Chemin de sortie en dehors du dossier autorisé")

        if not self._chemin_courant.exists():
            with open(self._chemin_courant, "w", encoding="utf-8", newline="") as f:
                ecrivain = csv.writer(f)
                ecrivain.writerow(ligne.keys())

        with open(self._chemin_courant, "a", encoding="utf-8", newline="") as f:
            ecrivain = csv.writer(f)
            ecrivain.writerow(ligne.values())

        return self._chemin_courant
