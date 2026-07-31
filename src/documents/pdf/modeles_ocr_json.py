from dataclasses import dataclass
from enum import StrEnum

from documents.page import ContexteDuBloc

class TypeDeBlocOcr(StrEnum):
    TITRE = "titre"
    RECOMMANDATION = "recommandation"
    PARAGRAPHE = "paragraphe"
    LISTE = "liste"
    TABLEAU = "tableau"
    TABLE_DES_MATIERES = "table_des_matieres"
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
class BlocIndexable:
    texte: str
    page_debut: int
    page_fin: int
    pages_couvertes: tuple[int, ...]
    contexte: ContexteDuBloc
