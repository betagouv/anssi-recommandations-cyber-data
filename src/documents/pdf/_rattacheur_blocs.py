from dataclasses import replace
from enum import StrEnum

from documents.pdf._normalisateur_ocr import _NormalisateurDeBlocsOcr
from documents.pdf.modeles_ocr_json import (
    BlocIndexable,
    BlocOcr,
    ContexteDuBloc,
    TypeDeBlocOcr,
)


class _ActionDeRattachement(StrEnum):
    AJOUTE = "ajoute"
    IGNORE_LE_DOUBLON = "ignore_le_doublon"
    FUSIONNE = "fusionne"
    FUSIONNE_COMME_LISTE = "fusionne_comme_liste"


class _RattacheurDeBlocs:
    def __init__(self, normalisateur: _NormalisateurDeBlocsOcr) -> None:
        self._normalisateur = normalisateur

    def rattache(
        self,
        blocs_indexables: list[BlocIndexable],
        bloc_ocr: BlocOcr,
        bloc_indexable: BlocIndexable,
        est_le_premier_bloc_utile: bool,
    ) -> None:
        bloc_precedent = blocs_indexables[-1] if blocs_indexables else None
        action = self._determine_l_action_de_rattachement(
            bloc_precedent,
            bloc_ocr,
            bloc_indexable,
            est_le_premier_bloc_utile,
        )
        self._applique_l_action_de_rattachement(
            blocs_indexables,
            bloc_indexable,
            action,
        )

    def _determine_l_action_de_rattachement(
        self,
        bloc_precedent: BlocIndexable | None,
        bloc_ocr: BlocOcr,
        bloc_indexable: BlocIndexable,
        est_le_premier_bloc_utile: bool,
    ) -> _ActionDeRattachement:
        if bloc_precedent is None:
            return _ActionDeRattachement.AJOUTE
        if self._est_une_liste_identique_repetee(bloc_precedent, bloc_indexable):
            return _ActionDeRattachement.IGNORE_LE_DOUBLON
        est_une_continuation = self._est_une_continuation(
            bloc_precedent,
            bloc_ocr,
            bloc_indexable,
            est_le_premier_bloc_utile,
        )
        if self._peut_fusionner(
            bloc_precedent,
            bloc_indexable,
            est_une_continuation,
        ):
            return _ActionDeRattachement.FUSIONNE
        if self._peut_joindre_une_liste_a_son_introduction(
            bloc_precedent,
            bloc_indexable,
        ):
            return _ActionDeRattachement.FUSIONNE_COMME_LISTE
        return _ActionDeRattachement.AJOUTE

    def _est_une_continuation(
        self,
        bloc_precedent: BlocIndexable,
        bloc_ocr: BlocOcr,
        bloc_indexable: BlocIndexable,
        est_le_premier_bloc_utile: bool,
    ) -> bool:
        if bloc_ocr.est_une_continuation:
            return True
        if not est_le_premier_bloc_utile:
            return False
        if self._normalisateur.est_une_puce_de_liste(bloc_ocr.texte):
            return True
        return self._semble_etre_la_suite_d_un_paragraphe(
            bloc_precedent,
            bloc_indexable,
        )

    def _applique_l_action_de_rattachement(
        self,
        blocs_indexables: list[BlocIndexable],
        bloc_indexable: BlocIndexable,
        action: _ActionDeRattachement,
    ) -> None:
        if action == _ActionDeRattachement.AJOUTE:
            blocs_indexables.append(bloc_indexable)
            return
        if action == _ActionDeRattachement.IGNORE_LE_DOUBLON:
            return
        if not blocs_indexables:
            raise RuntimeError("Un rattachement exige un bloc précédent")
        bloc_precedent = blocs_indexables[-1]
        if action == _ActionDeRattachement.FUSIONNE:
            blocs_indexables[-1] = _fusionne_les_blocs(
                bloc_precedent,
                bloc_indexable,
            )
            return
        if action == _ActionDeRattachement.FUSIONNE_COMME_LISTE:
            blocs_indexables[-1] = _fusionne_les_blocs(
                bloc_precedent,
                bloc_indexable,
                bloc_indexable.contexte,
            )
            return
        raise ValueError(f"Action de rattachement inconnue: {action}")

    def _semble_etre_la_suite_d_un_paragraphe(
        self,
        bloc_precedent: BlocIndexable,
        bloc_suivant: BlocIndexable,
    ) -> bool:
        if not _les_types_de_blocs_sont_compatibles_pour_fusion(
            bloc_precedent,
            bloc_suivant,
        ):
            return False
        texte_precedent = bloc_precedent.texte.rstrip()
        texte_suivant = bloc_suivant.texte.lstrip()
        if not texte_precedent or not texte_suivant:
            return False
        if texte_precedent.endswith((".", "!", "?", ";", ":", "…")):
            return False
        return texte_suivant[0].islower()

    def _peut_fusionner(
        self,
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
        if (
            bloc_precedent.contexte.chemin_des_sections
            != bloc_suivant.contexte.chemin_des_sections
        ):
            return False
        return _les_types_de_blocs_sont_compatibles_pour_fusion(
            bloc_precedent,
            bloc_suivant,
            autorise_la_fusion_de_listes=True,
        ) or (
            bloc_precedent.contexte.type_de_bloc
            == TypeDeBlocOcr.RECOMMANDATION.value
            and bloc_suivant.contexte.type_de_bloc == TypeDeBlocOcr.LISTE.value
            and _contient_des_elements_de_liste(bloc_precedent.texte)
        )

    def _est_une_liste_identique_repetee(
        self,
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

    def _peut_joindre_une_liste_a_son_introduction(
        self,
        bloc_precedent: BlocIndexable,
        bloc_suivant: BlocIndexable,
    ) -> bool:
        if bloc_precedent.page_fin != bloc_suivant.page_debut:
            return False
        if (
            bloc_precedent.contexte.chemin_des_sections
            != bloc_suivant.contexte.chemin_des_sections
        ):
            return False
        if bloc_precedent.contexte.type_de_bloc != TypeDeBlocOcr.PARAGRAPHE.value:
            return False
        if bloc_suivant.contexte.type_de_bloc != TypeDeBlocOcr.LISTE.value:
            return False
        return bloc_precedent.texte.rstrip().endswith(":")


def _les_types_de_blocs_sont_compatibles_pour_fusion(
    bloc_precedent: BlocIndexable,
    bloc_suivant: BlocIndexable,
    *,
    autorise_la_fusion_de_listes: bool = False,
) -> bool:
    type_precedent = bloc_precedent.contexte.type_de_bloc
    type_suivant = bloc_suivant.contexte.type_de_bloc
    types_identiques_autorises = {TypeDeBlocOcr.PARAGRAPHE.value}
    if autorise_la_fusion_de_listes:
        types_identiques_autorises.add(TypeDeBlocOcr.LISTE.value)
    return (
        type_precedent == type_suivant
        and type_suivant in types_identiques_autorises
    ) or (
        type_precedent == TypeDeBlocOcr.LISTE.value
        and type_suivant == TypeDeBlocOcr.PARAGRAPHE.value
    ) or (
        type_precedent == TypeDeBlocOcr.RECOMMANDATION.value
        and type_suivant == TypeDeBlocOcr.PARAGRAPHE.value
    )


def _contient_des_elements_de_liste(texte: str) -> bool:
    return any(ligne.lstrip().startswith("- ") for ligne in texte.splitlines())


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
