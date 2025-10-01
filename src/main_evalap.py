import pandas as pd
from pathlib import Path
from argparse import ArgumentParser
from src.client_evalap import ClientEvalap, DatasetPayload
from src.configuration import recupere_configuration
import requests


def main():
    p = ArgumentParser(description="Remplir 'Réponse Bot' depuis 'Question'")
    p.add_argument("--csv", required=True, type=Path, help="Chemin du CSV d'entrée")
    p.add_argument("--nom", required=True, type=str, help="Nom du dataset")
    args = p.parse_args()

    conf = recupere_configuration().evalap
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
    client = ClientEvalap(conf, session=session)
    _ = client.ajoute_dataset(payload)

    print("Dataset ajouté :")
    print(client.liste_datasets())


if __name__ == "__main__":
    main()
