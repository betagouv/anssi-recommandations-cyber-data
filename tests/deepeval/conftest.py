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
    metriques_soumises: list[BaseMetric] = []

    def __init__(self):
        super().__init__()
        self.metriques_soumises = []
        self.cas_de_test_executes = []

    def evaluate(
        self, test_cases: list[LLMTestCase], metrics: Optional[list[BaseMetric]] = None
    ) -> EvaluationResult:
        self.cas_de_test_executes.extend(test_cases)
        if metrics is not None:
            self.metriques_soumises.extend(metrics)
        metriques = [
            ConstructeurMetricData.construis(
                nom="bon_nom_document_en_contexte_2",
                score=1,
            ),
            ConstructeurMetricData.construis(
                nom="score_bon_nom_document_en_contexte_2",
                score=0.7,
            ),
            ConstructeurMetricData.construis(
                nom="hallucination",
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
