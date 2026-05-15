from adaptateurs.clients_albert import ClientAlbertIndexation, ReponseCollection
from configuration import MSC, CollectionsMQC
from documents.indexeur.indexeur import DocumentAIndexer, ReponseDocument, Indexeur
from documents.service_indexation_documents import ServiceIndexationNouveauxDocuments
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
        self.supprime_document_appele = 0
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
        return []

    def document_existe(self, nom_document: str, id_collection: str) -> str | None:
        if (
            self.leve_une_exception_sur_document_existe
            and nom_document == self.leve_une_exception_sur_document_existe["document"]
        ) and id_collection == self.leve_une_exception_sur_document_existe[
            "collection"
        ]:
            raise Exception(
                "Une erreur est survenue lors de la vérification de l'existence du document"
            )
        documents = self.collections_existantes.get(id_collection)
        if documents:
            document_existe = list(
                filter(lambda doc: doc["nom"] == nom_document, documents)
            )
            return document_existe[0]["id"] if len(document_existe) > 0 else None
        return None

    def supprime_document(self, id_document: str):
        self.supprime_document_appele += 1
        if self.leve_une_exception_sur_supprime_document:
            docs_dans_collection = self.collections_existantes.get(
                self.leve_une_exception_sur_supprime_document["collection"], []
            )
            if id_document == self.leve_une_exception_sur_supprime_document[
                "document"
            ] and any(doc["id"] == id_document for doc in docs_dans_collection):
                raise Exception(
                    "Une erreur est survenue lors de la suppression du document"
                )
        docs_a_supprimer = {
            k: [doc for doc in docs if doc["id"] == id_document]
            for k, docs in self.collections_existantes.items()
        }
        for k, v in docs_a_supprimer.items():
            if v:
                self.documents_supprimes.setdefault(k, []).extend(v)
        self.collections_existantes = {
            k: [doc for doc in docs if doc["id"] != id_document]
            for k, docs in self.collections_existantes.items()
        }

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

    def document_existe_leve_une_erreur(self, id_collection: str, nom_document: str):
        self.leve_une_exception_sur_document_existe = {
            "collection": id_collection,
            "document": nom_document,
        }

    def supprime_document_leve_une_erreur(self, id_collection: str, id_document: str):
        self.leve_une_exception_sur_supprime_document = {
            "collection": id_collection,
            "document": id_document,
        }


