import uuid

from adaptateurs.clients_albert import ClientAlbertIndexation, ReponseCollection
from configuration import MSC
from documents.indexeur.indexeur import (
    Indexeur,
    DocumentAIndexer,
    ReponseDocument,
    ReponseDocumentEnSucces,
)
from documents.service_indexation_collections import ServiceIndexationNouvellesCollections
from infra.memoire.executeur_de_requete_memoire import ExecuteurDeRequeteDeTest


class IndexeurDeTest(Indexeur):
    def __init__(self):
        super().__init__()

    def ajoute_documents(
        self, documents: list[DocumentAIndexer], id_collection: str | None
    ) -> list[ReponseDocument]:
        return []


class ClientAlbertIndexationDeTest(ClientAlbertIndexation):
    def __init__(self):
        super().__init__(
            "", "", IndexeurDeTest(), ExecuteurDeRequeteDeTest(reponse_attendue=[])
        )
        self.leve_une_exception_sur_document_existe = None
        self.leve_une_exception_sur_supprime_document = None
        self.documents_ajoutes = []
        self.collections_existantes = {}
        self.documents_supprimes = {}
        self.documents_jeopardy_existants = []
        self.documents_jeopardy_supprimes = []

    def attribue_collection(self, id_collection: str) -> bool:
        self.id_collection = id_collection
        return True

    def ajoute_documents(
        self, documents: list[DocumentAIndexer]
    ) -> list[ReponseDocument]:
        self.documents_ajoutes = documents
        resultat:list[ReponseDocument] = []
        for document in documents:
            resultat.append(
                ReponseDocumentEnSucces(
                    id=str(uuid.uuid4()),
                    name=document.nom_document,
                    collection_id=self.id_collection,
                    created_at="2023-01-01T00:00:00Z",
                    updated_at="2023-01-01T00:00:00Z",
                )
            )
        return resultat

    def document_existe(self, nom_document: str, id_collection: str) -> str | None:
        return None

    def supprime_document(self, id_document: str):
        pass

    def _collection_existe(self, id_collection: str) -> bool:
        return True

    def cree_collection(self, nom: str, description: str) -> ReponseCollection:
        return ReponseCollection(
            name=nom,
            description=description,
            id="collection-test",
            visibility="public",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            documents=0,
        )


def test_ajoute_un_guide_de_l_anssi(un_service_jeopardy):
    client_indexation = ClientAlbertIndexationDeTest()

    reponse = ServiceIndexationNouvellesCollections(
        client_indexation,
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
    ).indexe_documents(["doc-1.pdf"])

    assert len(reponse) == 1
    assert reponse[0].id is not None
    assert reponse[0].collection_id == "collection-test"
    assert reponse[0].name == "doc-1.pdf"
