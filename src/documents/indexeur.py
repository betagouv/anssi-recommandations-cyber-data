from abc import ABC, abstractmethod
from typing import Union, Literal, Callable

from docling_core.transforms.chunker import BaseChunk
from typing_extensions import NamedTuple

from documents.document import BlocPage, Page

type NumeroPage = int
type CreationDePage = Callable[[], Page]
type CreationDeBlocPage = Callable[[], BlocPage]

type GenerationDePage = Callable[
    [], tuple[NumeroPage, CreationDePage, CreationDeBlocPage]
]


class GenerateurDePage(ABC):
    @abstractmethod
    def genere(
        self, chunk: BaseChunk
    ) -> GenerationDePage:
        pass


class DocumentAIndexer(ABC):
    _type: Literal["PDF", "HTML"]

    def __init__(self):
        self._generateur = None

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

    @property
    @abstractmethod
    def generateur(self) -> GenerateurDePage:
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
