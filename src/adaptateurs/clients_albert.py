from abc import ABC, abstractmethod

from typing_extensions import NamedTuple

from configuration import CollectionsMQC
from documents.indexeur.indexeur import Indexeur, DocumentAIndexer, ReponseDocument
from infra.executeur_requete import ExecuteurDeRequete


class PayloadCollection(NamedTuple):
    name: str
    description: str
    visibility: str = "private"


class ReponseCreationCollection(NamedTuple):
    id: str
    name: str
    description: str
    visibility: str
    documents: int
    created_at: str
    updated_at: str


class ReponseCollection(NamedTuple):
    id: str
    name: str
    description: str
    visibility: str
    documents: int
    created: str
    updated: str


class ReponseDocumentCollection(NamedTuple):
    id: str
    name: str
    created: str
    chunks: int


class ReponseDocuments(NamedTuple):
    indexee: list[ReponseDocumentCollection]
    jeopardy: list[ReponseDocumentCollection]


class ClientAlbertIndexation(ABC):
    def __init__(
        self,
        url: str,
        cle_api: str,
        indexeur: Indexeur,
        executeur_de_requete: ExecuteurDeRequete = ExecuteurDeRequete(),
    ):
        self.url = url
        self.id_collection: str = ""
        self.indexeur = indexeur
        self.executeur_de_requete = executeur_de_requete
        self.executeur_de_requete.initialise_connexion_securisee(cle_api)

    @abstractmethod
    def cree_collection(self, nom: str, description: str) -> ReponseCreationCollection:
        pass

    @abstractmethod
    def ajoute_documents(
        self,
        documents: list[DocumentAIndexer],
    ) -> list[ReponseDocument]:
        pass

    @abstractmethod
    def _collection_existe(self, id_collection: str) -> bool:
        pass

    @abstractmethod
    def attribue_collection(self, id_collection: str) -> bool:
        pass

    @abstractmethod
    def document_existe(self, nom_document: str, id_collection: str) -> str | None:
        pass

    @abstractmethod
    def supprime_document(self, id_document: str):
        pass


class ClientAlbertReformulation(ABC):
    @abstractmethod
    def reformule_la_question(self, prompt: str, question: str) -> str:
        pass


class ClientAlbertCollections(ABC):
    def __init__(
        self,
        url: str,
        cle_api: str,
        collections_mqc: CollectionsMQC,
        executeur_de_requete: ExecuteurDeRequete = ExecuteurDeRequete(),
    ):
        self.url = url
        self.executeur_de_requete = executeur_de_requete
        self.collections_mqc = collections_mqc
        self.executeur_de_requete.initialise_connexion_securisee(cle_api)

    @abstractmethod
    def recupere_collections_mqc(self) -> list[ReponseCollection]:
        pass

    @abstractmethod
    def recupere_documents_collection(
        self, offset_indexation: int, offset_jeopardy: int
    ) -> ReponseDocuments:
        pass
