from pathlib import Path
from typing import Any, Dict, Iterator, Mapping, Callable, cast
import pandas as pd


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

    def appliquer_calcul_colonne(
        self,
        nom_colonne: str,
        calcul: Callable[[Mapping[str, Any]], Any],
    ) -> None:
        lignes = cast(list[dict[str, Any]], self._df.to_dict(orient="records"))
        self._df[nom_colonne] = [calcul(ligne) for ligne in lignes]

    def ecrire_vers(
        self, chemin_sortie: Path, separateur: str = ",", encodage: str = "utf-8"
    ) -> None:
        Path(chemin_sortie).parent.mkdir(parents=True, exist_ok=True)
        self._df.to_csv(chemin_sortie, index=False, sep=separateur, encoding=encodage)

    @property
    def dataframe(self) -> pd.DataFrame:
        return self._df.copy()
