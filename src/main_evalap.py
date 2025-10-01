import pandas as pd
from src.client_evalap import ClientEvalap, DatasetPayload
from src.configuration import recupere_configuration
import requests


def main():
    conf = recupere_configuration().evalap
    df = pd.read_csv("../donnees/QA-labelisé-Question_par_guide_echantillon.csv")

    columns_map = {
        "Question type": "query",
        "Réponse Bot": "output",
        "Réponse envisagée": "output_true",
    }

    df_mapped = df.rename(columns=columns_map)

    payload = DatasetPayload(
        name="QA-demo",
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
