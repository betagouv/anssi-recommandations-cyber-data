from pathlib import Path

from configuration import recupere_configuration
from evaluation.mqc.remplisseur_reponses import ClientMQCHTTPAsync
from evaluation.mqc.traite_csv_par_lots_en_parallele import (
    traite_csv_par_lots_en_parallele,
)
from infra.ecrivain_sortie import EcrivainSortie
from infra.horloge import HorlogeSysteme


async def collecte_reponses_mqc(
    chemin_csv: Path,
    prefixe: str,
    ecrivain_sortie: EcrivainSortie,
    taille_lot: int,
    client: ClientMQCHTTPAsync,
) -> None:
    await traite_csv_par_lots_en_parallele(
        csv_path=chemin_csv,
        prefixe=prefixe,
        ecrivain_sortie=ecrivain_sortie,
        taille_lot=taille_lot,
        client=client,
    )

    return None


class CollecteurDeReponses:
    def __init__(
        self,
        ecrivain_sortie: EcrivainSortie,
        client: ClientMQCHTTPAsync,
        taille_lot: int,
    ):
        super().__init__()
        self._ecrivain_sortie = ecrivain_sortie
        self._client = client
        self._taille_lot = taille_lot
        self._prefixe = "collecte_reponses_mqc"

    async def collecte_reponses(self, chemin_csv: Path):
        return await collecte_reponses_mqc(
            chemin_csv,
            self._prefixe,
            self._ecrivain_sortie,
            self._taille_lot,
            self._client,
        )

    @property
    def fichier_de_reponses(self) -> Path:
        return self._ecrivain_sortie.fichier_de_reponses


def fabrique_collecteur_de_reponses():
    configuration = recupere_configuration()
    sortie = Path("/tmp/collecte_reponses")
    sortie.mkdir(parents=True, exist_ok=True)
    ecrivain_sortie = EcrivainSortie(
        racine=Path.cwd(), sous_dossier=sortie, horloge=HorlogeSysteme()
    )
    return CollecteurDeReponses(
        ecrivain_sortie,
        ClientMQCHTTPAsync(configuration.mqc),
        configuration.parametres_deepeval.taille_de_lot_collecte_mqc,
    )
