from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class RequeteCreationDocumentAlbert:
    name: str
    metadata: dict[str, Any]


@dataclass
class ReponseCreationCollection:
    id: str


class ClientAlbertJeopardy(ABC):
    @abstractmethod
    def cree_collection(self) -> ReponseCreationCollection:
        pass

    @abstractmethod
    def ajoute_document(
        self, identifiant_collection: str, document: RequeteCreationDocumentAlbert
    ):
        pass

    @abstractmethod
    def genere_question(self, contenu: str) -> list[str]:
        pass
