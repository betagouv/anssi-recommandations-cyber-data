import re
from copy import copy
from dataclasses import dataclass, field
from typing import NamedTuple


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
        blocs_fusionnes: list[BlocPage] = copy(self.blocs)  # type: ignore [annotation-unchecked]
        while i < len(self.blocs):
            courant = self.blocs[i]
            if (
                self._est_entete(courant.texte)
                and i + 1 < len(self.blocs)
                and not self._est_entete(self.blocs[i + 1].texte)
            ):
                suivant = self.blocs[i + 1]

                if suivant.texte.startswith(courant.texte):
                    blocs_fusionnes[i] = BlocPage(
                        texte=suivant.texte, position=courant.position
                    )
                else:
                    blocs_fusionnes[i] = BlocPage(
                        texte=f"{courant.texte}\n{suivant.texte}",
                        position=courant.position,
                    )
                blocs_fusionnes.pop(i + 1)
            i += 1
        self.blocs = blocs_fusionnes

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


@dataclass
class Guide:
    pages: dict[int, Page] = field(default_factory=dict)

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
