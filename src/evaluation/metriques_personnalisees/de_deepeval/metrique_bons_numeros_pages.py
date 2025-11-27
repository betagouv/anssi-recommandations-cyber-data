from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class MetriqueBonNumeroPage(BaseMetric):
    def __init__(self, numero_page_reponse_bot: str):
        super().__init__()
        self.numero_page_reponse_bot = numero_page_reponse_bot
        self.numero_page_verite_terrain = "numero_page_verite_terrain"
        self.threshold = 0.5

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        self.score = 0
        metadata: dict | None = test_case.additional_metadata
        la_reponse_du_bot_correspond_aux_numeros_de_pages_terrain = (
            metadata is not None
            and int(metadata[self.numero_page_reponse_bot])
            == int(metadata[self.numero_page_verite_terrain])
        )
        if la_reponse_du_bot_correspond_aux_numeros_de_pages_terrain:
            self.score = 1
        return self.score

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        return self.measure(test_case, *args, **kwargs)

    def is_successful(self) -> bool:
        return self.score == 1


class MetriquesBonsNumerosPages:
    @staticmethod
    def cree_metriques() -> list[MetriqueBonNumeroPage]:
        return [MetriqueBonNumeroPage(f"numero_page_reponse_bot_{i}") for i in range(5)]
