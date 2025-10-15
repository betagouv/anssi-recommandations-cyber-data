from pathlib import Path
from typing import Any, Iterator, Mapping, Callable, cast, Union
import pandas as pd
import logging


class LecteurCSV:
    def __init__(
        self, chemin: Path, separateur: str = ",", encodage: str = "utf-8"
    ) -> None:
        self._chemin = Path(chemin)
        self._df: pd.DataFrame = pd.read_csv(
            self._chemin, sep=separateur, encoding=encodage
        )

    def iterer_lignes(self) -> Iterator[Mapping[str, Any]]:
        lignes = cast(list[dict[str, Any]], self._df.to_dict(orient="records"))
        for ligne in lignes:
            yield ligne

    def _log_progression(self, index: int, total: int, nom_colonne: str) -> None:
        if index == 1:
            logging.info(
                f"Traitement de {total} lignes pour la colonne '{nom_colonne}'"
            )
        logging.info(f"Ligne {index}/{total} traitée")

    def appliquer_calcul_colonne(
        self,
        nom_colonne: str,
        calcul: Callable[[Mapping[str, Any]], Any],
    ) -> None:
        lignes = cast(list[dict[str, Any]], self._df.to_dict(orient="records"))
        total_lignes = len(lignes)

        resultats = []
        for i, ligne in enumerate(lignes, 1):
            resultats.append(calcul(ligne))
            self._log_progression(i, total_lignes, nom_colonne)

        self._df[nom_colonne] = resultats

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
