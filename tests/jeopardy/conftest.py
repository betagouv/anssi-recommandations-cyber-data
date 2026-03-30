from collections.abc import Callable
from dataclasses import dataclass

import pytest

from documents.docling.multi_processeur import Multiprocesseur
from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    ReponseCreationCollection,
    ReponseCreationDocument,
    RequeteCreationDocumentAlbert,
    RequeteAjoutChunksDansDocumentAlbert,
    ReponseDocumentOrigine,
    ReponseDocumentsCollectionOrigine,
)
from jeopardy.collecteur import Document, Chunk
from jeopardy.questions import EntrepotQuestionGenereeMemoire


class ConstructeurDeDocument:
    def __init__(self):
        self.contenu = "contenu de test"
        self.nom = "nom de test"
        self.metadonnees = {"a": "b"}
        self.clef = "Un document indexé"
        self.identifiant_document = "doc-123"
        self.chunks = []

    def construis(self) -> Document:
        return Document(
            {self.clef: {"id": self.identifiant_document, "chunks": self.chunks}}
        )

    def ajoute_chunk(self, chunk: Chunk):
        self.chunks.append(
            {
                "id": chunk.id,
                "contenu": chunk.contenu,
                "page": chunk.page,
            }
        )
        return self

    def ajoute_nombre_de_chunks(self, nombre_de_chunks: int):
        for i, chunk in enumerate(range(nombre_de_chunks)):
            c = Chunk(contenu=f"le contenu numero {i}", id=i, page=42)
            self.ajoute_chunk(c)
        return self


@pytest.fixture
def un_constructeur_de_document() -> Callable[[], ConstructeurDeDocument]:
    def constructeur():
        return ConstructeurDeDocument()

    return constructeur


@dataclass
class AppelAjoutChunks:
    identifiant_collection: str
    requete: RequeteAjoutChunksDansDocumentAlbert


class ClientAlbertJeopardyDeTest(ClientAlbertJeopardy):
    def __init__(self):
        super().__init__()
        self.description_collection_passe = None
        self.nom_collection_passe = None
        self._reponses_questions_generees = []
        self.questions_generees = []
        self.collection_creee = False
        self.document_cree = None
        self._identifiant_de_collection = None
        self._identifiant_document_cree = "doc-cree-123"
        self.collection_attendue = None
        self.document_ajoute = None
        self.chunks_fournis = []
        self.prompt_passe = ""
        self.appels_ajout_chunks = []
        self.identifiant_collection_lu = None
        self._identifiants_documents = []
        self.identifiant_document_lu = None
        self._chunks_par_document: dict[str, list[dict]] = {}

    def genere_questions(self, prompt: str, contenu: str) -> list[str]:
        self.questions_generees = self._reponses_questions_generees
        self.chunks_fournis.append(contenu)
        self.prompt_passe = prompt
        return self._reponses_questions_generees

    def cree_collection(
        self, nom_collection, description_collection
    ) -> ReponseCreationCollection:
        self.collection_creee = True
        self.nom_collection_passe = nom_collection
        self.description_collection_passe = description_collection
        return ReponseCreationCollection(id=self._identifiant_de_collection)

    def cree_document(
        self, identifiant_collection: str, document: RequeteCreationDocumentAlbert
    ) -> ReponseCreationDocument:
        self.document_cree = document
        self.collection_attendue = identifiant_collection
        return ReponseCreationDocument(id=self._identifiant_document_cree)

    def avec_un_identifiant_de_collection(self, identifiant_collection: str):
        self._identifiant_de_collection = identifiant_collection
        return self

    def qui_retourne_une_collection_avec_les_identifiants_de_document(
        self, identifiants_documents: list[str]
    ):
        self._identifiants_documents.extend(identifiants_documents)
        return self

    def avec_un_identifiant_de_document_cree(self, identifiant_document: str):
        self._identifiant_document_cree = identifiant_document
        return self

    def qui_retourne_les_questions_generees(self, questions_generees: list[str]):
        self._reponses_questions_generees = questions_generees
        return self

    def ajoute_chunks_dans_document(
        self,
        identifiant_collection: str,
        requete: RequeteAjoutChunksDansDocumentAlbert,
    ):
        self.appels_ajout_chunks.append(
            AppelAjoutChunks(
                identifiant_collection=identifiant_collection,
                requete=requete,
            )
        )

    def liste_ids_documents_de_collection(
        self, identifiant_collection: str
    ) -> list[str]:
        self.identifiant_collection_lu = identifiant_collection
        return list(self._chunks_par_document.keys())

    def recupere_documents_collection(
        self, identifiant_collection: str
    ) -> ReponseDocumentsCollectionOrigine:
        self.identifiant_collection_lu = identifiant_collection
        return ReponseDocumentsCollectionOrigine(
            id=identifiant_collection,
            documents=[
                ReponseDocumentOrigine(
                    id=identifiant,
                    nom=f"document-{identifiant}",
                    nombre_chunks=len(self._chunks_par_document.get(identifiant, [])),
                )
                for identifiant in self._identifiants_documents
            ],
        )

    def recupere_chunks_document(self, id_document: str) -> list[dict]:
        self.identifiant_document_lu = id_document
        return self._chunks_par_document.get(id_document, [])

    def avec_les_chunks_du_document(self, id_document: str, chunks: list[dict]):
        self._chunks_par_document[id_document] = chunks
        return self


@pytest.fixture
def un_client_albert_de_test() -> Callable[[], ClientAlbertJeopardyDeTest]:
    def constructeur():
        return ClientAlbertJeopardyDeTest()

    return constructeur


@pytest.fixture
def un_entrepot_memoire() -> EntrepotQuestionGenereeMemoire:
    return EntrepotQuestionGenereeMemoire()


class MultiProcesseurDeTest(Multiprocesseur):
    def __init__(self):
        self.a_ete_appele = False

    def execute(self, func, iterable) -> list:
        self.a_ete_appele = True
        resultats = []
        for chunk in iterable:
            resultats.append(func(chunk))
        return resultats


@pytest.fixture()
def un_multiprocesseur() -> MultiProcesseurDeTest:
    return MultiProcesseurDeTest()
