from pathlib import Path
from typing import cast

from docling_core.transforms.chunker import BaseChunk, DocMeta

from documents.chunker_docling import extrais_position
from documents.generateur_de_pages import (
    GenerateurDePages,
    NumeroPage,
    CreationDePage,
    CreationDeBlocPage,
)
from documents.indexeur import (
    DocumentAIndexer,
    GenerationDePage,
)
from documents.page import Position, BlocPagePDF, Page, PagePDF


class GenerateurDePagesPDF(GenerateurDePages):
    def genere(self, chunks: list[BaseChunk]) -> dict[int, Page]:
        resultat: dict[int, Page] = {}

        for chunk in chunks:
            try:
                (numero_page, cree_page, cree_bloc) = self.__genere(chunk)()
                if resultat.get(numero_page) is None:
                    resultat[numero_page] = cree_page()
                else:
                    resultat[numero_page].ajoute_bloc(cree_bloc())
            except Exception:
                continue
        return resultat

    @staticmethod
    def __genere(chunk: BaseChunk) -> GenerationDePage:
        def _cree_page(numero_page: int, texte: str, position: Position) -> Page:
            page = PagePDF(numero_page=numero_page)
            page.ajoute_bloc(BlocPagePDF(texte=texte, position=position))
            return page

        def _genere() -> tuple[NumeroPage, CreationDePage, CreationDeBlocPage]:
            numero_page = cast(DocMeta, chunk.meta).doc_items[0].prov[0].page_no
            position = extrais_position(chunk)
            return (
                numero_page,
                lambda: _cree_page(numero_page, chunk.text, position),
                lambda: BlocPagePDF(texte=chunk.text, position=position),
            )

        return _genere


class DocumentPDF(DocumentAIndexer):
    def __init__(self, chemin_pdf: str, url_pdf: str):
        super().__init__()
        self.url_pdf = url_pdf
        self.chemin_pdf = chemin_pdf
        self._type = "PDF"

    @property
    def nom_document(self) -> str:
        return Path(self.chemin_pdf).name

    @property
    def url(self) -> str:
        return self.url_pdf

    @property
    def chemin(self) -> str:
        return self.chemin_pdf

    @property
    def generateur(self) -> GenerateurDePages:
        return GenerateurDePagesPDF()
