from adaptateurs.client_albert import ReponseCollectionAlbert
from adaptateurs.client_albert_reel import ClientAlbertReel
from guides.indexeur import DocumentPDF, Indexeur, ReponseDocument
from guides.indexeur_albert import IndexeurBaseVectorielleAlbert


def test_client_albert_initialise_correctement():
    url = "https://test.api"

    client = ClientAlbertReel(url, "test-key", IndexeurBaseVectorielleAlbert(url))

    assert str(client.client_openai.base_url) == "https://test.api"
    assert (
        client.executeur_de_requete.session.headers["Authorization"]
        == "Bearer test-key"
    )
    assert client.id_collection is None


def test_client_albert_cree_collection(
    un_executeur_de_requete, une_reponse_de_creation_de_collection_OK
):
    url = "https://test.api"
    reponse_attendue = ReponseCollectionAlbert(
        id="mem-0",
        name="test collection",
        description="description test",
        visibility="public",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        documents=1,
    )

    client = ClientAlbertReel(
        url,
        "test-key",
        IndexeurBaseVectorielleAlbert(url),
        un_executeur_de_requete(
            [une_reponse_de_creation_de_collection_OK(reponse_attendue)]
        ),
    )

    reponse = client.cree_collection("test collection", "description test")

    assert client.id_collection == "mem-0"
    assert reponse.id == "mem-0"
    assert reponse.name == "test collection"


def test_attribue_id_collection_au_client_albert(
    un_executeur_de_requete, une_reponse_de_recuperation_de_collection_OK
):
    reponse_collection = ReponseCollectionAlbert(
        id="collection-123",
        name="test collection",
        description="description test",
        visibility="public",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        documents=1,
    )
    client = ClientAlbertReel(
        "https://test.api",
        "test-key",
        IndexeurBaseVectorielleAlbert("https://test.api"),
        un_executeur_de_requete(
            [une_reponse_de_recuperation_de_collection_OK(reponse_collection)]
        ),
    )
    id_collection = "collection-123"

    result = client.attribue_collection(id_collection)

    assert result is True
    assert client.id_collection == id_collection


def test_client_albert_verifie_collection_n_existe_pas(
    un_executeur_de_requete, une_reponse_de_recuperation_de_collection_KO
):
    client = ClientAlbertReel(
        "https://test.api",
        "test-key",
        IndexeurBaseVectorielleAlbert("https://test.api"),
        un_executeur_de_requete([une_reponse_de_recuperation_de_collection_KO]),
    )
    client.collections_existantes = {"collection-123"}

    result = client.attribue_collection("collection-123")

    assert result is False


class IndexeurDeTest(Indexeur):
    def __init__(self):
        super().__init__()
        self.documents_recus = []
        self.collection_recue = None

    def ajoute_documents(
        self, documents: list[DocumentPDF], id_collection: str | None
    ) -> list[ReponseDocument]:
        self.documents_recus.extend(documents)
        self.collection_recue = id_collection
        return []


def test_client_albert_ajoute_documents(
    un_executeur_de_requete, une_reponse_de_creation_de_collection_OK
):
    indexeur_de_test = IndexeurDeTest()
    collection = ReponseCollectionAlbert(
        id="id-collection",
        name="test collection",
        description="description test",
        visibility="public",
        created_at="2023-01-01T00:00:00Z",
        updated_at="2023-01-01T00:00:00Z",
        documents=1,
    )
    client = ClientAlbertReel(
        "https://test.api",
        "test-key",
        indexeur_de_test,
        un_executeur_de_requete([une_reponse_de_creation_de_collection_OK(collection)]),
    )
    client.cree_collection("test", "description")

    documents = [DocumentPDF("test.pdf", "http://example.com/test.pdf")]
    client.ajoute_documents(documents)

    assert indexeur_de_test.documents_recus == documents
    assert indexeur_de_test.collection_recue == "id-collection"
