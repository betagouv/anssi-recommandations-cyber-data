import multiprocessing as mp
import sys
from itertools import islice
from typing import Optional, Generator
from deepeval.evaluate import evaluate, DisplayConfig
from deepeval.evaluate.types import EvaluationResult
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase

from evaluation.lanceur_deepeval import EvaluateurDeepeval


def configure_sorties_utf8():
    for flux in (sys.stdout, sys.stderr):
        reconfigure = getattr(flux, "reconfigure", None)
        if callable(reconfigure):
            reconfigure(encoding="utf-8", errors="replace")


class EvaluateurDeepevalMultiProcessus(EvaluateurDeepeval):
    def __init__(self, nb_processus=1):
        self.nb_processus = nb_processus
        self.metrics = []

    def evaluate(
        self, test_cases: list[LLMTestCase], metrics: Optional[list[BaseMetric]] = None
    ) -> list[EvaluationResult]:
        self.metrics = metrics
        lots = self.divise_en_lots(test_cases)
        with mp.Pool(
            processes=self.nb_processus, initializer=configure_sorties_utf8
        ) as pool:
            resultats = pool.map(self.execute_evaluation, lots)

        return resultats

    def execute_evaluation(
        self, les_cas_de_test: list[LLMTestCase]
    ) -> EvaluationResult:
        return evaluate(
            les_cas_de_test,
            self.metrics,
            display_config=DisplayConfig(
                print_results=False,
                show_indicator=False,
                verbose_mode=False,
            ),
        )

    def divise_en_lots(self, cas_de_test: list[LLMTestCase]) -> list[list[LLMTestCase]]:
        return list(self.genere_chunk(cas_de_test))

    def genere_chunk(self, iterable: list[LLMTestCase]) -> Generator[list[LLMTestCase]]:
        it = iter(iterable)
        while True:
            chunk = list(islice(it, self.nb_processus))
            if not chunk:
                break
            yield chunk
