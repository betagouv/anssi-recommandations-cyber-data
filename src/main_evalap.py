import pandas as pd
from pathlib import Path
from argparse import ArgumentParser
from src.evalap.evalap_dataset_http import DatasetPayload
from src.configuration import Evalap
from src.evalap import EvalapClient
from src.configuration import recupere_configuration
import requests


def main():
    p = ArgumentParser(description="Remplir 'Réponse Bot' depuis 'Question'")
    p.add_argument("--csv", required=True, type=Path, help="Chemin du CSV d'entrée")
    p.add_argument("--nom", required=True, type=str, help="Nom du dataset")
    args = p.parse_args()

    conf = recupere_configuration()
    df = pd.read_csv(args.csv)

    columns_map = {
        "Question type": "query",
        "Réponse Bot": "output",
        "Réponse envisagée": "output_true",
    }

    df_mapped = df.rename(columns=columns_map)

    payload = DatasetPayload(
        name=args.nom,
        readme="Jeu d'évaluation QA pour Evalap",
        default_metric="judge_precision",
        df=df_mapped.astype(object).where(pd.notnull(df_mapped), None).to_json(),
    )
    session = requests.Session()

    client = EvalapClient(conf, session=session)
    _resultat = client.dataset.ajoute(payload)

    print("Dataset ajouté :")
    print(client.dataset.liste())


if __name__ == "__main__":
    main()
