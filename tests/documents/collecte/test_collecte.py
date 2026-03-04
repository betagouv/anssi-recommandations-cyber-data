from pathlib import Path

from configuration import MSC
from documents.collecte.collecte import (
    collecte_guides_anssi,
    collecte_guide_anssi,
    collecte_documents_distants,
)
from documents.html.document_html import GenerateurDePagesHTML
from documents.pdf.document_pdf import DocumentPDF, GenerateurDePagesPDF


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


def test_collecte_guide_anssi_retourne_un_document(dossier_guide_anssi):
    chemin_fichier = str(dossier_guide_anssi.resolve() / "test.pdf")

    document = collecte_guide_anssi(chemin_fichier)
    print(document)
    assert isinstance(document, DocumentPDF)
    assert document.chemin_pdf == chemin_fichier
    assert (
        document.url_pdf
        == "https://messervices.cyber.gouv.fr/documents-guides/test.pdf"
    )


def test_collecte_un_document_distant():
    documents = collecte_documents_distants(
        {"test.pdf": {"type": "PDF", "url": "https://un-pdf-distant.local/test.pdf"}}
    )

    assert documents[0].type == "PDF"
    assert documents[0].nom_document == "test.pdf"
    assert documents[0].url == "https://un-pdf-distant.local/test.pdf"
    assert documents[0].chemin == "https://un-pdf-distant.local/test.pdf"
    assert isinstance(documents[0].generateur, GenerateurDePagesPDF)


def test_collecte_un_document_distant_de_type_html():
    documents = collecte_documents_distants(
        {
            "Ma page": {
                "type": "HTML",
                "url": "https://une-page-distante.local/index.html",
            }
        }
    )

    assert documents[0].type == "HTML"
    assert documents[0].nom_document == "Ma page"
    assert documents[0].url == "https://une-page-distante.local/index.html"
    assert documents[0].chemin == "https://une-page-distante.local/index.html"
    assert isinstance(documents[0].generateur, GenerateurDePagesHTML)
