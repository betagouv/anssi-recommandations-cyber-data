import re
from dataclasses import dataclass, replace
from enum import StrEnum


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
            est_le_premier_bloc_utile = True
            for bloc_ocr in page_ocr.blocs:
                if bloc_ocr.type_de_bloc == TypeDeBlocOcr.PIED_DE_PAGE:
                    continue

                if self._doit_promouvoir_le_titre_local_en_section(
                    bloc_ocr,
                    chemin_des_sections,
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
                    est_le_premier_bloc_utile = False
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
                if (
                    bloc_ocr.type_de_bloc == TypeDeBlocOcr.PARAGRAPHE
                    and bloc_ocr.titre
                ):
                    texte = self._ajoute_le_titre_au_premier_contenu(
                        bloc_ocr.titre,
                        texte,
                    )
                type_de_bloc = self._determine_le_type_de_bloc_indexable(bloc_ocr)
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
                    type_de_bloc=type_de_bloc.value,
                    code_recommandation=bloc_ocr.code,
                    titre=bloc_ocr.titre or titre_de_section,
                    section=chemin_du_bloc[-1] if chemin_du_bloc else None,
                    chemin_des_sections=chemin_du_bloc,
                    niveau=bloc_ocr.niveau,
                )
                bloc_indexable = self._cree_un_bloc_indexable(
                    texte=texte,
                    numero_page=page_ocr.numero_page,
                    contexte=contexte,
                )
                est_une_continuation = bloc_ocr.est_une_continuation or (
                    est_le_premier_bloc_utile
                    and (
                        self._est_une_puce_de_liste(bloc_ocr.texte)
                        or self._semble_etre_la_suite_d_un_paragraphe(
                            blocs_indexables[-1] if blocs_indexables else None,
                            bloc_indexable,
                        )
                    )
                )
                if blocs_indexables and self._est_une_liste_identique_repetee(
                    blocs_indexables[-1],
                    bloc_indexable,
                ):
                    continue
                if blocs_indexables and self._peut_fusionner(
                    blocs_indexables[-1],
                    bloc_indexable,
                    est_une_continuation,
                ):
                    blocs_indexables[-1] = self._fusionne_les_blocs(
                        blocs_indexables[-1],
                        bloc_indexable,
                    )
                elif blocs_indexables and self._peut_joindre_une_liste_a_son_introduction(
                    blocs_indexables[-1],
                    bloc_indexable,
                ):
                    blocs_indexables[-1] = self._fusionne_les_blocs(
                        blocs_indexables[-1],
                        bloc_indexable,
                        bloc_indexable.contexte,
                    )
                else:
                    blocs_indexables.append(bloc_indexable)
                est_le_premier_bloc_utile = False

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
        correspondance = re.match(r"\s*(\d+(?:\.\d+)*)\b", titre)
        if correspondance is not None:
            return correspondance.group(1).count(".") + 1
        if niveau is not None and niveau > 0:
            return niveau
        return None

    @classmethod
    def _doit_promouvoir_le_titre_local_en_section(
        cls,
        bloc_ocr: BlocOcr,
        chemin_des_sections: list[str],
    ) -> bool:
        if bloc_ocr.type_de_bloc != TypeDeBlocOcr.PARAGRAPHE or not bloc_ocr.titre:
            return False
        numero_de_section = cls._extrait_le_numero_de_section(bloc_ocr.titre)
        if numero_de_section is None:
            return False
        niveau = numero_de_section.count(".") + 1
        chapitre_courant = cls._extrait_le_chapitre_courant(chemin_des_sections)
        chapitre_du_titre = numero_de_section.split(".")[0]
        if chapitre_courant is None:
            return niveau == 1
        if niveau == 1:
            return int(chapitre_du_titre) in {
                int(chapitre_courant),
                int(chapitre_courant) + 1,
            }
        return chapitre_du_titre == chapitre_courant

    @staticmethod
    def _extrait_le_numero_de_section(titre: str) -> str | None:
        correspondance = re.match(r"\s*(\d+(?:\.\d+)*)\b", titre)
        if correspondance is None:
            return None
        return correspondance.group(1)

    @classmethod
    def _extrait_le_chapitre_courant(
        cls,
        chemin_des_sections: list[str],
    ) -> str | None:
        for section in chemin_des_sections:
            numero_de_section = cls._extrait_le_numero_de_section(section)
            if numero_de_section is not None:
                return numero_de_section.split(".")[0]
        return None

    @staticmethod
    def _est_un_bloc_a_ignorer(bloc_ocr: BlocOcr) -> bool:
        texte = bloc_ocr.texte.strip()
        if bloc_ocr.type_de_bloc == TypeDeBlocOcr.LISTE:
            return not texte and not bloc_ocr.elements_de_liste
        if bloc_ocr.type_de_bloc == TypeDeBlocOcr.TABLEAU:
            return not texte and not bloc_ocr.lignes_de_tableau
        return not texte and not bloc_ocr.titre and not bloc_ocr.code

    @classmethod
    def _construit_le_texte(cls, bloc_ocr: BlocOcr) -> str:
        texte = bloc_ocr.texte.strip()
        if cls._est_une_puce_de_liste(texte):
            texte = cls._formate_l_element_de_liste(texte)
        elements_de_texte = {
            cls._retire_le_marqueur_de_liste(ligne)
            for ligne in texte.splitlines()
        }
        parties = [texte]
        parties.extend(
            cls._formate_l_element_de_liste(element)
            for element in bloc_ocr.elements_de_liste
            if cls._retire_le_marqueur_de_liste(element) not in elements_de_texte
        )
        parties.extend(
            "\t".join(cellule.strip() for cellule in ligne)
            for ligne in bloc_ocr.lignes_de_tableau
        )
        texte = "\n".join(partie for partie in dict.fromkeys(parties) if partie)
        if bloc_ocr.type_de_bloc != TypeDeBlocOcr.RECOMMANDATION:
            return texte

        parties_recommandation = [
            partie
            for partie in (bloc_ocr.code, bloc_ocr.titre, texte)
            if partie and partie.strip()
        ]
        return "\n".join(dict.fromkeys(parties_recommandation))

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
    def _determine_le_type_de_bloc_indexable(bloc_ocr: BlocOcr) -> TypeDeBlocOcr:
        if bloc_ocr.type_de_bloc in {
            TypeDeBlocOcr.RECOMMANDATION,
            TypeDeBlocOcr.TABLEAU,
            TypeDeBlocOcr.TABLE_DES_MATIERES,
        }:
            return bloc_ocr.type_de_bloc
        if bloc_ocr.elements_de_liste or AssembleurDeBlocsJson._est_une_puce_de_liste(
            bloc_ocr.texte
        ):
            return TypeDeBlocOcr.LISTE
        return bloc_ocr.type_de_bloc

    @staticmethod
    def _formate_l_element_de_liste(element: str) -> str:
        element_nettoye = AssembleurDeBlocsJson._retire_le_marqueur_de_liste(element)
        return f"- {element_nettoye}"

    @staticmethod
    def _est_une_puce_de_liste(texte: str) -> bool:
        texte_nettoye = texte.lstrip()
        return texte_nettoye.startswith(("■", "•", "▪", "◦", "‣", "- "))

    @classmethod
    def _semble_etre_la_suite_d_un_paragraphe(
        cls,
        bloc_precedent: BlocIndexable | None,
        bloc_suivant: BlocIndexable,
    ) -> bool:
        if bloc_precedent is None:
            return False
        types_compatibles = (
            bloc_precedent.contexte.type_de_bloc
            == bloc_suivant.contexte.type_de_bloc
            == TypeDeBlocOcr.PARAGRAPHE.value
            or (
                bloc_precedent.contexte.type_de_bloc == TypeDeBlocOcr.LISTE.value
                and bloc_suivant.contexte.type_de_bloc
                == TypeDeBlocOcr.PARAGRAPHE.value
            )
            or (
                bloc_precedent.contexte.type_de_bloc
                == TypeDeBlocOcr.RECOMMANDATION.value
                and bloc_suivant.contexte.type_de_bloc
                == TypeDeBlocOcr.PARAGRAPHE.value
            )
        )
        if not types_compatibles:
            return False
        texte_precedent = bloc_precedent.texte.rstrip()
        texte_suivant = bloc_suivant.texte.lstrip()
        if not texte_precedent or not texte_suivant:
            return False
        if texte_precedent.endswith((".", "!", "?", ";", ":", "…")):
            return False
        return texte_suivant[0].islower()

    @staticmethod
    def _retire_le_marqueur_de_liste(texte: str) -> str:
        texte_nettoye = texte.strip()
        if texte_nettoye.startswith(("■", "•", "▪", "◦", "‣")):
            return texte_nettoye[1:].lstrip()
        if texte_nettoye.startswith("- "):
            return texte_nettoye[2:].lstrip()
        return texte_nettoye

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

    @staticmethod
    def _peut_fusionner(
        bloc_precedent: BlocIndexable,
        bloc_suivant: BlocIndexable,
        est_une_continuation: bool,
    ) -> bool:
        if not est_une_continuation:
            return False
        pages_contigues = bloc_precedent.page_fin + 1 == bloc_suivant.page_debut
        deux_listes_sur_la_meme_page = (
            bloc_precedent.page_fin == bloc_suivant.page_debut
            and bloc_precedent.contexte.type_de_bloc
            == bloc_suivant.contexte.type_de_bloc
            == TypeDeBlocOcr.LISTE.value
        )
        if not pages_contigues and not deux_listes_sur_la_meme_page:
            return False
        if bloc_precedent.contexte.chemin_des_sections != bloc_suivant.contexte.chemin_des_sections:
            return False
        types_compatibles = (
            bloc_precedent.contexte.type_de_bloc
            == bloc_suivant.contexte.type_de_bloc
            and bloc_suivant.contexte.type_de_bloc
            in {TypeDeBlocOcr.PARAGRAPHE.value, TypeDeBlocOcr.LISTE.value}
        )
        return types_compatibles or (
            bloc_precedent.contexte.type_de_bloc == TypeDeBlocOcr.LISTE.value
            and bloc_suivant.contexte.type_de_bloc == TypeDeBlocOcr.PARAGRAPHE.value
        ) or (
            bloc_precedent.contexte.type_de_bloc
            == TypeDeBlocOcr.RECOMMANDATION.value
            and bloc_suivant.contexte.type_de_bloc == TypeDeBlocOcr.PARAGRAPHE.value
        ) or (
            bloc_precedent.contexte.type_de_bloc
            == TypeDeBlocOcr.RECOMMANDATION.value
            and bloc_suivant.contexte.type_de_bloc == TypeDeBlocOcr.LISTE.value
            and AssembleurDeBlocsJson._contient_des_elements_de_liste(
                bloc_precedent.texte
            )
        )

    @staticmethod
    def _contient_des_elements_de_liste(texte: str) -> bool:
        return any(
            ligne.lstrip().startswith("- ") for ligne in texte.splitlines()
        )

    @staticmethod
    def _est_une_liste_identique_repetee(
        bloc_precedent: BlocIndexable,
        bloc_suivant: BlocIndexable,
    ) -> bool:
        return (
            bloc_precedent.page_debut == bloc_suivant.page_debut
            and bloc_precedent.page_fin == bloc_suivant.page_fin
            and bloc_precedent.contexte.chemin_des_sections
            == bloc_suivant.contexte.chemin_des_sections
            and bloc_precedent.contexte.type_de_bloc == TypeDeBlocOcr.LISTE.value
            and bloc_suivant.contexte.type_de_bloc == TypeDeBlocOcr.LISTE.value
            and bloc_precedent.texte == bloc_suivant.texte
        )

    @staticmethod
    def _peut_joindre_une_liste_a_son_introduction(
        bloc_precedent: BlocIndexable,
        bloc_suivant: BlocIndexable,
    ) -> bool:
        if bloc_precedent.page_fin != bloc_suivant.page_debut:
            return False
        if bloc_precedent.contexte.chemin_des_sections != bloc_suivant.contexte.chemin_des_sections:
            return False
        if bloc_precedent.contexte.type_de_bloc != TypeDeBlocOcr.PARAGRAPHE.value:
            return False
        if bloc_suivant.contexte.type_de_bloc != TypeDeBlocOcr.LISTE.value:
            return False
        return bloc_precedent.texte.rstrip().endswith(":")

    @staticmethod
    def _fusionne_les_blocs(
        bloc_precedent: BlocIndexable,
        bloc_suivant: BlocIndexable,
        contexte: ContexteDuBloc | None = None,
    ) -> BlocIndexable:
        texte = (
            bloc_precedent.texte
            if bloc_precedent.texte == bloc_suivant.texte
            else f"{bloc_precedent.texte}\n{bloc_suivant.texte}"
        )
        return replace(
            bloc_precedent,
            texte=texte,
            page_fin=bloc_suivant.page_fin,
            pages_couvertes=tuple(
                dict.fromkeys(
                    bloc_precedent.pages_couvertes + bloc_suivant.pages_couvertes
                )
            ),
            contexte=contexte or bloc_precedent.contexte,
        )
