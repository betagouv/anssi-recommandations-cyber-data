import ast
import pandas as pd
from pathlib import Path
from argparse import ArgumentParser
from evalap.evalap_dataset_http import DatasetPayload, DatasetReponse
from evalap.evalap_experience_http import ExperiencePayload
from evalap import EvalapClient
from configuration import recupere_configuration, Configuration
from metriques import Metriques
from formateur_resultats_experiences import FormateurResultatsExperiences
from remplisseur_reponses import EcrivainResultatsFlux
import requests
import logging
from typing import Optional
from formateur_resultats_experiences import GenerateurMetriques

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def applique_mapping_noms_documents(
    df: pd.DataFrame, chemin_mapping: Path
) -> pd.DataFrame:
    df_resultat = df.copy()
    df_mapping = pd.read_csv(chemin_mapping)

    def _extrait_cinq_premieres_valeurs(liste_noms: list[str]) -> pd.Series:
        resultats = {}
        for i in range(5):
            resultats[f"nom_document_reponse_bot_{i}"] = (
                liste_noms[i] if len(liste_noms) > i else ""
            )
        return pd.Series(resultats)

    def _convertit_liste_str_en_liste(valeur):
        # La valeur est de type str mais contient la représentation d'une liste
        # que l'on souhaite manipuler en tant que tel.
        return ast.literal_eval(valeur)

    def _traite_et_extrait_noms(valeur: str):
        liste_noms = _convertit_liste_str_en_liste(valeur)
        return _extrait_cinq_premieres_valeurs(liste_noms)

    nouvelles_colonnes = df_resultat["Noms Documents"].apply(_traite_et_extrait_noms)
    df_resultat = pd.concat([df_resultat, nouvelles_colonnes], axis=1)

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

    def _extrait_cinq_premiers_numeros_page(liste_pages: list) -> pd.Series:
        resultats = {}
        for i in range(5):
            resultats[f"numero_page_reponse_bot_{i}"] = (
                liste_pages[i] if len(liste_pages) > i else None
            )
        return pd.Series(resultats)

    def _traite_et_extrait_pages(valeur: str):
        liste_pages = _convertit_liste_str_en_liste(valeur)
        return _extrait_cinq_premiers_numeros_page(liste_pages)

    if "Numéros Page" not in df_resultat.columns:
        raise ValueError("La colonne 'Numéros Page' est requise")

    nouvelles_colonnes_pages = df_resultat["Numéros Page"].apply(
        _traite_et_extrait_pages
    )
    df_resultat = pd.concat([df_resultat, nouvelles_colonnes_pages], axis=1)

    if "Numéro page (lecteur)" not in df_resultat.columns:
        raise ValueError("La colonne 'Numéro page (lecteur)' est requise")

    df_resultat["numero_page_verite_terrain"] = df_resultat["Numéro page (lecteur)"]

    return df_resultat


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if "Contexte" in df.columns:
        df["Contexte"] = df["Contexte"].apply(
            lambda x: x.split("${SEPARATEUR_DOCUMENT}")
            if isinstance(x, str) and x.strip()
            else []
        )

    chemin_mapping = Path("donnees/jointure-nom-guide.csv")
    if "Noms Documents" in df.columns and "REF Guide" in df.columns:
        df = applique_mapping_noms_documents(df, chemin_mapping)
    else:
        raise ValueError("Les colonnes 'Noms Documents' et 'REF Guide' sont requises")

    for i in range(5):
        if f"numero_page_reponse_bot_{i}" in df.columns:
            df[f"numero_page_reponse_bot_{i}"] = df[
                f"numero_page_reponse_bot_{i}"
            ].fillna(0)

    if "numero_page_verite_terrain" in df.columns:
        df["numero_page_verite_terrain"] = df["numero_page_verite_terrain"].fillna(0)

    columns_map = {
        "Question type": "query",
        "Réponse Bot": "output",
        "Réponse envisagée": "output_true",
        "Contexte": "context",
    }

    return df.rename(columns=columns_map)


def sauvegarde_resultats(
    formateur_de_resultats: FormateurResultatsExperiences, experience_id: int
) -> None:
    dossier_sortie = Path("./donnees/resultats_evaluations")
    dossier_sortie.mkdir(parents=True, exist_ok=True)

    ecrivain = EcrivainResultatsFlux(dossier_sortie, "resultats_experience")
    generateur_resultats: GenerateurMetriques = (
        formateur_de_resultats.surveille_experience_flux(experience_id)
    )

    chemin_fichier = ecrivain.ecrit_resultats_flux(generateur_resultats, experience_id)
    logging.info(f"Résultats sauvegardés dans: {chemin_fichier}")


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

    metriques_enum = chargeur.recupere_depuis_fichier(fichier_metriques)
    metriques = [m.value for m in metriques_enum]

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
    logging.info(
        f"Token authentification configuré: {'Oui' if conf.evalap.token_authentification else 'Non'}"
    )
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
    sauvegarde_resultats(formateur_de_resultats, experience_id_cree)
    persiste_id_experience_dans_la_github_action(experience_id_cree)


def persiste_id_experience_dans_la_github_action(experience_id_cree: int) -> None:
    print(experience_id_cree)


if __name__ == "__main__":
    main()
