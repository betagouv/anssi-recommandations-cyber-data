import re
from dataclasses import dataclass
from pathlib import Path
from typing import cast, NamedTuple

from docling_core.transforms.chunker import BaseChunk, DocMeta

from documents.extrais_les_chunks import ElementsFiltres, extrais_les_chunks
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
from documents.page import Page, BlocPage


class GenerateurDePagesPDF(GenerateurDePages):
    def genere(self, elements_filtres: ElementsFiltres) -> dict[int, Page]:
        resultat: dict[int, Page] = {}

        for chunk in extrais_les_chunks(elements_filtres):
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
    def chemin(self) -> Path:
        return Path(self.chemin_pdf)

    @property
    def generateur(self) -> GenerateurDePages:
        return GenerateurDePagesPDF()


class Position(NamedTuple):
    x: float
    y: float
    largeur: float
    hauteur: float


def extrais_position(chunk: BaseChunk) -> Position:
    try:
        meta = cast(DocMeta, chunk.meta)
        bbox = meta.doc_items[0].prov[0].bbox
        return Position(
            x=float(bbox.l),
            y=float(bbox.t),
            largeur=float(bbox.r - bbox.l),
            hauteur=float(bbox.b - bbox.t),
        )
    except Exception:
        return Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0)


@dataclass(frozen=True)
class BlocPagePDF(BlocPage):
    position: Position


class PagePDF(Page[BlocPagePDF]):
    def ajoute_bloc(self, bloc: BlocPagePDF) -> None:
        les_positions = [bloc.position for bloc in self.blocs]
        les_positions.append(bloc.position)
        les_positions_ordonnees = [
            pos
            for idx, pos in sorted(enumerate(les_positions), key=lambda it: -it[1].y)
        ]
        for indice, position in enumerate(les_positions_ordonnees):
            if bloc.position == position:
                self.blocs.insert(
                    indice, BlocPagePDF(texte=bloc.texte, position=bloc.position)
                )

        self._fusionne_les_entetes_avec_leur_contenu()

    def _fusionne_les_entetes_avec_leur_contenu(self):
        i = 0
        blocs_fusionnes = []
        while i < len(self.blocs):
            courant = self.blocs[i]
            suivant = self.blocs[i + 1] if i + 1 < len(self.blocs) else None
            if self._a_du_contenu_adjacent_au_titre(courant, suivant):
                blocs_fusionnes.append(
                    BlocPagePDF(
                        texte=f"{courant.texte}\n{suivant.texte}",
                        position=courant.position,
                    )
                )
                i += 1
            elif self._a_du_contenu_adjacent_au_sous_titre(courant, suivant):
                blocs_fusionnes.append(
                    BlocPagePDF(
                        texte=f"{courant.texte}\n{suivant.texte}",
                        position=courant.position,
                    )
                )
                i += 1
            else:
                blocs_fusionnes.append(courant)
            i += 1

        self.blocs = blocs_fusionnes

    def _a_du_contenu_adjacent_au_titre(
        self, courant: BlocPagePDF, suivant: BlocPagePDF | None
    ) -> bool:
        return self.a_du_contenu_adjacent(courant, "[TITRE]", suivant)

    def _a_du_contenu_adjacent_au_sous_titre(
        self, courant: BlocPagePDF, suivant: BlocPagePDF | None
    ) -> bool:
        return self.a_du_contenu_adjacent(courant, "[SOUS-TITRE]", suivant)

    def a_du_contenu_adjacent(
        self, courant: BlocPagePDF, sous_titre_: str, suivant: BlocPagePDF | None
    ) -> bool:
        return (
            courant.texte.startswith(sous_titre_)
            and suivant is not None
            and (
                suivant.texte.startswith("[TEXTE]")
                or suivant.texte.startswith("[RECOMMANDATION]")
                or suivant.texte.startswith("[TABLEAU]")
            )
        )

    @staticmethod
    def _est_entete(texte: str) -> bool:
        t = (texte or "").strip()
        if not t:
            return False
        if t.endswith((".", "…", "!", "?")):
            return False
        tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", t)
        if not (1 <= len(tokens) <= 6):
            return False
        if len(t) > 60:
            return False
        return True
