import tempfile
import os
from unittest.mock import Mock
from indexe_documents_rag import (
    ClientAlbert,
    DocumentPDF,
    collecte_documents_pdf,
    ReponseDocument,
)


def test_client_albert_initialise_correctement():
    client = ClientAlbert("https://test.api", "test-key")

    assert isinstance(client, ClientAlbert)
    assert str(client.client_openai.base_url) == "https://test.api"
    assert client.session.headers["Authorization"] == "Bearer test-key"
    assert client.id_collection is None


def test_document_pdf_cree_correctement():
    doc = DocumentPDF("chemin/vers/fichier.pdf", "https://example.com/fichier.pdf")

    assert doc.chemin_pdf == "chemin/vers/fichier.pdf"
    assert doc.url_pdf == "https://example.com/fichier.pdf"


def test_collecte_documents_pdf_retourne_liste_documents():
    with tempfile.TemporaryDirectory() as temp_dir:
        test_pdf = os.path.join(temp_dir, "test.pdf")
        with open(test_pdf, "wb") as f:
            f.write(b"pdf content")

        documents = collecte_documents_pdf(temp_dir)

        assert isinstance(documents, list)
        assert len(documents) == 1
        assert isinstance(documents[0], DocumentPDF)
        assert documents[0].chemin_pdf == test_pdf
        assert (
            documents[0].url_pdf
            == "https://demo.messervices.cyber.gouv.fr/documents-guides/test.pdf"
        )


def test_client_albert_cree_collection():
    client = ClientAlbert("https://test.api", "test-key")

    mock_response = Mock()
    mock_response.json.return_value = {
        "id": "12345",
        "name": "test collection",
        "description": "description test",
        "visibility": "private",
        "documents": 0,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }
    client.session.post = Mock(return_value=mock_response)

    reponse = client.cree_collection("test collection", "description test")

    assert client.id_collection == "12345"
    assert reponse.id == "12345"
    assert reponse.name == "test collection"


def test_client_albert_ajoute_documents():
    client = ClientAlbert("https://test.api", "test-key")
    client.id_collection = "12345"

    mock_response = Mock()
    reponse_attendue = ReponseDocument(
        id="doc123",
        name="test.pdf",
        collection_id="12345",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )
    mock_response.json.return_value = reponse_attendue._asdict()
    client.session.post = Mock(return_value=mock_response)

    with open("test.pdf", "wb") as f:
        f.write(b"pdf content")

    documents = [DocumentPDF("test.pdf", "https://example.com/test.pdf")]
    reponses = client.ajoute_documents(documents)

    assert len(reponses) == 1
    assert reponses[0].id == "doc123"
    assert reponses[0].name == "test.pdf"
    assert reponses[0].collection_id == "12345"
