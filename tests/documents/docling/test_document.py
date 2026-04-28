from unittest.mock import MagicMock

from documents.docling.document import Document
from documents.html.document_html import BlocPageReponse
from documents.page import BlocPage


def _un_document_a_indexer(nom="doc.pdf", url="https://example.com"):
    mock = MagicMock()
    mock.nom_document = nom
    mock.url = url
    return mock


def test_metadata_contient_reponse_maitrisee_vrai_quand_active():
    document = Document(_un_document_a_indexer(), reponse_maitrisee=True)
    bloc = BlocPage(texte="contenu", numero_page=1)

    metadata = document.metadata(bloc)

    assert metadata["reponse_maitrisee"] is True


def test_metadata_contient_id_reponse_quand_bloc_a_un_slug():
    document = Document(_un_document_a_indexer())
    bloc = BlocPageReponse(texte="Qui est le directeur ?", id_reponse="qui-est-le-directeur")

    metadata = document.metadata(bloc)

    assert metadata["id_reponse"] == "qui-est-le-directeur"
    assert "reponse" not in metadata
