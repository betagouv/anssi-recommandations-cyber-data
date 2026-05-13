from adaptateurs.clients_albert import ClientAlbertIndexation, ReponseCollection
from configuration import MSC, CollectionsMQC
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
        self.documents_existants = []
        self.documents_supprimes = []

    def attribue_collection(self, id_collection: str) -> bool:
        self.id_collection = id_collection
        return True

    def ajoute_documents(
        self, documents: list[DocumentAIndexer]
    ) -> list[ReponseDocument]:
        self.documents_ajoutes = documents
        return []

    def document_existe(self, nom_document: str):
        document_existe = list(
            filter(lambda doc: doc["nom"] == nom_document, self.documents_existants)
        )
        return document_existe[0]["id"] if len(document_existe) > 0 else None

    def supprime_document(self, id_document: str):
        document_existant = list(
            filter(lambda doc: doc["id"] == id_document, self.documents_existants)
        )[0]
        self.documents_supprimes.append(document_existant["nom"])
        self.documents_existants.remove(document_existant)

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


def test_indexe_un_document(un_service_jeopardy):
    client_indexation = ClientAlbertIndexationDeTest()

    ServiceDIndexation(
        client_indexation,
        CollectionsMQC(
            id_collection_indexee="collection-1",
            id_collection_jeopardy="collection-jeopardy",
        ),
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
    ).indexe_documents(["doc-1.pdf"])

    assert client_indexation.id_collection == "collection-1"
    assert len(client_indexation.documents_ajoutes) == 1
    assert client_indexation.documents_ajoutes[0].nom_document == "doc-1.pdf"
    assert (
        client_indexation.documents_ajoutes[0].url
        == "http://documents.local/guides/doc-1.pdf"
    )
    assert client_indexation.documents_ajoutes[0]._type == "PDF"


def test_jeopardyse_les_documents_indexes(un_service_jeopardy):
    ServiceDIndexation(
        ClientAlbertIndexationDeTest(),
        CollectionsMQC(
            id_collection_indexee="collection-1",
            id_collection_jeopardy="collection-jeopardy",
        ),
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
    ).indexe_documents(["nouveau-doc-1.pdf", "nouveau-doc-2.pdf"])

    assert un_service_jeopardy.jeopardyse_documents_appele
    assert un_service_jeopardy.identifiant_collection_jeopardy == "collection-jeopardy"
    assert un_service_jeopardy.noms_documents_a_jeopardyser == [
        "nouveau-doc-1.pdf",
        "nouveau-doc-2.pdf",
    ]
    assert un_service_jeopardy.identifiant_collection_a_jeopardyser == "collection-1"


def test_modifie_un_document_deja_indexe(un_service_jeopardy):
    client_indexation = ClientAlbertIndexationDeTest()
    client_indexation.documents_existants = [{"id": "2", "nom": "doc-2.pdf"}]

    ServiceDIndexation(
        client_indexation,
        CollectionsMQC(
            id_collection_indexee="collection-1",
            id_collection_jeopardy="collection-jeopardy",
        ),
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
    ).indexe_documents(["doc-1.pdf", "doc-2.pdf"])

    assert len(client_indexation.documents_ajoutes) == 2
    assert client_indexation.documents_supprimes == ["doc-2.pdf"]
    assert client_indexation.documents_ajoutes[0].nom_document == "doc-1.pdf"
    assert client_indexation.documents_ajoutes[1].nom_document == "doc-2.pdf"
    assert un_service_jeopardy.noms_documents_a_jeopardyser == [
        "doc-1.pdf",
        "doc-2.pdf",
    ]
