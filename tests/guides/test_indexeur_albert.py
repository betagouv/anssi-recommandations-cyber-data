from unittest.mock import Mock

from guides.indexeur import ReponseDocument, DocumentPDF
from guides.indexeur_albert import IndexeurBaseVectorielleAlbert


def test_indexeur_base_vectorielle_albert_ajoute_documents(fichier_pdf):
    chemin_fichier_de_test = str(fichier_pdf("test.pdf").resolve())
    indexeur = IndexeurBaseVectorielleAlbert("https://test.api")
    mock_response = Mock()
    reponse_attendue = ReponseDocument(
        id="doc123",
        name="test.pdf",
        collection_id="12345",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )
    mock_response.json.return_value = reponse_attendue._asdict()
    indexeur.session.post = Mock(return_value=mock_response)

    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")
    reponses = indexeur.ajoute_documents([document], "12345")

    assert len(reponses) == 1
    assert reponses[0].id == "doc123"
    assert reponses[0].name == "test.pdf"
    assert reponses[0].collection_id == "12345"


def test_client_albert_ajoute_documents_avec_retry(fichier_pdf):
    chemin_fichier_de_test = str(fichier_pdf("test.pdf").resolve())
    indexeur = IndexeurBaseVectorielleAlbert("https://test.api")
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
    indexeur.session.post = Mock(
        side_effect=[mock_response_echec, mock_response_succes]
    )

    documents = [DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")]
    reponses = indexeur.ajoute_documents(documents, "12345")

    assert len(reponses) == 1
    assert reponses[0].id == "doc123"
    assert indexeur.session.post.call_count == 2


def test_client_albert_ajoute_documents_avec_2_tentatives_en_echec_pour_un_nombre_de_tentatives_a_2(
    fichier_pdf,
):
    chemin_fichier_test_en_echec = str(fichier_pdf("test_en_echec.pdf").resolve())
    chemin_fichier_test_en_succes = str(fichier_pdf("test_en_succes.pdf").resolve())
    indexeur = IndexeurBaseVectorielleAlbert("https://test.api", 2, 0.01)
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
    indexeur.session.post = Mock(
        side_effect=[mock_response_echec, mock_response_echec, mock_response_succes]
    )

    documents = [
        DocumentPDF(
            chemin_fichier_test_en_echec, "https://example.com/test_en_echec.pdf"
        ),
        DocumentPDF(
            chemin_fichier_test_en_succes, "https://example.com/test_en_succes.pdf"
        ),
    ]
    reponses = indexeur.ajoute_documents(documents, "12345")

    assert len(reponses) == 1
    assert reponses[0].id == "doc123"
    assert indexeur.session.post.call_count == 3
