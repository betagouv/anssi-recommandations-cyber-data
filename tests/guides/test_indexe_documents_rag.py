from pathlib import Path

from configuration import MSC
from guides.indexe_documents_rag import (
    collecte_documents_pdf,
    collecte_document_pdf,
)
from guides.indexeur import DocumentPDF


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
        == "https://messervices.cyber.gouv.fr/documents-guides/test.pdf"
    )


def test_ajoute_l_url_vers_msc_lors_de_la_collecte(dossier_guide_anssi):
    chemin_fichier = str(dossier_guide_anssi.resolve())

    documents = collecte_documents_pdf(
        chemin_fichier, MSC(url="http://msc.local", chemin_guides="documents-guides")
    )

    assert documents[0].url_pdf == "http://msc.local/documents-guides/test.pdf"


def test_collecte_document_pdf_retourne_un_document(dossier_guide_anssi):
    chemin_fichier = str(dossier_guide_anssi.resolve())

    document = collecte_document_pdf(chemin_fichier)

    assert isinstance(document, DocumentPDF)
    assert document.chemin_pdf == str((Path(chemin_fichier) / "test.pdf").resolve())
    assert (
        document.url_pdf
        == "https://messervices.cyber.gouv.fr/documents-guides/test.pdf"
    )
