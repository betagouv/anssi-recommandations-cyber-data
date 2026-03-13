from typing import Optional, Union

import pytest
from deepeval.evaluate.types import EvaluationResult, TestResult
from deepeval.metrics import (
    BaseMetric,
)
from deepeval.test_case import LLMTestCase
from deepeval.tracing.api import MetricData

from evaluation.deepeval_adaptateur.lanceur_deepeval import EvaluateurDeepeval


class ConstructeurMetricData:
    @staticmethod
    def construis(nom: str, score: Union[float, int]) -> MetricData:
        return MetricData(
            name=nom,
            score=score,
            evaluationCost=0,
            success=True,
            threshold=0.5,
            strictMode=False,
            evaluationModel="gpt-4.1",
            verboseLogs=None,
        )


class EvaluateurDeepevalTest(EvaluateurDeepeval):
    cas_de_test_executes: list[LLMTestCase] = []
    metriques_deepeval_soumises: list[BaseMetric] = []
    metriques_personnalisees_soumises: list[BaseMetric] = []

    def __init__(self):
        super().__init__()
        self.metriques_personnalisees_soumises = []
        self.nombre_metriques_soumise = 0
        self.metriques_deepeval_soumises = []
        self.cas_de_test_executes = []

    def evaluate(
        self, test_cases: list[LLMTestCase], metrics: Optional[list[BaseMetric]] = None
    ) -> list[EvaluationResult]:
        self.cas_de_test_executes.extend(test_cases)
        if metrics is not None:
            self.metriques_deepeval_soumises.extend(metrics[0:3])
            self.metriques_personnalisees_soumises.extend(metrics[3:])
            self.nombre_metriques_soumise = len(self.metriques_deepeval_soumises) + len(
                self.metriques_personnalisees_soumises
            )

        metriques = self._construis_metriques_de_test()

        results = []
        for test_case in test_cases:
            results.append(
                TestResult(
                    metrics_data=metriques,
                    name="",
                    success=True,
                    conversational=False,
                    additional_metadata=test_case.additional_metadata,
                )
            )
        return [
            EvaluationResult(
                test_results=results, confident_link=None, test_run_id=None
            )
        ]

    def _construis_metriques_de_test(self) -> list[MetricData]:
        scores_par_nom = {
            "bon_nom_document_en_contexte_2": 1,
            "bon_numéro_page_en_contexte_2": 0,
            "score_numéro_page_en_contexte_2": 0.7,
            "hallucination": 0.6,
        }

        metriques = []

        for metrique in self.metriques_personnalisees_soumises:
            nom = metrique.__name__.lower().replace(" ", "_")
            score = scores_par_nom.get(nom, 1)
            metriques.append(
                ConstructeurMetricData.construis(nom=metrique.__name__, score=score)
            )

        for metrique in self.metriques_deepeval_soumises:
            nom = metrique.__name__.lower().replace(" ", "_")
            score = scores_par_nom.get(nom, 0.6)
            metriques.append(
                ConstructeurMetricData.construis(nom=metrique.__name__, score=score)
            )

        return metriques


@pytest.fixture
def evaluateur_de_test_avec_metriques() -> EvaluateurDeepevalTest:
    return EvaluateurDeepevalTest()
