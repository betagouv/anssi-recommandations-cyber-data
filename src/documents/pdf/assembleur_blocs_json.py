import re
from dataclasses import dataclass, replace
from enum import StrEnum


class TypeDeBlocOcr(StrEnum):
    TITRE = "heading"
    RECOMMANDATION = "recommendation"
    PARAGRAPHE = "paragraph"
    LISTE = "list"
    TABLEAU = "table"
    AUTRE = "other"
    PIED_DE_PAGE = "footer"


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
    est_decoratif: bool = False


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


@dataclass
class _TitreEnAttente:
    texte: str
    niveau: int | None
    page: int
    chemin_des_sections: tuple[str, ...]


class AssembleurDeBlocsJson:
    def assemble(self, resultat_ocr: ResultatOcrPdf) -> list[BlocIndexable]:
        blocs_indexables: list[BlocIndexable] = []
        chemin_des_sections: list[str] = []
        titre_en_attente: _TitreEnAttente | None = None

        for page_ocr in sorted(resultat_ocr.pages, key=lambda page: page.numero_page):
            for bloc_ocr in page_ocr.blocs:
                if bloc_ocr.type_de_bloc == TypeDeBlocOcr.PIED_DE_PAGE:
                    continue

                if (
                    bloc_ocr.type_de_bloc == TypeDeBlocOcr.PARAGRAPHE
                    and bloc_ocr.titre
                ):
                    bloc_ocr = replace(
                        bloc_ocr,
                        type_de_bloc=TypeDeBlocOcr.TITRE,
                    )

                if bloc_ocr.type_de_bloc == TypeDeBlocOcr.TITRE:
                    if titre_en_attente is not None:
                        blocs_indexables.append(
                            self._cree_un_bloc_indexable(
                                texte=titre_en_attente.texte,
                                numero_page=titre_en_attente.page,
                                contexte=ContexteDuBloc(
                                    type_de_bloc=TypeDeBlocOcr.TITRE.value,
                                    titre=titre_en_attente.texte,
                                    section=titre_en_attente.texte,
                                    chemin_des_sections=titre_en_attente.chemin_des_sections,
                                    niveau=titre_en_attente.niveau,
                                ),
                            )
                        )
                    titre, texte_suivant = self._separe_le_titre_du_texte(
                        bloc_ocr.titre,
                        bloc_ocr.texte,
                    )
                    if not titre:
                        continue
                    niveau_du_titre = self._determine_le_niveau_du_titre(
                        titre,
                        bloc_ocr.niveau,
                    )
                    chemin_des_sections = self._met_a_jour_le_chemin_des_sections(
                        chemin_des_sections,
                        titre,
                        niveau_du_titre,
                    )
                    titre_en_attente = _TitreEnAttente(
                        texte=titre,
                        niveau=niveau_du_titre,
                        page=page_ocr.numero_page,
                        chemin_des_sections=tuple(chemin_des_sections),
                    )
                    if not texte_suivant:
                        continue
                    bloc_ocr = replace(
                        bloc_ocr,
                        type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
                        code=None,
                        titre=None,
                        texte=texte_suivant,
                        niveau=None,
                    )

                if self._est_un_bloc_a_ignorer(bloc_ocr):
                    continue

                texte = self._construit_le_texte(bloc_ocr)
                chemin_du_bloc = tuple(chemin_des_sections)
                titre_de_section = None
                if titre_en_attente is not None:
                    titre_de_section = titre_en_attente.texte
                    texte = self._ajoute_le_titre_au_premier_contenu(
                        titre_en_attente.texte,
                        texte,
                    )
                    titre_en_attente = None

                contexte = ContexteDuBloc(
                    type_de_bloc=bloc_ocr.type_de_bloc.value,
                    code_recommandation=bloc_ocr.code,
                    titre=bloc_ocr.titre or titre_de_section,
                    section=chemin_du_bloc[-1] if chemin_du_bloc else None,
                    chemin_des_sections=chemin_du_bloc,
                    niveau=bloc_ocr.niveau,
                )
                blocs_indexables.append(
                    self._cree_un_bloc_indexable(
                        texte=texte,
                        numero_page=page_ocr.numero_page,
                        contexte=contexte,
                    )
                )

        if titre_en_attente is not None:
            blocs_indexables.append(
                self._cree_un_bloc_indexable(
                    texte=titre_en_attente.texte,
                    numero_page=titre_en_attente.page,
                    contexte=ContexteDuBloc(
                        type_de_bloc=TypeDeBlocOcr.TITRE.value,
                        titre=titre_en_attente.texte,
                        section=titre_en_attente.texte,
                        chemin_des_sections=titre_en_attente.chemin_des_sections,
                        niveau=titre_en_attente.niveau,
                    ),
                )
            )

        return blocs_indexables

    @staticmethod
    def _met_a_jour_le_chemin_des_sections(
        chemin_des_sections: list[str],
        titre: str,
        niveau: int | None,
    ) -> list[str]:
        if niveau is None or niveau <= 0:
            return [titre]
        return [*chemin_des_sections[: niveau - 1], titre]

    @staticmethod
    def _determine_le_niveau_du_titre(
        titre: str,
        niveau: int | None,
    ) -> int | None:
        if niveau is not None and niveau > 0:
            return niveau
        correspondance = re.match(r"\s*(\d+(?:\.\d+)*)\b", titre)
        if correspondance is None:
            return None
        return correspondance.group(1).count(".") + 1

    @staticmethod
    def _est_un_bloc_a_ignorer(bloc_ocr: BlocOcr) -> bool:
        if bloc_ocr.est_decoratif:
            return True
        return not bloc_ocr.texte.strip() and not bloc_ocr.titre and not bloc_ocr.code

    @classmethod
    def _construit_le_texte(cls, bloc_ocr: BlocOcr) -> str:
        texte = bloc_ocr.texte.strip()
        if bloc_ocr.type_de_bloc != TypeDeBlocOcr.RECOMMANDATION:
            return texte
        parties = [
            partie
            for partie in (bloc_ocr.code, bloc_ocr.titre, texte)
            if partie and partie.strip()
        ]
        return "\n".join(dict.fromkeys(parties))

    @staticmethod
    def _separe_le_titre_du_texte(
        titre: str | None,
        texte: str,
    ) -> tuple[str, str]:
        titre_nettoye = (titre or "").strip()
        texte_nettoye = texte.strip()
        if not titre_nettoye:
            return texte_nettoye, ""
        if re.fullmatch(r"\d+(?:\.\d+)*", titre_nettoye) and texte_nettoye:
            return f"{titre_nettoye} {texte_nettoye}", ""
        if texte_nettoye == titre_nettoye:
            return titre_nettoye, ""
        return titre_nettoye, texte_nettoye

    @staticmethod
    def _ajoute_le_titre_au_premier_contenu(titre: str, texte: str) -> str:
        if not texte:
            return titre
        if texte == titre or texte.startswith(f"{titre}\n"):
            return texte
        return f"{titre}\n{texte}"

    @staticmethod
    def _cree_un_bloc_indexable(
        texte: str,
        numero_page: int,
        contexte: ContexteDuBloc,
    ) -> BlocIndexable:
        return BlocIndexable(
            texte=texte,
            page_debut=numero_page,
            page_fin=numero_page,
            pages_couvertes=(numero_page,),
            contexte=contexte,
        )
