from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union

from typing_extensions import NamedTuple


@dataclass
class DocumentPDF:
    chemin_pdf: str
    url_pdf: str


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


type ReponseDocument = Union[ReponseDocumentEnSucces, ReponseDocumentEnErreur]


class Indexeur(ABC):
    @abstractmethod
    def ajoute_documents(
        self, documents: list[DocumentPDF], id_collection: str | None
    ) -> list[ReponseDocument]:
        pass
