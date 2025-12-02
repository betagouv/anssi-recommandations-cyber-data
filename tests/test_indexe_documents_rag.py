import tempfile
import os
from indexe_documents_rag import ClientAlbert, DocumentPDF, collecte_documents_pdf


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
