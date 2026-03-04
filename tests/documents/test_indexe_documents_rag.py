from pathlib import Path

import pytest

from configuration import MSC, recupere_configuration
from documents.indexe_documents_rag import (
    collecte_guides_anssi,
)
from documents.pdf.document_pdf import DocumentPDF


def test_document_pdf_cree_correctement():
    doc = DocumentPDF("chemin/vers/fichier.pdf", "https://example.com/fichier.pdf")

    assert doc.chemin_pdf == "chemin/vers/fichier.pdf"
    assert doc.url_pdf == "https://example.com/fichier.pdf"


def test_collecte_guides_anssi_retourne_liste_documents(dossier_guide_anssi):
    chemin_fichier = str(dossier_guide_anssi.resolve())
    documents = collecte_guides_anssi(chemin_fichier)

    assert isinstance(documents, list)
    assert len(documents) == 1
    assert isinstance(documents[0], DocumentPDF)
    assert documents[0].chemin_pdf == str((Path(chemin_fichier) / "test.pdf").resolve())
    assert (
        documents[0].url_pdf
        == "https://messervices.cyber.gouv.fr/documents-guides/test.pdf"
    )


def test_ajoute_l_url_vers_msc_lors_de_la_collecte(dossier_guide_anssi):
    chemin_fichier = str(dossier_guide_anssi.resolve())

    documents = collecte_guides_anssi(
        chemin_fichier, MSC(url="http://msc.local", chemin_guides="documents-guides")
    )

    assert documents[0].url_pdf == "http://msc.local/documents-guides/test.pdf"


@pytest.mark.skip(
    reason="En attendant d’exposer une fonction spécifique pour les documents distants"
)
def test_collecte_guides_anssi_utilise_url_specifique_depuis_json(
    dossier_guide_anssi,
    fichier_urls_specifiques,
):
    chemin_dossier = str(dossier_guide_anssi.resolve())

    documents = collecte_guides_anssi(
        dossier=chemin_dossier,
        configuration_msc=recupere_configuration().msc,
        path_url=str(fichier_urls_specifiques),
    )

    assert len(documents) == 1
    assert documents[0].url_pdf == "https://url_de_test.com"
