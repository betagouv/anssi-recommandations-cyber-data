import glob
import json
from pathlib import Path
from typing import Literal, TypedDict, Optional

from configuration import MSC, recupere_configuration
from documents.html.document_html import DocumentHTML, DocumentReponsesMaitrisees
from documents.indexeur.indexeur import DocumentAIndexer
from documents.pdf.cree_document_pdf import cree_document_pdf, cree_document_pdf_distant
from documents.pdf.document_pdf import DocumentPDF


class URLDocument(TypedDict):
    type: Literal["PDF", "HTML"]
    url: str
    chemin: Optional[str]


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


def mappe_en_document_distant(documents_distants: Path) -> DocumentDistant | None:
    if documents_distants.exists():

        def _mappe(document: dict) -> URLDocument | dict:
            if "url" in document and "type" in document:
                chemin = None
                if "chemin" in document:
                    chemin = document["chemin"]
                return URLDocument(
                    type=document["type"], url=document["url"], chemin=chemin
                )
            return document

        contenu: DocumentDistant = json.loads(
            documents_distants.read_text(encoding="utf-8"),
            object_hook=_mappe,
        )
        return contenu
    return None


def collecte_document_maitrise(chemin: Path) -> DocumentReponsesMaitrisees:
    return DocumentReponsesMaitrisees(chemin.stem, chemin=str(chemin))


def collecte_documents_distants(
    documents_distants: DocumentDistant,
) -> list[DocumentAIndexer]:
    resultat: list[DocumentAIndexer] = []
    for nom, document_distant in documents_distants.items():
        if document_distant["type"] == "PDF":
            resultat.append(cree_document_pdf_distant(nom, document_distant["url"]))
        if document_distant["type"] == "HTML":
            resultat.append(
                DocumentHTML(
                    nom,
                    document_distant["url"],
                    document_distant["chemin"]
                    if "chemin" in document_distant
                    else None,
                )
            )
    return resultat
