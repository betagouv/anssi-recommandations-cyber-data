from pathlib import Path
from unittest.mock import Mock

from configuration import MSC
from guides.indexe_documents_rag import (
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


def test_collecte_documents_pdf_retourne_liste_documents(dossier_guide_anssi):
    chemin_fichier = str(dossier_guide_anssi.resolve())
    documents = collecte_documents_pdf(chemin_fichier)

    assert isinstance(documents, list)
    assert len(documents) == 1
    assert isinstance(documents[0], DocumentPDF)
    assert documents[0].chemin_pdf == str((Path(chemin_fichier) / "test.pdf").resolve())
    assert (
        documents[0].url_pdf
        == "https://demo.messervices.cyber.gouv.fr/documents-guides/test.pdf"
    )


def test_ajoute_l_url_vers_msc_lors_de_la_collecte(dossier_guide_anssi):
    chemin_fichier = str(dossier_guide_anssi.resolve())

    documents = collecte_documents_pdf(
        chemin_fichier, MSC(url="http://msc.local", chemin_guides="documents-guides")
    )

    assert documents[0].url_pdf == "http://msc.local/documents-guides/test.pdf"


def test_client_albert_cree_collection():
    client = ClientAlbert("https://test.api", "test-key")

    mock_response = Mock()
    mock_response.status_code = 201
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

    document = DocumentPDF("test.pdf", "https://example.com/test.pdf")
    reponses = client.ajoute_document(document)

    assert len(reponses) == 1
    assert reponses[0].id == "doc123"
    assert reponses[0].name == "test.pdf"
    assert reponses[0].collection_id == "12345"


def test_client_albert_ajoute_documents_avec_retry():
    client = ClientAlbert("https://test.api", "test-key")
    client.id_collection = "12345"

    mock_response_echec = Mock()
    mock_response_echec.json.side_effect = Exception("Erreur réseau")

    mock_response_succes = Mock()
    reponse_attendue = ReponseDocument(
        id="doc123",
        name="test.pdf",
        collection_id="12345",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )
    mock_response_succes.json.return_value = reponse_attendue._asdict()

    client.session.post = Mock(side_effect=[mock_response_echec, mock_response_succes])

    with open("test.pdf", "wb") as f:
        f.write(b"pdf content")

    documents = [DocumentPDF("test.pdf", "https://example.com/test.pdf")]
    reponses = client.ajoute_documents_avec_retry(documents, 3, 0.01)

    assert len(reponses) == 1
    assert reponses[0].id == "doc123"
    assert client.session.post.call_count == 2
