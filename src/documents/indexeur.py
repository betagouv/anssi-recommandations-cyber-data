from abc import ABC, abstractmethod
from typing import Union, Literal, Optional

from typing_extensions import NamedTuple


class DocumentAIndexer(ABC):
    _type: Literal["PDF", "HTML"]

    @property
    def type(self) -> Literal["PDF", "HTML"]:
        return self._type

    @property
    @abstractmethod
    def nom_document(self) -> str:
        pass

    @property
    @abstractmethod
    def url(self) -> str:
        pass

    @property
    @abstractmethod
    def chemin(self) -> str:
        pass

    @abstractmethod
    def initie_page(self, numero_page: Optional[int] = None):
        pass


class PayloadDocument(NamedTuple):
    collection: str
    metadata: str
    chunk_min_size: int


class ReponseDocumentEnSucces(NamedTuple):
    id: str
    name: str
    collection_id: str
    created_at: str
    updated_at: str


class ReponseDocumentEnErreur(NamedTuple):
    detail: str
    document_en_erreur: str


type ReponseDocument = Union[ReponseDocumentEnSucces, ReponseDocumentEnErreur]


class Indexeur(ABC):
    @abstractmethod
    def ajoute_documents(
        self, documents: list[DocumentAIndexer], id_collection: str | None
    ) -> list[ReponseDocument]:
        pass
