import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Literal
from urllib.parse import quote

from configuration import MSC
from documents.pdf.document_pdf import DocumentPDF


@dataclass
class URLDocument:
    type: Literal["PDF", "HTML"]
    url: str


type DocumentDistant = dict[str, URLDocument]


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
