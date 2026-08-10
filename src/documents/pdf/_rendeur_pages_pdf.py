from __future__ import annotations

import base64
from io import BytesIO
from pathlib import Path
from typing import Protocol

import pypdfium2
import requests


ECHELLE_DE_RENDU_OCR = 3.0


class RendeurDePagesPdf(Protocol):
    def nombre_de_pages(self, chemin: str | Path) -> int:
        ...

    def encode_l_image(self, chemin: str | Path, numero_page: int) -> str:
        ...


class RendeurDePagesPdfPypdfium2:
    def nombre_de_pages(self, chemin: str | Path) -> int:
        document_pdf = self._ouvre_le_pdf(chemin)
        try:
            return len(document_pdf)
        finally:
            document_pdf.close()

    def encode_l_image(self, chemin: str | Path, numero_page: int) -> str:
        document_pdf = self._ouvre_le_pdf(chemin)
        try:
            image = document_pdf[numero_page - 1].render(
                scale=ECHELLE_DE_RENDU_OCR
            ).to_pil()
            with BytesIO() as flux:
                image.save(flux, format="PNG")
                return base64.b64encode(flux.getvalue()).decode("ascii")
        finally:
            document_pdf.close()

    @staticmethod
    def _ouvre_le_pdf(chemin: str | Path):
        chemin_pdf = Path(chemin)
        if chemin_pdf.exists():
            return pypdfium2.PdfDocument(chemin_pdf)
        reponse = requests.get(str(chemin), timeout=30)
        reponse.raise_for_status()
        return pypdfium2.PdfDocument(BytesIO(reponse.content))
