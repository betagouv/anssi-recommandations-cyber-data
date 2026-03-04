import json
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
    fichier_urls_specifiques: Optional[str] | None = None,
) -> DocumentPDF:
    base = configuration_msc.url.rstrip("/")
    chemin_guides = configuration_msc.chemin_guides.strip("/")
    nom_fichier = Path(chemin).name
    nom_fichier = unicodedata.normalize("NFC", nom_fichier)
    nom_fichier_encode = quote(nom_fichier, safe="-._~")
    url = f"{base}/{chemin_guides}/{nom_fichier_encode}"
    if fichier_urls_specifiques:
        chemin_json = Path(fichier_urls_specifiques)
        if chemin_json.exists():

            def as_url_document(d: dict) -> URLDocument | dict:
                if "url" in d and "type" in d:
                    return URLDocument(**d)
                return d

            contenu: DocumentDistant = json.loads(
                chemin_json.read_text(encoding="utf-8"),
                object_hook=as_url_document,
            )
            url = contenu[nom_fichier].url
    return DocumentPDF(chemin, url)
