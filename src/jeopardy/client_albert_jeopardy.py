from __future__ import annotations

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


@dataclass
class ReponseCreationDocument:
    id: str


class ClientAlbertJeopardy(ABC):
    @abstractmethod
    def cree_collection(
        self, nom_collection, description_collection
    ) -> ReponseCreationCollection:
        pass

    @abstractmethod
    def cree_document(
        self, identifiant_collection: str, document: RequeteCreationDocumentAlbert
    ) -> ReponseCreationDocument:
        pass

    @abstractmethod
    def genere_questions(self, prompt: str, contenu: str) -> list[str]:
        pass

    @abstractmethod
    def ajoute_chunks_dans_document(
        self,
        identifiant_collection: str,
        requete: RequeteAjoutChunksDansDocumentAlbert,
    ):
        pass

    @abstractmethod
    def recupere_chunks_document(self, id_document: str) -> list[dict]:
        pass

    @abstractmethod
    def recupere_documents_collection(
        self, id_collection: str
    ) -> ReponseDocumentsCollectionOrigine:
        pass


class ErreurClientAlbertJeopardy(Exception):
    """Erreur levée lors d'un échange avec Albert."""


@dataclass(frozen=True)
class ConfigurationJeopardy:
    base_url: str
    cle_api: str
    modele_generation: str = "openai/gpt-oss-120b"


@dataclass
class RequeteAjoutChunksDansDocumentAlbert:
    id_document: str
    chunks: list[dict[str, Any]]


@dataclass
class ReponseDocumentOrigine:
    id: str
    nom: str
    nombre_chunks: int


@dataclass
class ReponseDocumentsCollectionOrigine:
    id: str
    documents: list[ReponseDocumentOrigine]
