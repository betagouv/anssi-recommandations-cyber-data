from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class MetriqueBonNomDocument(BaseMetric):
    def __init__(self, nom_document_reponse: str, nom_document_verite_terrain: str):
        super().__init__()
        self.nom_document_reponse = nom_document_reponse
        self.nom_document_verite_terrain = nom_document_verite_terrain

    def measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        self.score = 0
        if (
            test_case.additional_metadata is not None
            and test_case.additional_metadata[self.nom_document_reponse]
            == test_case.additional_metadata[self.nom_document_verite_terrain]
        ):
            self.score = 1
        return self.score

    async def a_measure(self, test_case: LLMTestCase, *args, **kwargs) -> float:
        return self.measure(test_case)

    def is_successful(self) -> bool:
        return self.score == 1

    @property
    def __name__(self):
        return "Bon nom document"


class MetriquesBonNomDocuments:
    @staticmethod
    def cree_metriques() -> list[MetriqueBonNomDocument]:
        return [
            MetriqueBonNomDocument(
                f"nom_document_reponse_bot_{i}", f"nom_document_verite_terrain_{i}"
            )
            for i in range(5)
        ]
