from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from docling_core.types import DoclingDocument
from docling_core.types.doc import TableItem, SectionHeaderItem, TitleItem

from documents.elements_filtres import ElementsFiltres
from documents.generateur_de_pages import GenerateurDePages
from documents.html.slugifie import slugifie
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
    def genere(
        self, elements_filtres: ElementsFiltres, document: Optional[DoclingDocument]
    ) -> dict[int, Page]:
        page = PageHTML()
        les_headers: list[SectionHeaderItem | TitleItem] = [
            item
            for item in elements_filtres
            if isinstance(item, (SectionHeaderItem, TitleItem))
        ]
        if len(les_headers) == 0:
            page.ajoute_bloc(
                BlocPageHTML(
                    texte=self.__extrais_contenu_textuel(elements_filtres, document)
                )
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
                    texte=f"{header.text}\n{self.__extrais_contenu_textuel(les_enfants, document)}"
                )
            )
        return {0: page}

    def __extrais_contenu_textuel(
        self, elements_filtres: ElementsFiltres, document: Optional[DoclingDocument]
    ) -> str:
        les_tableaux: list[TableItem] = list(
            filter(lambda item: isinstance(item, TableItem), elements_filtres)  # type: ignore[arg-type]
        )
        if len(les_tableaux) > 0:
            return "\n".join(
                map(lambda item: item.export_to_markdown(document), les_tableaux)
            )
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


@dataclass(frozen=True)
class BlocPageReponse(BlocPage):
    id_reponse: str = ""
    reponse: str = ""
    numero_page: int = 0


class GenerateurReponsesMaitrisees(GenerateurDePages):
    def genere(
        self, elements_filtres: ElementsFiltres, document: Optional[DoclingDocument]
    ) -> dict[int, Page]:
        page = PageHTML()
        les_headers: list[SectionHeaderItem | TitleItem] = [
            item
            for item in elements_filtres
            if isinstance(item, (SectionHeaderItem, TitleItem))
        ]
        for header in les_headers:
            id_reponse = slugifie(header.text)
            les_references_enfants = {item.cref for item in header.children}
            les_enfants = [
                item
                for item in elements_filtres
                if item.self_ref in les_references_enfants
            ]
            reponse = "\n".join(e.text for e in les_enfants)  # type: ignore[union-attr]
            page.ajoute_bloc(
                BlocPageReponse(
                    texte=header.text, id_reponse=id_reponse, reponse=reponse
                )
            )
        return {0: page}


class DocumentReponsesMaitrisees(DocumentHTML):
    def __init__(self, nom_document: str, chemin: Optional[str] = None):
        super().__init__(nom_document, "", chemin)

    @property
    def url(self) -> str:
        return str(self.chemin)

    @property
    def generateur(self) -> GenerateurDePages:
        return GenerateurReponsesMaitrisees()
