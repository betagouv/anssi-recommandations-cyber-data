import pandas as pd
from pathlib import Path
from argparse import ArgumentParser
from src.evalap.evalap_dataset_http import DatasetPayload, DatasetReponse
from src.evalap.evalap_experience_http import ExperiencePayload
from src.evalap import EvalapClient
from src.configuration import recupere_configuration, Configuration
import requests
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def ajoute_dataset(
    client: EvalapClient, nom: str, df_mapped: pd.DataFrame
) -> Optional[DatasetReponse]:
    payload = DatasetPayload(
        name=nom,
        readme="Jeu d'évaluation QA pour Evalap",
        default_metric="judge_precision",
        df=df_mapped.astype(object).where(pd.notnull(df_mapped), None).to_json(),
    )

    resultat = client.dataset.ajoute(payload)

    if resultat is None:
        logging.error("Le dataset n'a pas pu être ajouté")
        return None

    logging.info("Dataset ajouté")
    logging.info(f"Datasets disponibles: {len(client.dataset.liste())}")
    return resultat


def cree_experience(
    client: EvalapClient,
    dataset: DatasetReponse,
    df_mapped: pd.DataFrame,
    conf: Configuration,
):
    metriques = ["judge_precision"]

    payload_experience = ExperiencePayload(
        name="Experience Test",
        metrics=metriques,
        dataset=dataset.name,
        model={
            "output": df_mapped["output"].astype(str).tolist(),
            "aliased_name": "precomputed",
        },
        judge_model={
            "name": "albert-large",
            "base_url": conf.albert.url,
            "api_key": conf.albert.cle_api,
        },
    )

    resultat_experience = client.experience.cree(payload_experience)
    if resultat_experience:
        logging.info(
            f"Expérience créée: {resultat_experience.name} (ID: {resultat_experience.id})"
        )
    else:
        logging.error("L'expérience n'a pas pu être créée")


def main():
    p = ArgumentParser(description="Remplir 'Réponse Bot' depuis 'Question'")
    p.add_argument("--csv", required=True, type=Path, help="Chemin du CSV d'entrée")
    p.add_argument("--nom", required=True, type=str, help="Nom du dataset")
    args = p.parse_args()

    if not args.csv.exists():
        logging.error(f"Le fichier {args.csv} n'existe pas")
        return

    conf = recupere_configuration()
    df = pd.read_csv(args.csv)

    columns_map = {
        "Question type": "query",
        "Réponse Bot": "output",
        "Réponse envisagée": "output_true",
    }

    df_mapped = df.rename(columns=columns_map)
    session = requests.Session()
    client = EvalapClient(conf, session=session)

    dataset = ajoute_dataset(client, args.nom, df_mapped)
    if dataset is None:
        return

    cree_experience(client, dataset, df_mapped, conf)


if __name__ == "__main__":
    main()
