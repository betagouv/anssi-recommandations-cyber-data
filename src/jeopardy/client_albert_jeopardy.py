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


class ClientAlbertJeopardy(ABC):
    @abstractmethod
    def cree_collection(
        self, nom_collection, description_collection
    ) -> ReponseCreationCollection:
        pass

    @abstractmethod
    def ajoute_document(
        self, identifiant_collection: str, document: RequeteCreationDocumentAlbert
    ):
        pass

    @abstractmethod
    def genere_questions(self, prompt: str, contenu: str) -> list[str]:
        pass


class ErreurClientAlbertJeopardy(Exception):
    """Erreur levée lors d'un échange avec Albert."""


@dataclass(frozen=True)
class ConfigurationJeopardy:
    base_url: str
    cle_api: str
    modele_generation: str = "mistral-medium-2508"
