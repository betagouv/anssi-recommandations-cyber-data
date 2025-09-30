from pathlib import Path
from argparse import ArgumentParser
from .configuration import recupere_configuration
from .remplisseur_reponses import (
    ClientMQCHTTP,
    RemplisseurReponses,
    EcrivainSortie,
    HorlogeSysteme,
)


def main() -> None:
    p = ArgumentParser(description="Remplir 'Réponse Bot' depuis 'Question'")
    p.add_argument("--csv", required=True, type=Path, help="Chemin du CSV d'entrée")
    p.add_argument(
        "--prefixe", default="evaluation", help="Préfixe du fichier de sortie"
    )
    p.add_argument("--sortie", default="donnees/sortie", help="Sous-dossier de sortie")
    args = p.parse_args()

    cfg = recupere_configuration()
    client = ClientMQCHTTP(cfg=cfg)
    remplisseur = RemplisseurReponses(client=client)

    lecteur = remplisseur.remplit_fichier(args.csv)
    ecrivain = EcrivainSortie(
        racine=Path.cwd(), sous_dossier=Path(args.sortie), horloge=HorlogeSysteme()
    )
    chemin = ecrivain.ecrit_fichier_depuis_lecteur_csv(lecteur, prefixe=args.prefixe)
    print(f"Nouveau fichier créé : {str(chemin)}")


if __name__ == "__main__":
    main()
