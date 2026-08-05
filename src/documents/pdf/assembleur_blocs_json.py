from dataclasses import dataclass
from functools import partial
from typing import TypeGuard

from documents.pdf._gestionnaire_sections import (
    _GestionnaireDeSections,
    _TitreEnAttente,
)
from documents.pdf._normalisateur_ocr import _NormalisateurDeBlocsOcr
from documents.pdf._rattacheur_blocs import _RattacheurDeBlocs
from documents.pdf.modeles_ocr_json import (
    BlocIndexable,
    BlocOcr,
    ContexteDuBloc,
    PageOcr,
    ResultatOcrPdf,
    TypeDeBlocOcr,
)


@dataclass(frozen=True)
class _PreparationDuBloc:
    bloc_ocr: BlocOcr
    bloc_indexable: BlocIndexable
    titre_a_finaliser: _TitreEnAttente | None


@dataclass
class _EtatDeLaPage:
    est_le_premier_bloc_utile: bool = True

    def marque_un_bloc_utile(self) -> None:
        self.est_le_premier_bloc_utile = False


class AssembleurDeBlocsJson:
    def assemble(self, resultat_ocr: ResultatOcrPdf) -> list[BlocIndexable]:
        normalisateur = _NormalisateurDeBlocsOcr()
        sections = _GestionnaireDeSections(normalisateur)
        rattacheur = _RattacheurDeBlocs(normalisateur)
        blocs_indexables: list[BlocIndexable] = []

        for page_ocr in sorted(resultat_ocr.pages, key=lambda page: page.numero_page):
            self._assemble_les_blocs_de_la_page(
                page_ocr,
                normalisateur,
                sections,
                rattacheur,
                blocs_indexables,
            )

        self._ajoute_le_titre_en_attente(sections, blocs_indexables)
        return blocs_indexables

    def _assemble_les_blocs_de_la_page(
        self,
        page_ocr: PageOcr,
        normalisateur: _NormalisateurDeBlocsOcr,
        sections: _GestionnaireDeSections,
        rattacheur: _RattacheurDeBlocs,
        blocs_indexables: list[BlocIndexable],
    ) -> None:
        etat_de_la_page = _EtatDeLaPage()
        blocs_ocr = filter(normalisateur.doit_traiter, page_ocr.blocs)
        preparations = map(
            partial(
                self._prepare_le_bloc,
                numero_page=page_ocr.numero_page,
                normalisateur=normalisateur,
                sections=sections,
                etat_de_la_page=etat_de_la_page,
            ),
            blocs_ocr,
        )

        for preparation in filter(_est_une_preparation_valide, preparations):
            if preparation.titre_a_finaliser is not None:
                blocs_indexables.append(
                    _cree_un_bloc_pour_un_titre(preparation.titre_a_finaliser)
                )
            rattacheur.rattache(
                blocs_indexables,
                preparation.bloc_ocr,
                preparation.bloc_indexable,
                etat_de_la_page.est_le_premier_bloc_utile,
            )
            etat_de_la_page.marque_un_bloc_utile()

    def _prepare_le_bloc(
        self,
        bloc_ocr: BlocOcr,
        numero_page: int,
        normalisateur: _NormalisateurDeBlocsOcr,
        sections: _GestionnaireDeSections,
        etat_de_la_page: _EtatDeLaPage,
    ) -> _PreparationDuBloc | None:
        bloc_normalise = sections.normalise(bloc_ocr)
        bloc_apres_titre, est_un_titre_traite, titre_a_finaliser = sections.traite_le_titre(
            bloc_normalise,
            numero_page,
        )
        if est_un_titre_traite:
            etat_de_la_page.marque_un_bloc_utile()
        if bloc_apres_titre is None:
            return None

        if (
            bloc_apres_titre.type_de_bloc == TypeDeBlocOcr.AUTRE
            or sections.doit_finaliser_le_titre_avant(bloc_apres_titre)
        ):
            titre_a_finaliser = (
                titre_a_finaliser or sections.consomme_le_titre_en_attente()
            )

        bloc_indexable = self._cree_le_bloc_indexable(
            bloc_apres_titre,
            numero_page,
            normalisateur,
            sections,
        )
        if bloc_indexable is None:
            return None
        return _PreparationDuBloc(
            bloc_apres_titre,
            bloc_indexable,
            titre_a_finaliser,
        )

    def _cree_le_bloc_indexable(
        self,
        bloc_ocr: BlocOcr,
        numero_page: int,
        normalisateur: _NormalisateurDeBlocsOcr,
        sections: _GestionnaireDeSections,
    ) -> BlocIndexable | None:
        if normalisateur.est_un_bloc_a_ignorer(bloc_ocr):
            return None
        texte = normalisateur.prepare_le_texte_indexable(bloc_ocr)
        if bloc_ocr.type_de_bloc == TypeDeBlocOcr.PARAGRAPHE and bloc_ocr.titre:
            texte = _ajoute_le_titre_au_premier_contenu(bloc_ocr.titre, texte)
        titre_en_attente = sections.consomme_le_titre_en_attente()
        if titre_en_attente is not None:
            texte = _ajoute_le_titre_au_premier_contenu(
                titre_en_attente.texte,
                texte,
            )
        chemin_des_sections = tuple(sections.chemin_des_sections)
        contexte = ContexteDuBloc(
            type_de_bloc=normalisateur.determine_le_type_de_bloc_indexable(
                bloc_ocr
            ).value,
            code_recommandation=bloc_ocr.code,
            titre=bloc_ocr.titre
            or (titre_en_attente.texte if titre_en_attente is not None else None),
            section=chemin_des_sections[-1] if chemin_des_sections else None,
            chemin_des_sections=chemin_des_sections,
            niveau=bloc_ocr.niveau,
        )
        return _cree_un_bloc_indexable(texte, numero_page, contexte)

    def _ajoute_le_titre_en_attente(
        self,
        sections: _GestionnaireDeSections,
        blocs_indexables: list[BlocIndexable],
    ) -> None:
        titre_en_attente = sections.consomme_le_titre_en_attente()
        if titre_en_attente is not None:
            blocs_indexables.append(_cree_un_bloc_pour_un_titre(titre_en_attente))


def _est_une_preparation_valide(
    preparation: _PreparationDuBloc | None,
) -> TypeGuard[_PreparationDuBloc]:
    return preparation is not None


def _ajoute_le_titre_au_premier_contenu(titre: str, texte: str) -> str:
    if not texte:
        return titre
    if texte == titre or texte.startswith(f"{titre}\n"):
        return texte
    return f"{titre}\n{texte}"


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


def _cree_un_bloc_pour_un_titre(
    titre_en_attente: _TitreEnAttente,
) -> BlocIndexable:
    return _cree_un_bloc_indexable(
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
