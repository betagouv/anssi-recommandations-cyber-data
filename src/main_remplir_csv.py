import asyncio
from pathlib import Path
from argparse import ArgumentParser

from configuration import recupere_configuration
from mqc.collecte_reponses_mqc import collecte_reponses_mqc
import logging

from mqc.remplisseur_reponses import ClientMQCHTTPAsync

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


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

    configuration_mqc = recupere_configuration().mqc
    asyncio.run(
        collecte_reponses_mqc(
            args.csv,
            args.sortie,
            args.prefixe,
            args.taille_lot,
            ClientMQCHTTPAsync(configuration_mqc),
        )
    )


if __name__ == "__main__":
    main()
