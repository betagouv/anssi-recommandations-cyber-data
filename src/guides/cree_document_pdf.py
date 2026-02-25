import unicodedata
from pathlib import Path
from urllib.parse import quote

from configuration import MSC
from guides.indexeur import DocumentPDF


def cree_document_pdf(chemin: str, configuration_msc: MSC) -> DocumentPDF:
    base = configuration_msc.url.rstrip("/")
    chemin_guides = configuration_msc.chemin_guides.strip("/")
    nom_fichier = Path(chemin).name
    nom_fichier = unicodedata.normalize("NFC", nom_fichier)
    nom_fichier_encode = quote(nom_fichier, safe="-._~")
    url = f"{base}/{chemin_guides}/{nom_fichier_encode}"
    return DocumentPDF(chemin, url)
