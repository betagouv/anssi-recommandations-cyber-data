from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from docling_core.types.doc import DocItemLabel, TableItem, SectionHeaderItem

from documents.elements_filtres import ElementsFiltres
from documents.generateur_de_pages import GenerateurDePages
from documents.indexeur.indexeur import DocumentAIndexer
from documents.page import BlocPage, Page


@dataclass(frozen=True)
class BlocPageHTML(BlocPage):
    numero_page: int = 0


class PageHTML(Page):
    def __init__(self, blocs: Optional[list[BlocPageHTML]] = None):
        super().__init__(numero_page=None, blocs=blocs if blocs is not None else [])

    def ajoute_bloc(self, bloc: BlocPage) -> None:
        self.blocs.append(bloc)


class GenerateurDePagesHTML(GenerateurDePages):
    def genere(self, elements_filtres: ElementsFiltres) -> dict[int, Page]:
        page = PageHTML()
        les_headers: list[SectionHeaderItem] = list(
            filter(
                lambda item: item.label == DocItemLabel.SECTION_HEADER  # type: ignore[arg-type]
                or item.label == DocItemLabel.TITLE,
                elements_filtres,
            )
        )
        if len(les_headers) == 0:
            page.ajoute_bloc(
                BlocPageHTML(texte=self.__extrais_contenu_textuel(elements_filtres))
            )
        for header in les_headers:
            les_references_enfants = list(map(lambda item: item.cref, header.children))
            les_enfants = list(
                filter(
                    lambda item: item.self_ref in les_references_enfants,
                    elements_filtres,
                )
            )
            page.ajoute_bloc(
                BlocPageHTML(
                    texte=f"{header.text}\n{self.__extrais_contenu_textuel(les_enfants)}"
                )
            )
        return {0: page}

    def __extrais_contenu_textuel(self, elements_filtres: ElementsFiltres) -> str:
        les_tableaux: list[TableItem] = list(
            filter(lambda item: isinstance(item, TableItem), elements_filtres)  # type: ignore[arg-type]
        )
        if len(les_tableaux) > 0:
            return "\n".join(map(lambda item: item.export_to_markdown(), les_tableaux))
        return "\n".join(map(lambda element: element.text, elements_filtres))  # type: ignore[union-attr]


class DocumentHTML(DocumentAIndexer):
    def __init__(self, nom_document: str, url: str, chemin: Optional[str] = None):
        super().__init__()
        self._url = url
        self._chemin = chemin
        self._nom_document = nom_document
        self._type = "HTML"

    @property
    def nom_document(self) -> str:
        return self._nom_document

    @property
    def url(self) -> str:
        return self._url

    @property
    def chemin(self) -> Path | str:
        if self._chemin is not None:
            return Path(self._chemin)
        return self._url

    @property
    def generateur(self) -> GenerateurDePages:
        return GenerateurDePagesHTML()
