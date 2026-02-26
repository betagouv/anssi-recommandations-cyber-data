from pathlib import Path
from typing import Optional, cast

from documents.document import PagePDF
from documents.indexeur import DocumentAIndexer


class DocumentPDF(DocumentAIndexer):
    def __init__(self, chemin_pdf: str, url_pdf: str):
        super().__init__()
        self.url_pdf = url_pdf
        self.chemin_pdf = chemin_pdf
        self._type = "PDF"

    def initie_page(self, numero_page: Optional[int] = None):
        return PagePDF(numero_page=cast(int, numero_page))

    @property
    def nom_document(self) -> str:
        return Path(self.chemin_pdf).name

    @property
    def url(self) -> str:
        return self.url_pdf

    @property
    def chemin(self) -> str:
        return self.chemin_pdf
