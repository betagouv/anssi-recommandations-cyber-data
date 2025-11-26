import ast
from pathlib import Path
from typing import Any, Iterator, Mapping, Callable, cast, Union
import pandas as pd
import logging
from itertools import takewhile


class LecteurCSV:
    def __init__(
        self, chemin: Path, separateur: str = ",", encodage: str = "utf-8"
    ) -> None:
        self._chemin = Path(chemin)

        nb_lignes_header = self._detecte_lignes_header()

        self._df: pd.DataFrame = pd.read_csv(
            self._chemin, sep=separateur, encoding=encodage, skiprows=nb_lignes_header
        )
        self._iterateur: Iterator[Mapping[str, Any]] | None = None

    def _detecte_lignes_header(self) -> int:
        with open(self._chemin, "r", encoding="utf-8") as f:
            return sum(
                1 for _ in takewhile(lambda ligne: ligne.strip().startswith("#"), f)
            )

    def iterer_lignes(self) -> Iterator[Mapping[str, Any]]:
        lignes = cast(list[dict[str, Any]], self._df.to_dict(orient="records"))
        for ligne in lignes:
            yield ligne

    def ligne_suivante(self) -> Mapping[str, Any]:
        if self._iterateur is None:
            self._iterateur = self.iterer_lignes()
        return next(self._iterateur)

    def _log_progression(self, index: int, total: int, nom_colonne: str) -> None:
        if index == 1:
            logging.info(
                f"Traitement de {total} lignes pour la colonne '{nom_colonne}'"
            )
        logging.info(f"Ligne {index}/{total} traitée")

    def ecrire_vers(
        self, chemin_sortie: Path, separateur: str = ",", encodage: str = "utf-8"
    ) -> None:
        Path(chemin_sortie).parent.mkdir(parents=True, exist_ok=True)
        self._df.to_csv(chemin_sortie, index=False, sep=separateur, encoding=encodage)

    def appliquer_calcul_ligne(
        self,
        nom_colonne: str,
        calcul: Callable[[Mapping[str, Union[str, int, float]]], Any],
        ligne: Mapping[str, Union[str, int, float]],
    ) -> dict[str, Union[str, int, float]]:
        ligne_enrichie = dict(ligne)
        ligne_enrichie[nom_colonne] = calcul(ligne)
        return ligne_enrichie

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._df.copy()

    def recupere_les_informations_de_la_ligne(self, numero_ligne: int) -> dict:
        la_ligne = self._df.iloc[numero_ligne].to_dict()
        informations_de_la_ligne = {
            "question_type": la_ligne["Question type"],
            "reponse_envisagee": la_ligne["Réponse envisagée"],
            "reponse_bot": la_ligne["Réponse Bot"],
            "noms_documents": ast.literal_eval(la_ligne["Noms Documents"]),
            "numeros_page": ast.literal_eval(la_ligne["Numéros Page"]),
        }
        return informations_de_la_ligne
