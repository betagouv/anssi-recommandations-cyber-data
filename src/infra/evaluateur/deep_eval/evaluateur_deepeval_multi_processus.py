import multiprocessing as mp
from itertools import islice
from typing import Optional, Generator
from deepeval.evaluate import evaluate
from deepeval.evaluate.types import EvaluationResult
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

from evaluation.lanceur_deepeval import EvaluateurDeepeval


class EvaluateurDeepevalMultiProcessus(EvaluateurDeepeval):
    def __init__(self, nb_processus=1):
        self.nb_processus = nb_processus
        self.metrics = []

    def evaluate(
        self, test_cases: list[LLMTestCase], metrics: Optional[list[BaseMetric]] = None
    ) -> list[EvaluationResult]:
        self.metrics = metrics
        lots = self.divise_en_lots(test_cases)
        with mp.Pool(processes=self.nb_processus) as pool:
            resultats = pool.map(self.execute_evaluation, lots)

        return resultats

    def execute_evaluation(
        self, les_cas_de_test: list[LLMTestCase]
    ) -> EvaluationResult:
        return evaluate(les_cas_de_test, self.metrics)

    def divise_en_lots(self, cas_de_test: list[LLMTestCase]) -> list[list[LLMTestCase]]:
        return list(self.genere_chunk(cas_de_test))

    def genere_chunk(self, iterable: list[LLMTestCase]) -> Generator[list[LLMTestCase]]:
        it = iter(iterable)
        while True:
            chunk = list(islice(it, self.nb_processus))
            if not chunk:
                break
            yield chunk
