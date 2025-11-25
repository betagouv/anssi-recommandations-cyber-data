import logging
from pathlib import Path
from lecteur_csv import LecteurCSV
from mqc.ecrivain_sortie import EcrivainSortie
from mqc.remplisseur_reponses import (
    ClientMQCHTTPAsync,
    RemplisseurReponses,
)


async def traite_csv_par_lots_en_parallele(
    csv_path: Path,
    prefixe: str,
    ecrivain_sortie: EcrivainSortie,
    taille_lot: int,
    client: ClientMQCHTTPAsync,
) -> None:
    remplisseur = RemplisseurReponses(client)

    lecteur = LecteurCSV(csv_path)

    chemin = None
    try:
        while True:
            lignes_enrichies = await remplisseur.remplit_lot_lignes(lecteur, taille_lot)

            if not lignes_enrichies:
                raise StopIteration("Fin du fichier CSV atteinte")

            for ligne_enrichie in lignes_enrichies:
                if chemin is None:
                    chemin = ecrivain_sortie.ecrit_ligne_depuis_lecteur_csv(
                        ligne_enrichie, prefixe
                    )
                    logging.info(f"Nouveau fichier créé : {str(chemin)}")
                else:
                    ecrivain_sortie.ecrit_ligne_depuis_lecteur_csv(
                        ligne_enrichie, prefixe
                    )

            logging.info(f"Lot de {len(lignes_enrichies)} lignes traité et écrit")
    except StopIteration:
        pass
