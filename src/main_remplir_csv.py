from pathlib import Path
from argparse import ArgumentParser
from configuration import recupere_configuration
from remplisseur_reponses import (
    ClientMQCHTTPAsync,
    RemplisseurReponses,
    EcrivainSortie,
    HorlogeSysteme,
)
from lecteur_csv import LecteurCSV
import logging
import asyncio

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


async def traite_csv_par_lots_paralleles(
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


def main() -> None:
    p = ArgumentParser(description="Remplir 'Réponse Bot' depuis 'Question'")
    p.add_argument("--csv", required=True, type=Path, help="Chemin du CSV d'entrée")
    p.add_argument(
        "--prefixe", default="evaluation", help="Préfixe du fichier de sortie"
    )
    p.add_argument("--sortie", default="donnees/sortie", help="Sous-dossier de sortie")
    p.add_argument(
        "--taille-lot",
        default=10,
        type=int,
        help="Taille du lot pour traitement parallèle",
    )
    args = p.parse_args()

    chemin = asyncio.run(
        traite_csv_par_lots_paralleles(
            csv_path=args.csv,
            prefixe=args.prefixe,
            sortie=Path(args.sortie),
            taille_lot=args.taille_lot,
        )
    )

    if chemin:
        logging.info(f"Nouveau fichier créé : {str(chemin)}")


if __name__ == "__main__":
    main()
