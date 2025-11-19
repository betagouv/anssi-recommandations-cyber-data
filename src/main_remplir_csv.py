from pathlib import Path
from argparse import ArgumentParser
from mqc.traite_csv_par_lots_en_parallele import traite_csv_par_lots_en_parallele
import logging
import asyncio

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

    chemin = asyncio.run(
        traite_csv_par_lots_en_parallele(
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
