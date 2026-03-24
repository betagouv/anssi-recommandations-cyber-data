from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    ReponseCreationCollection,
    RequeteCreationDocumentAlbert,
)
from jeopardy.collecteur import Document, CollecteurDeQuestions


class ClientAlbertJeopardyDeTest(ClientAlbertJeopardy):
    def __init__(self):
        super().__init__()
        self.collection_creee = False
        self.document_cree = None
        self._identifiant_de_collection = None
        self.collection_attendue = None

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


def test_cree_une_collection():
    client_albert = ClientAlbertJeopardyDeTest()

    CollecteurDeQuestions(client_albert).collecte([])

    assert client_albert.collection_creee


def test_ajoute_un_document_a_la_collection():
    client_albert = ClientAlbertJeopardyDeTest().avec_un_identifiant_de_collection(
        "collection-123"
    )

    CollecteurDeQuestions(client_albert).collecte(
        [(Document({"Un document indexé": {"id": "doc-123"}}))]
    )

    assert client_albert.collection_attendue == "collection-123"
    assert client_albert.document_cree is not None
    assert client_albert.document_cree.metadata == {
        "source": {
            "nom_document": "Un document indexé",
            "id_document": "doc-123",
        }
    }
