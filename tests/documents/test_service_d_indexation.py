from adaptateurs.clients_albert import ClientAlbertIndexation, ReponseCollection
from configuration import MSC
from documents.indexeur.indexeur import DocumentAIndexer, ReponseDocument, Indexeur
from documents.service_indexation_documents import ServiceDIndexation
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
        self.documents_ajoutes = []

    def attribue_collection(self, id_collection: str) -> bool:
        self.id_collection = id_collection
        return True

    def ajoute_documents(
        self, documents: list[DocumentAIndexer]
    ) -> list[ReponseDocument]:
        self.documents_ajoutes = documents
        return []

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


def test_indexe_un_document():
    client_indexation = ClientAlbertIndexationDeTest()

    ServiceDIndexation(
        client_indexation,
        "collection-1",
        MSC(url="http://documents.local", chemin_guides="guides"),
    ).indexe_documents(["doc-1.pdf"])

    assert client_indexation.id_collection == "collection-1"
    assert len(client_indexation.documents_ajoutes) == 1
    assert client_indexation.documents_ajoutes[0].nom_document == "doc-1.pdf"
    assert (
        client_indexation.documents_ajoutes[0].url
        == "http://documents.local/guides/doc-1.pdf"
    )
    assert client_indexation.documents_ajoutes[0]._type == "PDF"
