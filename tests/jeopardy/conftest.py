from collections.abc import Callable
from typing import Any

import pytest

from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    ReponseCreationCollection,
    RequeteCreationDocumentAlbert,
)
from jeopardy.collecteur import Document, Chunk


class ConstructeurDeDocument:
    def __init__(self):
        self.contenu = "contenu de test"
        self.nom = "nom de test"
        self.metadonnees = {"a": "b"}
        self.clef = "Un document indexé"
        self.identifiant_document = "doc-123"
        self.chunks: list[dict[str, dict[str, Any]]] = []

    def construis(self) -> Document:
        return Document(
            {self.clef: {"id": self.identifiant_document, "chunks": self.chunks}}
        )

    def ajoute_chunk(self, chunk: Chunk):
        self.chunks.append(chunk._asdict())
        return self


@pytest.fixture
def un_constructeur_de_document() -> Callable[[], ConstructeurDeDocument]:
    def constructeur():
        return ConstructeurDeDocument()

    return constructeur


class ClientAlbertJeopardyDeTest(ClientAlbertJeopardy):
    def __init__(self):
        super().__init__()
        self._reponses_questions_generees = []
        self.questions_generees = []
        self.collection_creee = False
        self.document_cree = None
        self._identifiant_de_collection = None
        self.collection_attendue = None
        self.chunks_fournis: list[str] = []
        self.prompt_passe: str = ""

    def genere_question(self, prompt: str, contenu: str) -> list[str]:
        self.questions_generees = self._reponses_questions_generees
        self.chunks_fournis.append(contenu)
        self.prompt_passe = prompt
        return self._reponses_questions_generees

    def cree_collection(self) -> ReponseCreationCollection:
        self.collection_creee = True
        return ReponseCreationCollection(id=self._identifiant_de_collection)

    def ajoute_document(
        self, identifiant_collection: str, document: RequeteCreationDocumentAlbert
    ):
        self.document_cree = document
        self.collection_attendue = identifiant_collection

    def avec_un_identifiant_de_collection(self, identifiant_collection: str):
        self._identifiant_de_collection = identifiant_collection
        return self

    def qui_retourne_les_questions_generees(self, questions_generees: list[str]):
        self._reponses_questions_generees = questions_generees
        return self


@pytest.fixture
def un_client_albert_de_test() -> Callable[[], ClientAlbertJeopardyDeTest]:
    def constructeur():
        return ClientAlbertJeopardyDeTest()

    return constructeur
