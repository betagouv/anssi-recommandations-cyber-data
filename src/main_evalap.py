import logging
from argparse import ArgumentParser
from pathlib import Path
import requests
from configuration import recupere_configuration
from evalap import EvalapClient
from evalap.lance_experience import lance_experience

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def persiste_id_experience_dans_la_github_action(experience_id_cree: int) -> None:
    print(experience_id_cree)


def main():
    p = ArgumentParser(description="Remplir 'Réponse Bot' depuis 'Question'")
    p.add_argument("--csv", required=True, type=Path, help="Chemin du CSV d'entrée")
    p.add_argument("--nom", required=True, type=str, help="Nom du dataset")
    p.add_argument(
        "--delai-limite",
        type=int,
        default=300,
        help="Délai limite en secondes pour la vérification",
    )
    args = p.parse_args()
    nom = args.nom
    fichier_csv = args.csv
    limite = args.delai_limite

    if not fichier_csv.exists():
        logging.error(f"Le fichier {fichier_csv} n'existe pas")
        return

    conf = recupere_configuration()
    logging.info(
        f"Token authentification configuré: {'Oui' if conf.evalap.token_authentification else 'Non'}"
    )
    session = requests.Session()
    client = EvalapClient(conf, session=session)
    experience_id_cree = lance_experience(client, conf, limite, nom, fichier_csv)
    if experience_id_cree is None:
        return

    persiste_id_experience_dans_la_github_action(experience_id_cree)


if __name__ == "__main__":
    main()
