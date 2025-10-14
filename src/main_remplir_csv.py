from pathlib import Path
from argparse import ArgumentParser
from .configuration import recupere_configuration
from .remplisseur_reponses import (
    ClientMQCHTTP,
    RemplisseurReponses,
    EcrivainSortie,
    HorlogeSysteme,
)

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

    generateur = remplisseur.remplit_fichier_flux(args.csv)
    ecrivain = EcrivainSortie(
        racine=Path.cwd(), sous_dossier=Path(args.sortie), horloge=HorlogeSysteme()
    )
    chemin = ecrivain.ecrit_fichier_depuis_generateur(generateur, prefixe=args.prefixe)
    logging.info(f"Nouveau fichier créé : {str(chemin)}")


if __name__ == "__main__":
    main()
