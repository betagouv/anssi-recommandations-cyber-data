import logging
from pathlib import Path

from configuration import recupere_configuration
from lecteur_csv import LecteurCSV
from mqc.remplisseur_reponses import (
    ClientMQCHTTPAsync,
    RemplisseurReponses,
)
from mqc.ecrivain_sortie import HorlogeSysteme, EcrivainSortie


async def traite_csv_par_lots_en_parallele(
    csv_path: Path, prefixe: str, sortie: Path, taille_lot: int
) -> None:
    cfg = recupere_configuration().mqc
    client = ClientMQCHTTPAsync(cfg=cfg)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(csv_path)

    ecrivain = EcrivainSortie(
        racine=Path.cwd(), sous_dossier=sortie, horloge=HorlogeSysteme()
    )

    chemin = None
    try:
        while True:
            lignes_enrichies = await remplisseur.remplit_lot_lignes(lecteur, taille_lot)

            if not lignes_enrichies:
                raise StopIteration("Fin du fichier CSV atteinte")

            for ligne_enrichie in lignes_enrichies:
                if chemin is None:
                    chemin = ecrivain.ecrit_ligne_depuis_lecteur_csv(
                        ligne_enrichie, prefixe
                    )
                else:
                    ecrivain.ecrit_ligne_depuis_lecteur_csv(ligne_enrichie, prefixe)

            logging.info(f"Lot de {len(lignes_enrichies)} lignes traité et écrit")
    except StopIteration:
        pass
