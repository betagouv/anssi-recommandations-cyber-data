from dataclasses import dataclass
from enum import StrEnum


class TypeDeBlocOcr(StrEnum):
    TITRE = "titre"
    RECOMMANDATION = "recommandation"
    PARAGRAPHE = "paragraphe"
    LISTE = "liste"
    TABLEAU = "tableau"
    AUTRE = "autre"
    PIED_DE_PAGE = "pied_de_page"


@dataclass(frozen=True)
class BlocOcr:
    type_de_bloc: TypeDeBlocOcr
    code: str | None
    titre: str | None
    texte: str
    niveau: int | None = None
    est_une_continuation: bool = False
    elements_de_liste: tuple[str, ...] = ()
    lignes_de_tableau: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True)
class PageOcr:
    numero_page: int
    blocs: tuple[BlocOcr, ...]


@dataclass(frozen=True)
class ResultatOcrPdf:
    nombre_de_pages: int
    pages: tuple[PageOcr, ...]


@dataclass(frozen=True)
class ContexteDuBloc:
    type_de_bloc: str | None = None
    code_recommandation: str | None = None
    titre: str | None = None
    section: str | None = None
    chemin_des_sections: tuple[str, ...] = ()
    niveau: int | None = None


@dataclass(frozen=True)
class BlocIndexable:
    texte: str
    page_debut: int
    page_fin: int
    pages_couvertes: tuple[int, ...]
    contexte: ContexteDuBloc


class AssembleurDeBlocsJson:
    def assemble(self, resultat_ocr: ResultatOcrPdf) -> list[BlocIndexable]:
        return [
            BlocIndexable(
                texte=bloc.texte,
                page_debut=page.numero_page,
                page_fin=page.numero_page,
                pages_couvertes=(page.numero_page,),
                contexte=ContexteDuBloc(
                    type_de_bloc=bloc.type_de_bloc.value,
                    code_recommandation=bloc.code,
                    titre=bloc.titre,
                    niveau=bloc.niveau,
                ),
            )
            for page in resultat_ocr.pages
            for bloc in page.blocs
        ]