def test_indexe_un_document(un_service_jeopardy):
    client_indexation = ClientAlbertIndexationDeTest()

    ServiceIndexationNouveauxDocuments(
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
    ServiceIndexationNouveauxDocuments(
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
    client_indexation.collections_existantes = {
        "collection-1": [{"id": "2", "nom": "doc-2.pdf"}]
    }

    ServiceIndexationNouveauxDocuments(
        client_indexation,
        CollectionsMQC(
            id_collection_indexee="collection-1",
            id_collection_jeopardy="collection-jeopardy",
        ),
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
    ).indexe_documents(["doc-1.pdf", "doc-2.pdf"])

    assert client_indexation.documents_supprimes.get("collection-1") == [
        {"id": "2", "nom": "doc-2.pdf"}
    ]
    assert len(client_indexation.documents_ajoutes) == 2
    assert client_indexation.documents_ajoutes[0].nom_document == "doc-1.pdf"
    assert client_indexation.documents_ajoutes[1].nom_document == "doc-2.pdf"
    assert un_service_jeopardy.noms_documents_a_jeopardyser == [
        "doc-1.pdf",
        "doc-2.pdf",
    ]


def test_supprime_le_document_correspondant_dans_la_collection_jeopardy(
    un_service_jeopardy,
):
    client_indexation = ClientAlbertIndexationDeTest()
    client_indexation.collections_existantes = {
        "collection-1": [{"id": "2", "nom": "doc-2.pdf"}],
        "collection-jeopardy": [{"id": "b", "nom": "doc-2.pdf"}],
    }

    client_indexation.documents_jeopardy_existants = [{"id": "b", "nom": "doc-2.pdf"}]

    ServiceIndexationNouveauxDocuments(
        client_indexation,
        CollectionsMQC(
            id_collection_indexee="collection-1",
            id_collection_jeopardy="collection-jeopardy",
        ),
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
    ).indexe_documents(["doc-1.pdf", "doc-2.pdf"])

    assert client_indexation.documents_supprimes.get("collection-jeopardy") == [
        {"id": "b", "nom": "doc-2.pdf"}
    ]


def test_continue_le_traitement_si_le_document_existe_leve_une_erreur(
    un_service_jeopardy,
):
    client_indexation = ClientAlbertIndexationDeTest()
    client_indexation.collections_existantes = {
        "collection-1": [
            {"id": "1", "nom": "doc-1.pdf"},
            {"id": "2", "nom": "doc-2.pdf"},
        ],
        "collection-jeopardy": [
            {"id": "a", "nom": "doc-1.pdf"},
            {"id": "b", "nom": "doc-2.pdf"},
        ],
    }
    client_indexation.document_existe_leve_une_erreur("collection-1", "doc-1.pdf")
    client_indexation.documents_jeopardy_existants = [{"id": "b", "nom": "doc-2.pdf"}]

    ServiceIndexationNouveauxDocuments(
        client_indexation,
        CollectionsMQC(
            id_collection_indexee="collection-1",
            id_collection_jeopardy="collection-jeopardy",
        ),
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
    ).indexe_documents(["doc-1.pdf", "doc-2.pdf"])

    assert len(client_indexation.documents_ajoutes) == 1
    assert client_indexation.documents_ajoutes[0].nom_document == "doc-2.pdf"
    assert un_service_jeopardy.noms_documents_a_jeopardyser == [
        "doc-2.pdf",
    ]


def test_continue_le_traitement_si_supprime_document_leve_une_erreur(
    un_service_jeopardy,
):
    client_indexation = ClientAlbertIndexationDeTest()
    client_indexation.collections_existantes = {
        "collection-1": [
            {"id": "1", "nom": "doc-1.pdf"},
            {"id": "2", "nom": "doc-2.pdf"},
        ],
    }
    client_indexation.supprime_document_leve_une_erreur("collection-1", "1")

    ServiceIndexationNouveauxDocuments(
        client_indexation,
        CollectionsMQC(
            id_collection_indexee="collection-1",
            id_collection_jeopardy="collection-jeopardy",
        ),
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
    ).indexe_documents(["doc-1.pdf", "doc-2.pdf"])

    assert len(client_indexation.documents_ajoutes) == 1
    assert client_indexation.documents_ajoutes[0].nom_document == "doc-2.pdf"
    assert un_service_jeopardy.donnees_recues.noms_documents == ["doc-2.pdf"]


def test_supprime_les_documents(un_service_jeopardy):
    client_indexation = ClientAlbertIndexationDeTest()
    client_indexation.collections_existantes = {
        "collection-1": [
            {"id": "1", "nom": "doc-1.pdf"},
            {"id": "2", "nom": "doc-2.pdf"},
        ],
    }

    ServiceIndexationNouveauxDocuments(
        client_indexation,
        CollectionsMQC(
            id_collection_indexee="collection-1",
            id_collection_jeopardy="collection-jeopardy",
        ),
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
    ).indexe_documents([], ["doc-1.pdf", "doc-2.pdf"])

    documents_supprimes = client_indexation.documents_supprimes.get("collection-1")
    assert documents_supprimes is not None
    assert len(documents_supprimes) == 2


def test_supprime_les_documents_seulement_si_le_document_existe(un_service_jeopardy):
    client_indexation = ClientAlbertIndexationDeTest()
    client_indexation.collections_existantes = {
        "collection-1": [
            {"id": "2", "nom": "doc-2.pdf"},
        ],
    }

    ServiceIndexationNouveauxDocuments(
        client_indexation,
        CollectionsMQC(
            id_collection_indexee="collection-1",
            id_collection_jeopardy="collection-jeopardy",
        ),
        MSC(url="http://documents.local", chemin_guides="guides"),
        un_service_jeopardy,
    ).indexe_documents([], ["doc-1.pdf", "doc-2.pdf"])

    assert client_indexation.supprime_document_appele == 1
