import uuid

from adaptateurs.clients_albert import ClientAlbertIndexation, ReponseCreationCollection
from configuration import MSC
from documents.indexeur.indexeur import (
    Indexeur,
    DocumentAIndexer,
    ReponseDocument,
    ReponseDocumentEnSucces,
)
from documents.service_indexation_collections import (
    ServiceIndexationNouvellesCollections,
    DocumentsSources,
    CollecteurDocumentsAdditionnels,
)
from infra.memoire.executeur_de_requete_memoire import ExecuteurDeRequeteDeTest
from jeopardy.service import CollectionEntiere


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
        self.documents_ajoutes = []
        self.collections_creees = {}

    def attribue_collection(self, id_collection: str) -> bool:
        self.id_collection = id_collection
        return True

    def ajoute_documents(
        self, documents: list[DocumentAIndexer]
    ) -> list[ReponseDocument]:
        self.documents_ajoutes = documents
        resultat: list[ReponseDocument] = []
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

    def cree_collection(self, nom: str, description: str) -> ReponseCreationCollection:
        reponse_collection = ReponseCreationCollection(
            name=nom,
            description=description,
            id="collection-test",
            visibility="public",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
            documents=0,
        )
        self.collections_creees[nom] = reponse_collection
        return reponse_collection


class CollecteurDocumentsAdditionnelsDeTest(CollecteurDocumentsAdditionnels):
    def collecte(self) -> list[DocumentAIndexer]:
        return []


def test_ajoute_un_guide_de_l_anssi(un_service_jeopardy):
    client_indexation = ClientAlbertIndexationDeTest()

    reponse = ServiceIndexationNouvellesCollections(
        client_indexation,
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
        CollecteurDocumentsAdditionnelsDeTest(),
    ).indexe_documents("", "", DocumentsSources(fichiers=["doc-1.pdf"]))

    assert len(reponse) == 1
    assert reponse[0].id is not None
    assert reponse[0].collection_id == "collection-test"
    assert reponse[0].name == "doc-1.pdf"


def test_nomme_et_decrit_la_nouvelle_collection(un_service_jeopardy):
    client_indexation = ClientAlbertIndexationDeTest()

    ServiceIndexationNouvellesCollections(
        client_indexation,
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
        CollecteurDocumentsAdditionnelsDeTest(),
    ).indexe_documents(
        "le_nouveau_nom",
        "la description nouvelle",
        DocumentsSources(fichiers=["doc-1.pdf"]),
    )

    assert (
        client_indexation.collections_creees["le_nouveau_nom"].name == "le_nouveau_nom"
    )
    assert (
        client_indexation.collections_creees["le_nouveau_nom"].description
        == "la description nouvelle"
    )


def test_jeopardyse_un_guide_de_l_anssi(un_service_jeopardy):
    client_indexation = ClientAlbertIndexationDeTest()

    ServiceIndexationNouvellesCollections(
        client_indexation,
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
        CollecteurDocumentsAdditionnelsDeTest(),
    ).indexe_documents(
        "le_nouveau_nom", "pour tester", DocumentsSources(fichiers=["doc-1.pdf"])
    )

    assert un_service_jeopardy.jeopardyse_appele
    assert isinstance(un_service_jeopardy.donnees_recues, CollectionEntiere)
    assert un_service_jeopardy.donnees_recues.id_collection == "collection-test"
    assert (
        un_service_jeopardy.donnees_recues.nom_collection == "Jeopardy - le_nouveau_nom"
    )
    assert un_service_jeopardy.donnees_recues.description_collection == "pour tester"
