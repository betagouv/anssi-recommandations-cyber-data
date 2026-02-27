import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import NamedTuple, Callable, TypeVar, Generic


T_Bloc = TypeVar("T_Bloc", bound="BlocPage")


class Position(NamedTuple):
    x: float
    y: float
    largeur: float
    hauteur: float


@dataclass(frozen=True)
class BlocPage:
    texte: str


@dataclass(frozen=True)
class BlocPagePDF(BlocPage):
    position: Position


@dataclass
class Page(ABC, Generic[T_Bloc]):
    numero_page: int
    blocs: list[T_Bloc] = field(default_factory=list)

    @abstractmethod
    def ajoute_bloc(self, bloc: T_Bloc) -> None:
        pass

    @abstractmethod
    def supprime_bloc(self, bloc: T_Bloc) -> None:
        pass


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

    def supprime_bloc(self, bloc: BlocPagePDF) -> None:
        bloc_a_supprimer = None
        for b in self.blocs:
            if b.texte == bloc.texte and b.position == bloc.position:
                bloc_a_supprimer = b
                break

        if bloc_a_supprimer is None:
            raise ValueError("Bloc non trouvé")

        self.blocs.remove(bloc_a_supprimer)
        for i, b in enumerate(self.blocs):
            nouveau_bloc = BlocPagePDF(texte=b.texte, position=b.position)
            self.blocs[i] = nouveau_bloc

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


class Document:
    def __init__(self, nom_document, url):
        super().__init__()
        self._nom_document = nom_document
        self._url = url
        self.pages: dict[int, Page] = {}

    @property
    def nom_document(self):
        return self._nom_document

    @property
    def url(self):
        return self._url

    def ajoute(
        self,
        generateur: Callable[
            [],
            tuple[
                int,
                Callable[[], Page],
                Callable[[], BlocPagePDF],
            ],
        ],
    ) -> None:
        (numero_page, cree_page, cree_bloc) = generateur()
        if self.pages.get(numero_page) is None:
            self.pages[numero_page] = cree_page()
        else:
            self.pages[numero_page].ajoute_bloc(cree_bloc())

    def metatada(self, page) -> dict:
        return {
            "source_url": self.url,
            "page": page.numero_page,
            "nom_document": self.nom_document,
        }
