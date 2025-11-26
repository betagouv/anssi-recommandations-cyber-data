import pandas as pd
from pathlib import Path
from typing import List
import logging

from deepeval import evaluate
from deepeval.metrics import (
    HallucinationMetric,
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ToxicityMetric,
)
from deepeval.test_case import LLMTestCase
from deepeval.models import DeepEvalBaseLLM
from datetime import datetime
from configuration import recupere_configuration
from infra.lecteur_csv import LecteurCSV
from evalap.lance_experience import prepare_dataframe
from evalap.metriques import Metriques, MetriqueEnum
from metriques_personnalisees_evalap.metriques_personnalisees import (
    _metrique_bon_nom_document_en_contexte,
    _metrique_bon_numero_page_en_contexte,
    _metrique_score_numero_page_en_contexte,
)
import requests


class AlbertLLM(DeepEvalBaseLLM):
    def __init__(self):
        configuration = recupere_configuration()
        self.cle_api = configuration.albert.cle_api
        self.url_base = configuration.albert.url

    def load_model(self):
        return self

    def _appel_api_albert(self, prompt: str) -> str:
        en_tetes = {
            "Authorization": f"Bearer {self.cle_api}",
            "Content-Type": "application/json",
        }

        charge_utile = {
            "model": "albert-large",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800,
        }

        reponse = requests.post(
            f"{self.url_base}/chat/completions",
            headers=en_tetes,
            json=charge_utile,
            timeout=60,
        )

        if reponse.status_code == 200:
            return reponse.json()["choices"][0]["message"]["content"]

        raise RuntimeError(f"Erreur API Albert {reponse.status_code} : {reponse.text}")

    def generate(self, messages):
        """
        DeepEval peut passer :
        - une str
        - un dict {"role":..., "content":...}
        - une liste de messages [{"role":..., "content":...}]
        - un objet interne avec .input ou .prompt
        """

        # 1. case: DeepEval envoie une string
        if isinstance(messages, str):
            prompt = messages

        # 2. case: dict {"role": "...", "content": "..."}
        elif isinstance(messages, dict) and "content" in messages:
            prompt = messages["content"]

        # 3. case: liste de messages au format OpenAI
        elif isinstance(messages, list) and len(messages) > 0:
            last = messages[-1]
            if isinstance(last, dict) and "content" in last:
                prompt = last["content"]
            else:
                raise ValueError("Format de liste de messages invalide pour DeepEval")

        # 4. case: DeepEval TestCase objects
        elif hasattr(messages, "input"):
            prompt = messages.input

        elif hasattr(messages, "prompt"):
            prompt = messages.prompt

        else:
            raise ValueError(f"Format inattendu fourni par DeepEval: {type(messages)}")

        return self._appel_api_albert(prompt)

    async def a_generate(self, messages):
        return self.generate(messages)

    def get_model_name(self) -> str:
        return "albert-large"


def charge_donnees_depuis_fichier_csv(chemin_vers_fichier: str) -> pd.DataFrame:
    lecteur = LecteurCSV(Path(chemin_vers_fichier))
    donnees_brutes = lecteur.dataframe
    donnees_preparees = prepare_dataframe(donnees_brutes)
    return donnees_preparees


def nettoie_et_prepare_contexte_pour_evaluation(contexte_non_traite: str) -> str:
    if pd.isna(contexte_non_traite) or not isinstance(contexte_non_traite, str):
        return ""

    liste_documents = contexte_non_traite.split("${SEPARATEUR_DOCUMENT}")
    contexte_propre = "\n\n".join(
        [document.strip() for document in liste_documents if document.strip()]
    )

    return contexte_propre


def extrait_metadonnees_pour_metriques_personnalisees(ligne_donnees: pd.Series) -> dict:
    metadata = {}
    for j in range(5):
        if f"nom_document_reponse_bot_{j}" in ligne_donnees:
            metadata[f"nom_document_reponse_bot_{j}"] = ligne_donnees[
                f"nom_document_reponse_bot_{j}"
            ]
        if f"numero_page_reponse_bot_{j}" in ligne_donnees:
            metadata[f"numero_page_reponse_bot_{j}"] = ligne_donnees[
                f"numero_page_reponse_bot_{j}"
            ]

    if "nom_document_verite_terrain" in ligne_donnees:
        metadata["nom_document_verite_terrain"] = ligne_donnees[
            "nom_document_verite_terrain"
        ]
    if "numero_page_verite_terrain" in ligne_donnees:
        metadata["numero_page_verite_terrain"] = ligne_donnees[
            "numero_page_verite_terrain"
        ]

    return metadata


def cree_liste_cas_de_test_deepeval(
    donnees_dataframe: pd.DataFrame,
) -> List[LLMTestCase]:
    liste_cas_de_test = []

    for indice, ligne_donnees in donnees_dataframe.iterrows():
        contexte = ligne_donnees["context"]
        metadata = extrait_metadonnees_pour_metriques_personnalisees(ligne_donnees)

        cas_de_test_unique = LLMTestCase(
            input=ligne_donnees["query"],
            actual_output=ligne_donnees["output"],
            retrieval_context=contexte,
            context=contexte,
            additional_metadata=metadata,
        )
        liste_cas_de_test.append(cas_de_test_unique)

    logging.info(f"Créé {len(liste_cas_de_test)} cas de test")
    return liste_cas_de_test


