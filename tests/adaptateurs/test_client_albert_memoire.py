from adaptateurs.client_albert_memoire import ClientAlbertMemoire
from guides.indexeur_albert import IndexeurBaseVectorielleAlbert
from guides.indexeur import DocumentPDF


def test_client_albert_memoire_initialise_correctement():
    url = "https://test.api"

    client = ClientAlbertMemoire(url, "test-key", IndexeurBaseVectorielleAlbert(url))

    assert isinstance(client, ClientAlbertMemoire)
    assert str(client.client_openai.base_url) == "https://test.api"
    assert client.session.headers["Authorization"] == "Bearer test-key"
    assert client.id_collection is None


def test_client_albert_memoire_cree_collection():
    url = "https://test.api"

    client = ClientAlbertMemoire(url, "test-key", IndexeurBaseVectorielleAlbert(url))

    reponse = client.cree_collection("test collection", "description test")

    assert client.id_collection == "mem-0"
    assert reponse.id == "mem-0"
    assert reponse.name == "test collection"


def test_attribue_id_a_un_client_albert_memoire():
    client = ClientAlbertMemoire(
        "https://test.api",
        "test-key",
        IndexeurBaseVectorielleAlbert("https://test.api"),
    )
    id_collection = "collection-123"
    client.collections_existantes.add(id_collection)

    result = client.attribue_collection(id_collection)

    assert result is True
    assert client.id_collection == id_collection


def test_client_albert_memoire_verifie_collection_existe():
    client = ClientAlbertMemoire(
        "https://test.api",
        "test-key",
        IndexeurBaseVectorielleAlbert("https://test.api"),
    )
    client.collections_existantes = {"collection-123"}

    result = client.attribue_collection("collection-123")

    assert result is True
    assert client.id_collection == "collection-123"


def test_client_albert_memoire_ajoute_documents():

    client = ClientAlbertMemoire(
        "https://test.api",
        "test-key",
        IndexeurBaseVectorielleAlbert("https://test.api"),
    )
    client.cree_collection("test", "description")

    documents = [DocumentPDF("test.pdf", "http://example.com/test.pdf")]
    client.ajoute_documents(documents)

    assert client.id_collection in client.documents_par_collection
    assert len(client.documents_par_collection[client.id_collection]) == 1
    assert (
        client.documents_par_collection[client.id_collection][0].chemin_pdf
        == "test.pdf"
    )


def test_attribue_collection_inexistante_retourne_false():
    client = ClientAlbertMemoire(
        "https://test.api",
        "test-key",
        IndexeurBaseVectorielleAlbert("https://test.api"),
    )

    result = client.attribue_collection("collection-inexistante")

    assert result is False
    assert client.id_collection is None
