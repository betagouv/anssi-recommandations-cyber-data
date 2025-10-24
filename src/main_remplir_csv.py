from pathlib import Path
from argparse import ArgumentParser
from configuration import recupere_configuration
from remplisseur_reponses import (
    ClientMQCHTTP,
    RemplisseurReponses,
    EcrivainSortie,
    HorlogeSysteme,
)
from lecteur_csv import LecteurCSV

import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> None:
    p = ArgumentParser(description="Remplir 'Réponse Bot' depuis 'Question'")
    p.add_argument("--csv", required=True, type=Path, help="Chemin du CSV d'entrée")
    p.add_argument(
        "--prefixe", default="evaluation", help="Préfixe du fichier de sortie"
    )
    p.add_argument("--sortie", default="donnees/sortie", help="Sous-dossier de sortie")
    args = p.parse_args()

    cfg = recupere_configuration().mqc
    client = ClientMQCHTTP(cfg=cfg)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = LecteurCSV(args.csv)

    ecrivain = EcrivainSortie(
        racine=Path.cwd(), sous_dossier=Path(args.sortie), horloge=HorlogeSysteme()
    )

    chemin = None
    try:
        while True:
            ligne_enrichie = remplisseur.remplit_ligne(lecteur)
            if chemin is None:
                chemin = ecrivain.ecrit_ligne_depuis_lecteur_csv(
                    ligne_enrichie, args.prefixe
                )
            else:
                ecrivain.ecrit_ligne_depuis_lecteur_csv(ligne_enrichie, args.prefixe)
            logging.info("Ligne traitée et écrite")
    except StopIteration:
        pass

    if chemin:
        logging.info(f"Nouveau fichier créé : {str(chemin)}")


if __name__ == "__main__":
    main()
