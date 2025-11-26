import pandas as pd
from pathlib import Path
from typing import List
import logging

from deepeval import evaluate
from deepeval.metrics import HallucinationMetric
from deepeval.test_case import LLMTestCase
from deepeval.models import DeepEvalBaseLLM
from datetime import datetime
from configuration import recupere_configuration
from infra.lecteur_csv import LecteurCSV
from evalap.lance_experience import prepare_dataframe


class AlbertLLM(DeepEvalBaseLLM):
    
    def __init__(self):
        configuration = recupere_configuration()
        self.cle_api = configuration.albert.cle_api
        self.url_base = configuration.albert.url
        
    def load_model(self):
        return self
        
    def generate(self, invite: str) -> str:
        import requests
        
        en_tetes = {
            "Authorization": f"Bearer {self.cle_api}",
            "Content-Type": "application/json"
        }
        
        charge_utile = {
            "model": "albert-large",
            "messages": [{"role": "user", "content": invite}],
            "max_tokens": 1000
        }
        
        reponse = requests.post(
            f"{self.url_base}/chat/completions",
            headers=en_tetes,
            json=charge_utile
        )
        
        if reponse.status_code == 200:
            return reponse.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Erreur API Albert: {reponse.status_code} - {reponse.text}")
    
    async def a_generate(self, invite: str) -> str:
        return self.generate(invite)
    
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
    contexte_propre = "\n\n".join([document.strip() for document in liste_documents if document.strip()])
    
    return contexte_propre


def cree_liste_cas_de_test_deepeval(donnees_dataframe: pd.DataFrame) -> List[LLMTestCase]:
    liste_cas_de_test = []
    
    for indice, ligne_donnees in donnees_dataframe.iterrows():
        contexte = ligne_donnees['context']
            
        cas_de_test_unique = LLMTestCase(
            input=ligne_donnees['query'],
            actual_output=ligne_donnees['output'],
            context=contexte
        )
        liste_cas_de_test.append(cas_de_test_unique)
    
    logging.info(f"Créé {len(liste_cas_de_test)} cas de test")
    return liste_cas_de_test


def execute_evaluation_hallucination(cas_de_test: List[LLMTestCase], albert_llm: AlbertLLM) -> None:
    metrique_hallucination = HallucinationMetric(
        model=albert_llm,
        threshold=0.5,
    )

    logging.info("Début de l'évaluation des hallucinations...")

    resultats = evaluate(
        test_cases=cas_de_test,
        metrics=[metrique_hallucination],
    )

    if hasattr(resultats, "test_results"):
        tests_resultats = resultats.test_results
    elif isinstance(resultats, tuple) and len(resultats) > 0:
        tests_resultats = resultats[0]
    else:
        tests_resultats = resultats

    donnees_export = []

    for i, test_result in enumerate(tests_resultats):
        score = None
        if getattr(test_result, "metrics_data", None):
            metric_data = test_result.metrics_data[0]
            score = getattr(metric_data, "score", None)

        donnees_export.append(
            {
                "numero_ligne": i,
                "hallucination": score,
            }
        )

    df_resultats = pd.DataFrame(donnees_export)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nom_fichier = f"resultats_deepeval_hallucination_{timestamp}.csv"
    chemin_sortie = Path("donnees/resultats_evaluations") / nom_fichier

    chemin_sortie.parent.mkdir(parents=True, exist_ok=True)

    df_resultats.to_csv(chemin_sortie, index=False)

    logging.info(f"📄 Résultats exportés vers: {chemin_sortie}")


def fonction_principale():
    configuration = recupere_configuration()
    
    chemin_fichier_donnees_csv = "/home/pleroy/PycharmProjects/anssi-recommandations-cyber-data/donnees/sortie/echantillon_01_evaluation_complete_2025.csv"
    
    if not Path(chemin_fichier_donnees_csv).exists():
        raise FileNotFoundError(f"Fichier non trouvé: {chemin_fichier_donnees_csv}")
    
    logging.info("=== POC DEEPEVAL - MÉTRIQUE HALLUCINATION ===")
    logging.info(f"Fichier de données: {chemin_fichier_donnees_csv}")
    logging.info(f"API Albert: {configuration.albert.url}")
    
    modele_llm_albert = AlbertLLM()
    
    donnees_chargees = charge_donnees_depuis_fichier_csv(chemin_fichier_donnees_csv)
    liste_cas_de_test = cree_liste_cas_de_test_deepeval(donnees_chargees)
    logging.info(f"Nombre de cas de test réels : {len(liste_cas_de_test)}")

    if not liste_cas_de_test:
        logging.warning("Aucun cas de test valide trouvé")
        return
    
    execute_evaluation_hallucination(liste_cas_de_test, modele_llm_albert)
    logging.info("=== POC TERMINÉ ===")


if __name__ == "__main__":
    fonction_principale()