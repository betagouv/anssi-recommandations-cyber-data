import unicodedata
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import pandas as pd
from deepeval.evaluate.types import EvaluationResult
from deepeval.metrics import (
    BaseMetric,
    HallucinationMetric,
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ToxicityMetric,
)
from deepeval.test_case import LLMTestCase

from evalap.lance_experience import prepare_dataframe
from evaluation.client_deepeval_albert import ClientDeepEvalAlbert
from evaluation.metriques_personnalisees.de_deepeval.metrique_bon_nom_document import (
    MetriquesBonNomDocuments,
)
from evaluation.metriques_personnalisees.de_deepeval.metrique_bons_numeros_pages import (
    MetriquesBonsNumerosPages,
)
from evaluation.metriques_personnalisees.de_deepeval.metrique_longueur_reponse import (
    MetriqueLongueurReponse,
)
from evaluation.metriques_personnalisees.de_deepeval.metrique_score_numero_page import (
    MetriquesScoreNumeropage,
)
from experience.experience import LanceurExperience
from infra.lecteur_csv import LecteurCSV
from journalisation.experience import EntrepotExperience, Experience


class EvaluateurDeepeval(ABC):
    @abstractmethod
    def evaluate(
        self, test_cases: list[LLMTestCase], metrics: Optional[list[BaseMetric]] = None
    ) -> EvaluationResult:
        pass


class LanceurExperienceDeepeval(LanceurExperience):
    def __init__(
        self,
        entrepot_experience: EntrepotExperience,
        evaluateur_deepeval: EvaluateurDeepeval,
    ):
        super().__init__()
        self.client_deepeval_albert = ClientDeepEvalAlbert()
        self.entrepot_experience = entrepot_experience
        self.evaluateur_deepeval = evaluateur_deepeval

    @staticmethod
    def __cree_liste_cas_de_test_deepeval(
        donnees_dataframe: pd.DataFrame,
    ) -> list[LLMTestCase]:
        liste_cas_de_test = []
        for indice, ligne_donnees in donnees_dataframe.iterrows():
            contexte = ligne_donnees["context"]

            cas_de_test_unique = LLMTestCase(
                input=ligne_donnees["query"],
                actual_output=ligne_donnees["output"],
                expected_output=ligne_donnees["output_true"],
                retrieval_context=contexte,
                context=contexte,
                additional_metadata={},
            )
            liste_cas_de_test.append(cas_de_test_unique)

        return liste_cas_de_test

    @staticmethod
    def __charge_donnees_depuis_fichier_csv(chemin_vers_fichier: Path) -> pd.DataFrame:
        lecteur = LecteurCSV(chemin_vers_fichier)
        donnees_brutes = lecteur.dataframe
        donnees_preparees = prepare_dataframe(donnees_brutes)
        return donnees_preparees

    @staticmethod
    def __extrait_scores_deepeval(test_result) -> dict:
        scores = {}
        metrics_data = getattr(test_result, "metrics_data", None) or []

        def nom_colonne_normalisee():
            return (
                unicodedata.normalize(
                    "NFKD",
                    nom_metrique.replace("Metric", "")
                    .strip()
                    .lower()
                    .replace(" ", "_"),
                )
                .encode("ASCII", "ignore")
                .decode("utf-8", "ignore")
            )

        for metric_data in metrics_data:
            nom_metrique = getattr(metric_data, "name", None)
            if not nom_metrique and hasattr(metric_data, "metric"):
                nom_metrique = getattr(
                    metric_data.metric, "name", metric_data.metric.__class__.__name__
                )
            if not nom_metrique:
                nom_metrique = metric_data.__class__.__name__

            score = getattr(metric_data, "score", None)
            scores[nom_colonne_normalisee()] = score

        return scores

    def lance_l_experience(self, fichier_csv: Path) -> int | str | None:
        id_experience = str(uuid.uuid4())
        donnees = self.__charge_donnees_depuis_fichier_csv(fichier_csv)

        metriques_deepeval: list[BaseMetric] = [
            HallucinationMetric(model=self.client_deepeval_albert, threshold=0.5),
            AnswerRelevancyMetric(model=self.client_deepeval_albert, threshold=0.5),
            FaithfulnessMetric(
                model=self.client_deepeval_albert,
                threshold=0.5,
                truths_extraction_limit=20,
            ),
            ToxicityMetric(model=self.client_deepeval_albert, threshold=0.5),
            MetriqueLongueurReponse(),
        ]
        metriques_deepeval.extend(MetriquesBonNomDocuments.cree_metriques())
        metriques_deepeval.extend(MetriquesBonsNumerosPages.cree_metriques())
        metriques_deepeval.extend(MetriquesScoreNumeropage.cree_metriques())

        cas_de_test = self.__cree_liste_cas_de_test_deepeval(donnees)
        resultat_evaluation = self.evaluateur_deepeval.evaluate(
            cas_de_test, metrics=metriques_deepeval
        )
        scores_deepeval = self.__extrait_scores_deepeval(
            resultat_evaluation.test_results[0]
        )
        self.entrepot_experience.persiste(Experience(id_experience, [scores_deepeval]))
        return id_experience
