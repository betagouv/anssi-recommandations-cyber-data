from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class MetriqueLongueurReponse(BaseMetric):
    def __init__(self):
        super().__init__()
        self.threshold = 0.5

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        self.score = 0
        if test_case.actual_output is not None:
            self.score = len(test_case.actual_output)
        return self.score

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.score is not None and self.score > 0

    @property
    def __name__(self):
        return "Longueur Réponse"