def execute_evaluation_metriques(
    cas_de_test: List[LLMTestCase], albert_llm: AlbertLLM
) -> None:
    chargeur = Metriques()
    fichier_metriques = Path("metriques.json")
    metriques_enum = chargeur.recupere_depuis_fichier(fichier_metriques)

    metriques_deepeval: list = []
    for metrique_enum in metriques_enum:
        if metrique_enum == MetriqueEnum.HALLUCINATION:
            metriques_deepeval.append(
                HallucinationMetric(model=albert_llm, threshold=0.5)
            )
        elif metrique_enum == MetriqueEnum.ANSWER_RELEVANCY:
            metriques_deepeval.append(
                AnswerRelevancyMetric(model=albert_llm, threshold=0.5)
            )
        elif metrique_enum == MetriqueEnum.FAITHFULNESS:
            metriques_deepeval.append(
                FaithfulnessMetric(model=albert_llm, threshold=0.5)
            )
        elif metrique_enum == MetriqueEnum.TOXICITY:
            metriques_deepeval.append(ToxicityMetric(model=albert_llm, threshold=0.5))

    if not metriques_deepeval:
        logging.warning("Aucune métrique DeepEval supportée trouvée")
        return

    logging.info(f"Début de l'évaluation avec {len(metriques_deepeval)} métriques...")

    resultats = evaluate(
        test_cases=cas_de_test,
        metrics=metriques_deepeval,
    )

    if hasattr(resultats, "test_results"):
        tests_resultats = resultats.test_results
    elif isinstance(resultats, tuple) and len(resultats) > 0:
        tests_resultats = resultats[0]
    else:
        tests_resultats = resultats

    donnees_export: list[dict] = []

    for i, test_result in enumerate(tests_resultats):
        ligne_export: dict = {"numero_ligne": i}

        # Métriques DeepEval
        metrics_data = getattr(test_result, "metrics_data", None) or []
        for metric_data in metrics_data:
            nom_metrique = getattr(metric_data, "name", None)
            if not nom_metrique and hasattr(metric_data, "metric"):
                nom_metrique = getattr(
                    metric_data.metric,
                    "name",
                    metric_data.metric.__class__.__name__,
                )
            if not nom_metrique:
                nom_metrique = metric_data.__class__.__name__

            nom_colonne = (
                nom_metrique.replace("Metric", "").strip().lower().replace(" ", "_")
            )
            score = getattr(metric_data, "score", None)
            ligne_export[nom_colonne] = score

        # Métriques personnalisées
        cas_test = cas_de_test[i]
        if hasattr(cas_test, "additional_metadata") and cas_test.additional_metadata:
            metadata = cas_test.additional_metadata

            # Métriques de nom de document
            for j in range(5):
                nom_doc_bot = metadata.get(f"nom_document_reponse_bot_{j}", "")
                nom_doc_verite = metadata.get("nom_document_verite_terrain", "")
                ligne_export[f"bon_nom_document_en_contexte_{j}"] = (
                    _metrique_bon_nom_document_en_contexte(nom_doc_bot, nom_doc_verite)
                )

            # Métriques de numéro de page
            for j in range(5):
                num_page_bot = metadata.get(f"numero_page_reponse_bot_{j}", 0)
                num_page_verite = metadata.get("numero_page_verite_terrain", 0)

                ligne_export[f"bon_numero_page_en_contexte_{j}"] = (
                    _metrique_bon_numero_page_en_contexte(num_page_bot, num_page_verite)
                )
                ligne_export[f"score_numero_page_en_contexte_{j}"] = (
                    _metrique_score_numero_page_en_contexte(
                        num_page_bot, num_page_verite
                    )
                )

        donnees_export.append(ligne_export)

    df_resultats = pd.DataFrame(donnees_export)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nom_fichier = f"resultats_deepeval_metriques_{timestamp}.csv"
    chemin_sortie = Path("donnees/resultats_evaluations") / nom_fichier

    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
    df_resultats.to_csv(chemin_sortie, index=False)
    logging.info(f"📄 Résultats exportés vers: {chemin_sortie}")


def fonction_principale():
    configuration = recupere_configuration()

    chemin_fichier_donnees_csv = "/home/pleroy/PycharmProjects/anssi-recommandations-cyber-data/donnees/sortie/echantillon_01_evaluation_complete_2025.csv"

    if not Path(chemin_fichier_donnees_csv).exists():
        raise FileNotFoundError(f"Fichier non trouvé: {chemin_fichier_donnees_csv}")

    logging.info("=== POC DEEPEVAL - MÉTRIQUES MULTIPLES ===")
    logging.info(f"Fichier de données: {chemin_fichier_donnees_csv}")
    logging.info(f"API Albert: {configuration.albert.url}")

    modele_llm_albert = AlbertLLM()

    donnees_chargees = charge_donnees_depuis_fichier_csv(chemin_fichier_donnees_csv)
    liste_cas_de_test = cree_liste_cas_de_test_deepeval(donnees_chargees)
    logging.info(f"Nombre de cas de test réels : {len(liste_cas_de_test)}")

    if not liste_cas_de_test:
        logging.warning("Aucun cas de test valide trouvé")
        return

    execute_evaluation_metriques(liste_cas_de_test, modele_llm_albert)
    logging.info("=== POC TERMINÉ ===")


if __name__ == "__main__":
    fonction_principale()
