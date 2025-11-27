import argparse
import logging
import multiprocessing as mp
import os
import time
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
import requests
from deepeval.evaluate import evaluate
from deepeval.metrics import (
    HallucinationMetric,
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ToxicityMetric,
    BaseMetric,
)
from deepeval.models import DeepEvalBaseLLM
from deepeval.test_case import LLMTestCase

from configuration import recupere_configuration
from evalap.lance_experience import prepare_dataframe
from evalap.metriques import Metriques, MetriqueEnum
from infra.lecteur_csv import LecteurCSV
from metriques_personnalisees_evalap.metriques_personnalisees import (
    _metrique_bon_nom_document_en_contexte,
    _metrique_bon_numero_page_en_contexte,
    _metrique_score_numero_page_en_contexte,
)


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
        return self._appel_api_albert(messages)

    async def a_generate(self, messages):
        return self.generate(messages)

    def get_model_name(self) -> str:
        return "albert-large"


def charge_donnees_depuis_fichier_csv(chemin_vers_fichier: str) -> pd.DataFrame:
    lecteur = LecteurCSV(Path(chemin_vers_fichier))
    donnees_brutes = lecteur.dataframe
    donnees_preparees = prepare_dataframe(donnees_brutes)
    return donnees_preparees


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


def cree_metriques_deepeval(albert_llm: AlbertLLM) -> list:
    chargeur = Metriques()
    fichier_metriques = Path("metriques.json")
    metriques_enum = chargeur.recupere_depuis_fichier(fichier_metriques)

    metriques_deepeval: list[BaseMetric] = []
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

    return metriques_deepeval


def extrait_scores_deepeval(test_result) -> dict:
    scores = {}
    metrics_data = getattr(test_result, "metrics_data", None) or []
    for metric_data in metrics_data:
        nom_metrique = getattr(metric_data, "name", None)
        if not nom_metrique and hasattr(metric_data, "metric"):
            nom_metrique = getattr(
                metric_data.metric, "name", metric_data.metric.__class__.__name__
            )
        if not nom_metrique:
            nom_metrique = metric_data.__class__.__name__

        nom_colonne = (
            nom_metrique.replace("Metric", "").strip().lower().replace(" ", "_")
        )
        score = getattr(metric_data, "score", None)
        scores[nom_colonne] = score

    return scores


def calcule_metriques_personnalisees(metadata: dict) -> dict:
    scores = {}

    for j in range(5):
        nom_doc_bot = metadata.get(f"nom_document_reponse_bot_{j}", "")
        nom_doc_verite = metadata.get("nom_document_verite_terrain", "")
        scores[f"bon_nom_document_en_contexte_{j}"] = (
            _metrique_bon_nom_document_en_contexte(nom_doc_bot, nom_doc_verite)
        )

    for j in range(5):
        num_page_bot = metadata.get(f"numero_page_reponse_bot_{j}", 0)
        num_page_verite = metadata.get("numero_page_verite_terrain", 0)

        scores[f"bon_numero_page_en_contexte_{j}"] = (
            _metrique_bon_numero_page_en_contexte(num_page_bot, num_page_verite)
        )
        scores[f"score_numero_page_en_contexte_{j}"] = (
            _metrique_score_numero_page_en_contexte(num_page_bot, num_page_verite)
        )

    return scores


def exporte_resultats(donnees_export: list[dict]) -> None:
    df_resultats = pd.DataFrame(donnees_export)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nom_fichier = f"resultats_deepeval_metriques_{timestamp}.csv"
    chemin_sortie = Path("donnees/resultats_evaluations") / nom_fichier
    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)
    df_resultats.to_csv(chemin_sortie, index=False)
    logging.info(f"📄 Résultats exportés vers: {chemin_sortie}")


def divise_en_lots(
    cas_de_test: List[LLMTestCase], taille_lot: int
) -> List[List[LLMTestCase]]:
    return [
        cas_de_test[i : i + taille_lot] for i in range(0, len(cas_de_test), taille_lot)
    ]


def execute_evaluation_lot(args) -> list[dict]:
    lot_cas_test, numero_batch = args
    process_id = os.getpid()
    debut = time.time()

    logging.info(
        f"🚀 Processus {process_id} - Début évaluation lot {numero_batch} ({len(lot_cas_test)} cas)"
    )

    albert_llm = AlbertLLM()
    metriques_deepeval = cree_metriques_deepeval(albert_llm)

    resultats_lot = []

    for i, cas_test in enumerate(lot_cas_test):
        debut_cas = time.time()
        logging.info(
            f"⚙️ Processus {process_id} - Lot {numero_batch}, cas {i + 1}/{len(lot_cas_test)}"
        )

        try:
            resultat_test = evaluate([cas_test], metriques_deepeval)

            scores_deepeval = extrait_scores_deepeval(resultat_test.test_results[0])
            scores_personnalises = calcule_metriques_personnalisees(
                cas_test.additional_metadata
            )

            donnees_ligne = {
                **scores_deepeval,
                **scores_personnalises,
            }
            resultats_lot.append(donnees_ligne)

            duree_cas = time.time() - debut_cas
            logging.info(
                f"✅ Processus {process_id} - Lot {numero_batch}, cas {i + 1} terminé en {duree_cas:.2f}s"
            )

        except Exception as e:
            logging.error(
                f"❌ Processus {process_id} - Erreur lot {numero_batch}, cas {i + 1}: {e}"
            )
            continue

    duree_totale = time.time() - debut
    logging.info(
        f"🏁 Processus {process_id} - Lot {numero_batch} terminé en {duree_totale:.2f}s"
    )

    return resultats_lot


def execute_evaluations_paralleles(
    cas_de_test: List[LLMTestCase], nb_processus: int | None = None, taille_lot: int = 5
) -> list[dict]:
    if nb_processus is None:
        nb_processus = min(mp.cpu_count(), 4)

    logging.info(
        f"🔧 Configuration parallélisation: {nb_processus} processus, lots de {taille_lot} cas"
    )

    lots = divise_en_lots(cas_de_test, taille_lot)
    args_lots = [(lot, i) for i, lot in enumerate(lots)]

    logging.info(
        f"📊 Démarrage évaluation parallèle: {len(cas_de_test)} cas répartis en {len(lots)} lots"
    )

    debut_global = time.time()

    with mp.Pool(processes=nb_processus) as pool:
        resultats_lots = pool.map(execute_evaluation_lot, args_lots)

    duree_globale = time.time() - debut_global

    tous_resultats = []
    for resultats_lot in resultats_lots:
        tous_resultats.extend(resultats_lot)

    logging.info(
        f"🎉 Évaluation parallèle terminée en {duree_globale:.2f}s - {len(tous_resultats)} résultats"
    )

    return tous_resultats


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nb-processus", type=int, default=3)
    parser.add_argument("--taille-lot", type=int, default=2)
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    chemin_fichier = "donnees/sortie/echantillon_01_evaluation_complete_2025.csv"
    donnees = charge_donnees_depuis_fichier_csv(chemin_fichier)
    donnees_test = donnees.head(10)
    cas_de_test = cree_liste_cas_de_test_deepeval(donnees_test)

    resultats = execute_evaluations_paralleles(
        cas_de_test, nb_processus=args.nb_processus, taille_lot=args.taille_lot
    )

    exporte_resultats(resultats)


if __name__ == "__main__":
    main()
