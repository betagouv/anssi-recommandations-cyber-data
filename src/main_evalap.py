import ast
import pandas as pd
from pathlib import Path
from argparse import ArgumentParser
from src.evalap.evalap_dataset_http import DatasetPayload, DatasetReponse
from src.evalap.evalap_experience_http import ExperiencePayload
from src.evalap import EvalapClient
from src.configuration import recupere_configuration, Configuration
from src.metriques import Metriques
from src.formateur_resultats_experiences import FormateurResultatsExperiences
import requests
import logging
from datetime import datetime
from typing import Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def applique_mapping_noms_documents(
    df: pd.DataFrame, chemin_mapping: Path
) -> pd.DataFrame:
    df_resultat = df.copy()
    df_mapping = pd.read_csv(chemin_mapping)

    df_resultat["Noms Documents"] = df_resultat["Noms Documents"].apply(
        lambda x: ast.literal_eval(x) if isinstance(x, str) else x
    )

    df_resultat["nom_document_reponse_bot"] = df_resultat["Noms Documents"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else ""
    )

    def obtient_nom_depuis_ref(ref: str) -> str:
        if not isinstance(ref, str) or not ref.strip():
            return ""

        ligne_mapping = df_mapping[df_mapping["REF"] == ref]
        if not ligne_mapping.empty:
            url = ligne_mapping["URL"].iloc[0]
            return url.split("/")[-1]
        return ""

    df_resultat["nom_document_verite_terrain"] = df_resultat["REF Guide"].apply(
        obtient_nom_depuis_ref
    )
    return df_resultat


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if "Contexte" in df.columns:
        df["Contexte"] = df["Contexte"].apply(
            lambda x: x.split("${SEPARATEUR_DOCUMENT}")
            if isinstance(x, str) and x.strip()
            else []
        )

    chemin_mapping = Path("donnees/QA-labelisé-Mapping_Nom.csv")
    if "Noms Documents" in df.columns and "REF Guide" in df.columns:
        df = applique_mapping_noms_documents(df, chemin_mapping)
    else:
        raise ValueError("Les colonnes 'Noms Documents' et 'REF Guide' sont requises")

    columns_map = {
        "Question type": "query",
        "Réponse Bot": "output",
        "Réponse envisagée": "output_true",
        "Contexte": "context",
    }

    return df.rename(columns=columns_map)


def sauvegarde_resultats(
    formateur: FormateurResultatsExperiences, experience_terminee, experience_id: int
) -> None:
    if experience_terminee:
        df_resultats = formateur.cree_dataframe_formate(experience_terminee)
        logging.info(f"DataFrame créé avec {len(df_resultats)} lignes")
        logging.info(f"Colonnes: {list(df_resultats.columns)}")

        dossier_sortie = Path("./donnees/resultats_evaluations")
        dossier_sortie.mkdir(parents=True, exist_ok=True)

        horodatage = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nom_fichier = f"resultats_experience_{experience_id}_{horodatage}.csv"
        chemin_fichier = dossier_sortie / nom_fichier

        df_resultats.to_csv(chemin_fichier, index=False)
        logging.info(f"Résultats sauvegardés dans: {chemin_fichier}")
    else:
        logging.error("Impossible d'obtenir les résultats de l'expérience")


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
) -> int:
    chargeur = Metriques()
    fichier_metriques = Path("metriques.json")

    try:
        metriques_enum = chargeur.recupere_depuis_fichier(fichier_metriques)
        metriques = [m.value for m in metriques_enum]
    except (FileNotFoundError, ValueError) as e:
        logging.warning(
            f"Erreur chargement métriques: {e}. Utilisation de la métrique par défaut"
        )
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
    if resultat_experience is not None:
        return resultat_experience.id
    else:
        return -1


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
    df_mapped = prepare_dataframe(df)

    session = requests.Session()
    client = EvalapClient(conf, session=session)

    dataset = ajoute_dataset(client, args.nom, df_mapped)
    if dataset is None:
        return

    experience_id_cree = cree_experience(client, dataset, df_mapped, conf)
    experience_listee = client.experience.lit(experience_id_cree)
    logging.info(f"Expérience affichée: {experience_listee} ")

    formateur_de_resultats = FormateurResultatsExperiences(client.experience)
    experience_terminee = formateur_de_resultats.attend_fin_experience(
        experience_id_cree
    )

    sauvegarde_resultats(
        formateur_de_resultats, experience_terminee, experience_id_cree
    )


if __name__ == "__main__":
    main()
