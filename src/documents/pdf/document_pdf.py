from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple, Union, Optional

from docling_core.types import DoclingDocument
from docling_core.types.doc import DocItemLabel, TableItem

from documents.elements_filtres import ElementsFiltres
from documents.generateur_de_pages import GenerateurDePages
from documents.indexeur.indexeur import DocumentAIndexer
from documents.page import Page, BlocPage


class GenerateurDePagesPDF(GenerateurDePages):
    def genere(
        self, elements_filtres: ElementsFiltres, document: Optional[DoclingDocument]
    ) -> dict[int, Page]:
        resultat: dict[int, Page] = {}
        bloc_lignes: list[str] = []
        bloc_page: int = 1
        dernier_group_ref: str | None = None
        precedent_etait_header: bool = False
        def _ajoute_bloc_a_la_page() -> None:
            if not bloc_lignes:
                return
            page = resultat.setdefault(bloc_page, PagePDF(bloc_page))
            page.ajoute_bloc(
                BlocPagePDF(
                    texte="\n".join(bloc_lignes),
                    numero_page=bloc_page,
                )
            )

        for element in elements_filtres:
            if element.label == DocItemLabel.PAGE_FOOTER:  # type: ignore[union-attr]
                continue

            numero_page = element.prov[0].page_no if element.prov else bloc_page  # type: ignore[union-attr]
            est_header = element.label in (  # type: ignore[union-attr]
                DocItemLabel.SECTION_HEADER,
                DocItemLabel.TITLE,
            )

            if est_header:
                _ajoute_bloc_a_la_page()
                bloc_lignes = [element.text]  # type: ignore[union-attr]
                bloc_page = numero_page
                dernier_group_ref = None
                precedent_etait_header = True
            else:
                est_element_liste = element.label == DocItemLabel.LIST_ITEM  # type: ignore[union-attr]
                if est_element_liste:
                    parent_ref = element.parent.cref if element.parent else None  # type: ignore[union-attr]
                    if (
                        parent_ref != dernier_group_ref
                        and not precedent_etait_header
                        and dernier_group_ref is not None
                    ):
                        _ajoute_bloc_a_la_page()
                        bloc_lignes = []
                        bloc_page = numero_page
                    dernier_group_ref = parent_ref

                if isinstance(element, TableItem):
                    bloc_lignes.append(element.export_to_markdown(document))
                else:
                    bloc_lignes.append(getattr(element, "text", "") or "")
                precedent_etait_header = False

        _ajoute_bloc_a_la_page()

        if not resultat:
            resultat[1] = PagePDF(1)
        return resultat


class DocumentPDF(DocumentAIndexer):
    def __init__(self, chemin_pdf: str, url_pdf: str):
        super().__init__()
        self._url_pdf = url_pdf
        self._chemin_pdf = chemin_pdf
        self._type = "PDF"

    @property
    def nom_document(self) -> str:
        return Path(self._chemin_pdf).name

    @property
    def url(self) -> str:
        return self._url_pdf

    @property
    def chemin(self) -> Path:
        return Path(self._chemin_pdf)

    @property
    def generateur(self) -> GenerateurDePages:
        return GenerateurDePagesPDF()


class DocumentPDFDistant(DocumentAIndexer):
    def __init__(self, nom: str, url: str):
        super().__init__()
        self._url_pdf = url
        self._nom_document = nom
        self._type = "PDF"

    @property
    def nom_document(self) -> str:
        return self._nom_document

    @property
    def url(self) -> str:
        return self._url_pdf

    @property
    def chemin(self) -> Union[Path, str]:
        return self._url_pdf

    @property
    def generateur(self) -> GenerateurDePages:
        return GenerateurDePagesPDF()


class Position(NamedTuple):
    x: float
    y: float
    largeur: float
    hauteur: float


@dataclass(frozen=True)
class BlocPagePDF(BlocPage):
    pass


class PagePDF(Page[BlocPagePDF]):
    def ajoute_bloc(self, bloc: BlocPagePDF) -> None:
        self.blocs.append(bloc)
