import json
import unicodedata
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from configuration import MSC
from documents.indexeur import DocumentPDF


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
            contenu = json.loads(chemin_json.read_text(encoding="utf-8"))
            url = contenu.get(nom_fichier)
    return DocumentPDF(chemin, url)
