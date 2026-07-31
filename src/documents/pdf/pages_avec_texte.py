import logging
from io import BytesIO
from pathlib import Path
from typing import Callable, Protocol, cast

import pypdfium2 as pdfium
import requests


_log = logging.getLogger(__name__)
SEUIL_CARACTERES_PAGE_VIDE = 10


class PageTextePDFLisible(Protocol):
    def get_text_bounded(self) -> str:
        ...


class PagePDFLisible(Protocol):
    def get_textpage(self) -> PageTextePDFLisible:
        ...


class DocumentPDFLisible(Protocol):
    def __len__(self) -> int:
        ...

    def __getitem__(self, numero_page: int) -> PagePDFLisible:
        ...

    def close(self) -> None:
        ...


def _regroupe_en_plages(pages_retenues: list[int]) -> list[tuple[int, int]]:
    if not pages_retenues:
        return []
    plages: list[tuple[int, int]] = []
    debut = pages_retenues[0]
    precedente = pages_retenues[0]
    for page in pages_retenues[1:]:
        if page != precedente + 1:
            plages.append((debut, precedente))
            debut = page
        precedente = page
    plages.append((debut, precedente))
    return plages


def _ouvre_le_pdf(chemin_ou_url: str) -> DocumentPDFLisible:
    chemin = Path(chemin_ou_url)
    if chemin.exists():
        return cast(DocumentPDFLisible, pdfium.PdfDocument(chemin))
    reponse = requests.get(chemin_ou_url, timeout=30)
    reponse.raise_for_status()
    return cast(
        DocumentPDFLisible,
        pdfium.PdfDocument(BytesIO(reponse.content)),
    )


def identifie_les_plages_de_pages_pdf_qui_contiennent_du_texte(
    chemin_ou_url: str,
    seuil_caracteres: int = SEUIL_CARACTERES_PAGE_VIDE,
    ouvre_pdf: Callable[[str], DocumentPDFLisible] = _ouvre_le_pdf,
) -> list[tuple[int, int]] | None:
    try:
        pdf = ouvre_pdf(chemin_ou_url)
        try:
            nombre_de_pages = len(pdf)
            pages_retenues = [
                i + 1
                for i in range(nombre_de_pages)
                if len(pdf[i].get_textpage().get_text_bounded().strip())
                >= seuil_caracteres
            ]
        finally:
            pdf.close()
    except Exception:
        _log.warning(
            "Impossible d'analyser le texte embarqué de %s, aucune page ignorée",
            chemin_ou_url,
            exc_info=True,
        )
        return None

    if len(pages_retenues) == nombre_de_pages:
        return None

    return _regroupe_en_plages(pages_retenues)
