from typing import Optional

import pytest

from adaptateurs.clients_albert import ClientAlbertIndexation, ReponseCreationCollection
from configuration import MSC
from documents.indexeur.indexeur import DocumentAIndexer, ReponseDocument
from documents.pdf.document_pdf import DocumentPDFDistant
from documents.service_indexation_collections import (
    ServiceIndexationNouvellesCollections,
    DocumentsSources,
)
from jeopardy.service import (
    CollectionEntiere,
    ListeDeDocuments,
    ServiceJeopardyse,
)

MSC_DE_TEST = MSC(url="http://msc.local", chemin_guides="/guides")


class ClientAlbertIndexationDeTest(ClientAlbertIndexation):
    def __init__(self):
        self.id_collection = ""
        self.documents_recus: list[DocumentAIndexer] = []

    def cree_collection(self, nom: str, description: str) -> ReponseCreationCollection:
        return ReponseCreationCollection(
            id="id-de-test",
            name=nom,
            description=description,
            visibility="private",
            documents=0,
            created_at="",
            updated_at="",
        )

    def ajoute_documents(
        self, documents: list[DocumentAIndexer]
    ) -> list[ReponseDocument]:
        self.documents_recus = documents
        return []

    def _collection_existe(self, id_collection: str) -> bool:
        return True

    def attribue_collection(self, id_collection: str) -> bool:
        return True

    def document_existe(self, nom_document: str, id_collection: str) -> Optional[str]:
        return None

    def supprime_document(self, id_document: str) -> None:
        pass


class ServiceJeopardyseDeTest(ServiceJeopardyse):
    def __init__(self):
        pass

    def jeopardyse(
        self,
        donnees: CollectionEntiere | ListeDeDocuments,
        taille_paquet_chunks: int = 10,
    ) -> None:
        pass

    def recupere_les_documents(
        self,
        donnees: CollectionEntiere | ListeDeDocuments,
        taille_paquet_chunks: int = 10,
    ) -> tuple[list, str]:
        return [], ""


def test_indexe_le_document_maitrise_si_chemin_fourni(monkeypatch: pytest.MonkeyPatch):
    from documents.html.document_html import DocumentReponsesMaitrisees

    un_document_maitrise = DocumentReponsesMaitrisees("reponses", chemin="chemin.html")
    monkeypatch.setattr(
        "documents.service_indexation_collections.collecte_document_maitrise",
        lambda _: un_document_maitrise,
    )

    client = ClientAlbertIndexationDeTest()
    service = ServiceIndexationNouvellesCollections(
        client, MSC_DE_TEST, ServiceJeopardyseDeTest()
    )

    service.indexe_documents("nom", "desc", DocumentsSources())

    assert un_document_maitrise in client.documents_recus


def test_indexe_les_documents_distants_si_chemin_fourni(
    monkeypatch: pytest.MonkeyPatch,
):
    un_document_distant = DocumentPDFDistant(
        "doc-distant", "http://example.com/doc.pdf"
    )
    monkeypatch.setattr(
        "documents.service_indexation_collections.mappe_en_document_distant",
        lambda _: {},
    )
    monkeypatch.setattr(
        "documents.service_indexation_collections.collecte_documents_distants",
        lambda _: [un_document_distant],
    )

    client = ClientAlbertIndexationDeTest()
    service = ServiceIndexationNouvellesCollections(
        client, MSC_DE_TEST, ServiceJeopardyseDeTest()
    )

    service.indexe_documents("nom", "desc", DocumentsSources())

    assert un_document_distant in client.documents_recus
