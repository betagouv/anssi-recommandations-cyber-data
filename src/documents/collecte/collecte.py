import glob
from typing import Literal, TypedDict

from configuration import MSC, recupere_configuration
from documents.html.document_html import DocumentHTML
from documents.indexeur import DocumentAIndexer
from documents.pdf.cree_document_pdf import cree_document_pdf, cree_document_pdf_distant
from documents.pdf.document_pdf import DocumentPDF


class URLDocument(TypedDict):
    type: Literal["PDF", "HTML"]
    url: str


type DocumentDistant = dict[str, URLDocument]


def collecte_guides_anssi(
    dossier: str = "donnees/guides_de_lANSSI",
    configuration_msc: MSC = recupere_configuration().msc,
) -> list[DocumentPDF]:
    chemins = glob.glob(f"{dossier}/*.pdf")
    return [cree_document_pdf(chemin, configuration_msc) for chemin in chemins]


def collecte_guide_anssi(
    path: str = "donnees/guides_de_lANSSI",
    configuration_msc: MSC = recupere_configuration().msc,
) -> DocumentPDF:
    return cree_document_pdf(path, configuration_msc)


def collecte_documents_distants(
    documents_distants: DocumentDistant,
) -> list[DocumentAIndexer]:
    resultat: list[DocumentAIndexer] = []
    for nom, document_distant in documents_distants.items():
        if document_distant["type"] == "PDF":
            resultat.append(cree_document_pdf_distant(nom, document_distant["url"]))
        if document_distant["type"] == "HTML":
            resultat.append(DocumentHTML(nom, document_distant["url"]))
    return resultat
