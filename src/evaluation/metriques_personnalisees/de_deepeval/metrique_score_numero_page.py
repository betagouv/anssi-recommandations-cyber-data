import numpy as np
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class MetriqueScoreNumeropage(BaseMetric):
    def __init__(self, numero_page_reponse_bot: str):
        super().__init__()
        self.numero_page_reponse_bot = numero_page_reponse_bot
        self.numero_page_verite_terrain = "numero_page_verite_terrain"
        self.threshold = 0.5

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        self.score = 0.6
        metadata = test_case.additional_metadata
        if metadata is not None:
            numero_page_reponse_bot, numero_page_verite_terrain = (
                self.__les_numeros_de_page(metadata)
            )
            if numero_page_reponse_bot == numero_page_verite_terrain:
                self.score = 1
            else:
                distance = abs(numero_page_reponse_bot - numero_page_verite_terrain)
                max_distance = 10
                distance_normalisee = min(distance / max_distance, 1.0)
                penalite = float(1 - np.exp(-1.5 * np.sqrt(distance_normalisee)))
                self.score = round(1.0 - penalite, 2)
        return self.score

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        return self.measure(test_case, *args, **kwargs)

    def is_successful(self) -> bool:
        return self.score == 1

    def __les_numeros_de_page(self, metadata: dict) -> tuple[int, int]:
        return int(metadata[self.numero_page_reponse_bot]), int(
            metadata[self.numero_page_verite_terrain]
        )

    @property
    def __name__(self):
        return f"Score numéro page en contexte {self.numero_page_reponse_bot[-1:]}"


class MetriquesScoreNumeropage:
    @staticmethod
    def cree_metriques() -> list[MetriqueScoreNumeropage]:
        return [
            MetriqueScoreNumeropage(f"numero_page_reponse_bot_{i}") for i in range(5)
        ]
