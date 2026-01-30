from abc import ABC, abstractmethod

from openai import OpenAI
from typing_extensions import NamedTuple

from guides.executeur_requete import ExecuteurDeRequete
from guides.indexeur import DocumentPDF, ReponseDocument, Indexeur


class PayloadCollection(NamedTuple):
    name: str
    description: str
    visibility: str = "private"


class ReponseCollection(NamedTuple):
    id: str
    name: str
    description: str
    visibility: str
    documents: int
    created_at: str
    updated_at: str


class ReponseCollectionAlbert(NamedTuple):
    id: str
    name: str
    description: str
    visibility: str
    documents: int
    created_at: str
    updated_at: str


class ClientAlbert(ABC):
    def __init__(
        self,
        url: str,
        cle_api: str,
        indexeur: Indexeur,
        executeur_de_requete: ExecuteurDeRequete = ExecuteurDeRequete(),
    ):
        self.url = url
        self.client_openai = OpenAI(base_url=url, api_key=cle_api)
        self.id_collection: str | None = None
        self.indexeur = indexeur
        self.executeur_de_requete = executeur_de_requete
        self.executeur_de_requete.initialise(cle_api)

    @abstractmethod
    def cree_collection(self, nom: str, description: str) -> ReponseCollection:
        pass

    @abstractmethod
    def ajoute_documents(
        self,
        documents: list[DocumentPDF],
    ) -> list[ReponseDocument]:
        pass

    @abstractmethod
    def _collection_existe(self, id_collection: str) -> bool:
        pass

    @abstractmethod
    def attribue_collection(self, id_collection: str) -> bool:
        pass
