import pytest
from typing import Optional, Union
from deepeval.evaluate.types import EvaluationResult, TestResult
from deepeval.metrics import (
    BaseMetric,
)
from deepeval.test_case import LLMTestCase
from deepeval.tracing.api import MetricData
from evaluation.lanceur_deepeval import EvaluateurDeepeval


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
    ) -> EvaluationResult:
        self.cas_de_test_executes.extend(test_cases)
        if metrics is not None:
            self.metriques_deepeval_soumises.extend(metrics[0:4])
            self.metriques_personnalisees_soumises.extend(metrics[4:])
            self.nombre_metriques_soumise = len(self.metriques_deepeval_soumises) + len(
                self.metriques_personnalisees_soumises
            )
        metrique_bon_document_en_contexte_2 = self.metriques_personnalisees_soumises[3]
        metrique_bon_numero_page_en_contexte_2 = self.metriques_personnalisees_soumises[
            8
        ]
        metrique_score_bon_document_en_contexte_2 = (
            self.metriques_personnalisees_soumises[13]
        )
        metrique_hallucination = self.metriques_deepeval_soumises[0]
        metriques = [
            ConstructeurMetricData.construis(
                nom=metrique_bon_document_en_contexte_2.__name__,
                score=1,
            ),
            ConstructeurMetricData.construis(
                nom=metrique_bon_numero_page_en_contexte_2.__name__,
                score=0,
            ),
            ConstructeurMetricData.construis(
                nom=metrique_score_bon_document_en_contexte_2.__name__,
                score=0.7,
            ),
            ConstructeurMetricData.construis(
                nom=metrique_hallucination.__name__,
                score=0.6,
            ),
        ]
        result = TestResult(
            metrics_data=metriques, name="", success=True, conversational=False
        )
        return EvaluationResult(
            test_results=[result], confident_link=None, test_run_id=None
        )


@pytest.fixture
def evaluateur_de_test() -> EvaluateurDeepevalTest:
    return EvaluateurDeepevalTest()
