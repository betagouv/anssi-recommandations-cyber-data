import unicodedata
import uuid
from itertools import chain
from pathlib import Path

import pandas as pd
from deepeval.evaluate.types import EvaluationResult, TestResult
from deepeval.metrics import (
    BaseMetric,
    HallucinationMetric,
    AnswerRelevancyMetric,
    ToxicityMetric,
)
from deepeval.test_case import LLMTestCase

from evaluation.evaluateur_deepeval import EvaluateurDeepeval
from evaluation.mqc.client_deepeval_albert import ClientDeepEvalAlbert
from evaluation.mqc.dataframe import prepare_dataframe
from evaluation.mqc.evaluation import LanceurEvaluation
from evaluation.mqc.metriques.metrique_bon_nom_document import MetriquesBonNomDocuments
from evaluation.mqc.metriques.metrique_bons_numeros_pages import (
    MetriquesBonsNumerosPages,
)
from evaluation.mqc.metriques.metrique_longueur_reponse import MetriqueLongueurReponse
from evaluation.mqc.metriques.metrique_score_numero_page import MetriquesScoreNumeropage
from infra.lecteur_csv import LecteurCSV
from journalisation.evaluation import EntrepotEvaluation, Evaluation


class LanceurEvaluationDeepeval(LanceurEvaluation):
    def __init__(
        self,
        entrepot_evaluation: EntrepotEvaluation,
        evaluateur_deepeval: EvaluateurDeepeval,
    ):
        super().__init__()
        self.client_deepeval_albert = ClientDeepEvalAlbert()
        self.entrepot_evaluation = entrepot_evaluation
        self.evaluateur_deepeval = evaluateur_deepeval

    def lance_l_evaluation(
        self, fichier_csv: Path, chemin_mapping: Path
    ) -> int | str | None:
        id_evaluation = str(uuid.uuid4())
        donnees = self.__charge_donnees_depuis_fichier_csv(fichier_csv, chemin_mapping)
        cas_de_test = self.__cree_liste_cas_de_test_deepeval(donnees)
        tous_les_resultats = self.__evalue_les_cas_de_test(cas_de_test)

        scores_deepeval = list(
            map(
                lambda score: self.__extrait_scores_deepeval(score),
                tous_les_resultats,
            )
        )
        self.entrepot_evaluation.persiste(Evaluation(id_evaluation, scores_deepeval))
        return id_evaluation

    @staticmethod
    def __cree_liste_cas_de_test_deepeval(
        donnees_dataframe: pd.DataFrame,
    ) -> list[LLMTestCase]:
        liste_cas_de_test = []
        for indice, ligne_donnees in donnees_dataframe.iterrows():
            contexte = ligne_donnees["context"]

            metadata = {"numero_ligne": indice}
            for col in ligne_donnees.index:
                if col.startswith(("nom_document_", "numero_page_")):
                    metadata[col] = ligne_donnees[col]

            cas_de_test_unique = LLMTestCase(
                input=ligne_donnees["query"],
                actual_output=ligne_donnees["output"],
                expected_output=ligne_donnees["output_true"],
                retrieval_context=contexte,
                context=contexte,
                additional_metadata=metadata,
            )
            liste_cas_de_test.append(cas_de_test_unique)

        return liste_cas_de_test

    def __charge_donnees_depuis_fichier_csv(
        self, chemin_vers_fichier: Path, chemin_mapping: Path
    ) -> pd.DataFrame:
        lecteur = LecteurCSV(chemin_vers_fichier)
        donnees_brutes = lecteur.dataframe
        donnees_preparees = prepare_dataframe(donnees_brutes, chemin_mapping)
        return donnees_preparees

    @staticmethod
    def __extrait_scores_deepeval(test_result: TestResult) -> dict:
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
            scores["numero_ligne"] = (
                test_result.additional_metadata["numero_ligne"]
                if test_result.additional_metadata is not None
                else 0
            )

        return scores

    def __evalue_les_cas_de_test(
        self, cas_de_test: list[LLMTestCase]
    ) -> list[TestResult]:
        metriques_deepeval: list[BaseMetric] = [
            HallucinationMetric(model=self.client_deepeval_albert, threshold=0.5),
            AnswerRelevancyMetric(model=self.client_deepeval_albert, threshold=0.5),
            ToxicityMetric(model=self.client_deepeval_albert, threshold=0.5),
            MetriqueLongueurReponse(),
        ]
        metriques_deepeval.extend(MetriquesBonNomDocuments.cree_metriques())
        metriques_deepeval.extend(MetriquesBonsNumerosPages.cree_metriques())
        metriques_deepeval.extend(MetriquesScoreNumeropage.cree_metriques())
        resultats_evaluations: list[EvaluationResult] = (
            self.evaluateur_deepeval.evaluate(cas_de_test, metrics=metriques_deepeval)
        )
        tous_les_resultats: list[TestResult] = list(
            chain.from_iterable(
                map(lambda resultats: resultats.test_results, resultats_evaluations)
            )
        )
        return tous_les_resultats
