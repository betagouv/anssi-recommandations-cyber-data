from abc import ABC, abstractmethod
from typing import Optional

from deepeval.evaluate.types import EvaluationResult
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class EvaluateurDeepeval(ABC):
    @abstractmethod
    def evaluate(
        self, test_cases: list[LLMTestCase], metrics: Optional[list[BaseMetric]] = None
    ) -> list[EvaluationResult]:
        pass
