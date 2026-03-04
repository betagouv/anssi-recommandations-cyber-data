import unicodedata
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from configuration import MSC
from documents.pdf.document_pdf import DocumentPDF, DocumentPDFDistant


def cree_document_pdf(
    chemin: str,
    configuration_msc: MSC,
    _fichier_urls_specifiques: Optional[str] | None = None,
) -> DocumentPDF:
    base = configuration_msc.url.rstrip("/")
    chemin_guides = configuration_msc.chemin_guides.strip("/")
    nom_fichier = Path(chemin).name
    nom_fichier = unicodedata.normalize("NFC", nom_fichier)
    nom_fichier_encode = quote(nom_fichier, safe="-._~")
    url = f"{base}/{chemin_guides}/{nom_fichier_encode}"
    return DocumentPDF(chemin, url)


def cree_document_pdf_distant(nom, url: str) -> DocumentPDFDistant:
    return DocumentPDFDistant(nom, url)
