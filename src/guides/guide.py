import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

from guides.indexeur import DocumentPDF


class Position(NamedTuple):
    x: float
    y: float
    largeur: float
    hauteur: float


@dataclass(frozen=True)
class BlocPage:
    texte: str
    position: Position


@dataclass
class Page:
    numero_page: int
    blocs: list[BlocPage] = field(default_factory=list)

    def ajoute_bloc(self, bloc: BlocPage) -> None:
        les_positions = [bloc.position for bloc in self.blocs]
        les_positions.append(bloc.position)
        les_positions_ordonnees = [
            pos
            for idx, pos in sorted(enumerate(les_positions), key=lambda it: -it[1].y)
        ]
        for indice, position in enumerate(les_positions_ordonnees):
            if bloc.position == position:
                self.blocs.insert(
                    indice, BlocPage(texte=bloc.texte, position=bloc.position)
                )

        self._fusionne_les_entetes_avec_leur_contenu()

    def supprime_bloc(self, bloc: BlocPage) -> None:
        bloc_a_supprimer = None
        for b in self.blocs:
            if b.texte == bloc.texte and b.position == bloc.position:
                bloc_a_supprimer = b
                break

        if bloc_a_supprimer is None:
            raise ValueError("Bloc non trouvé")

        self.blocs.remove(bloc_a_supprimer)
        for i, b in enumerate(self.blocs):
            nouveau_bloc = BlocPage(texte=b.texte, position=b.position)
            self.blocs[i] = nouveau_bloc

    def _fusionne_les_entetes_avec_leur_contenu(self):
        i = 0
        blocs_fusionnes = []
        while i < len(self.blocs):
            courant = self.blocs[i]
            suivant = self.blocs[i + 1] if i + 1 < len(self.blocs) else None
            if self.a_du_contenu_adjacent_au_titre(courant, suivant):
                blocs_fusionnes.append(
                    BlocPage(
                        texte=f"{courant.texte}\n{suivant.texte}",
                        position=courant.position,
                    )
                )
                i += 1
            elif self.a_du_contenu_adjacent_au_sous_titre(courant, suivant):
                blocs_fusionnes.append(
                    BlocPage(
                        texte=f"{courant.texte}\n{suivant.texte}",
                        position=courant.position,
                    )
                )
                i += 1
            else:
                blocs_fusionnes.append(courant)
            i += 1

        self.blocs = blocs_fusionnes

    def a_du_contenu_adjacent_au_titre(
        self, courant: BlocPage, suivant: BlocPage | None
    ) -> bool:
        return self.a_du_contenu_adjacent(courant, "[TITRE]", suivant)

    def a_du_contenu_adjacent_au_sous_titre(
        self, courant: BlocPage, suivant: BlocPage | None
    ) -> bool:
        return self.a_du_contenu_adjacent(courant, "[SOUS-TITRE]", suivant)

    def a_du_contenu_adjacent(
        self, courant: BlocPage, sous_titre_: str, suivant: BlocPage | None
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


class Guide:
    def __init__(self, document: DocumentPDF):
        super().__init__()
        self.nom_document = Path(document.chemin_pdf).name
        self.pages: dict[int, Page] = {}

    def ajoute_bloc_a_la_page(
        self, numero_page: int, position: Position, texte: str
    ) -> None:
        if self.pages.get(numero_page) is None:
            page = Page(numero_page=numero_page)
            page.ajoute_bloc(BlocPage(texte=texte, position=position))
            self.pages[numero_page] = page
        else:
            self.pages[numero_page].ajoute_bloc(
                BlocPage(texte=texte, position=position)
            )
