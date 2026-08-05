import pytest

from documents.pdf._gestionnaire_sections import _GestionnaireDeSections
from documents.pdf._gestionnaire_sections import _determine_le_niveau_du_titre
from documents.pdf._normalisateur_ocr import _NormalisateurDeBlocsOcr
from documents.pdf._rattacheur_blocs import _RattacheurDeBlocs
from documents.pdf.assembleur_blocs_json import (
    BlocIndexable,
    BlocOcr,
    ContexteDuBloc,
    TypeDeBlocOcr,
)


@pytest.mark.parametrize(
    (
        "titre",
        "niveau_du_titre_detecte_par_ocr",
        "niveau_attendu",
    ),
    [
        ("3 Recommandations", None, 1),
        ("3.3 Protection des données", 1, 2),
        (" 3.3.1 Mesures", None, 3),
        ("Introduction", 2, 2),
        ("Introduction", 0, None),
        ("Introduction", -1, None),
        ("Introduction", None, None),
    ],
)
def test_determine_le_niveau_du_titre(
    titre,
    niveau_du_titre_detecte_par_ocr,
    niveau_attendu,
):
    assert (
        _determine_le_niveau_du_titre(
            titre,
            niveau_du_titre_detecte_par_ocr,
        )
        == niveau_attendu
    )


@pytest.mark.parametrize(
    ("type_de_bloc", "texte", "elements_de_liste", "type_attendu"),
    [
        pytest.param(
            TypeDeBlocOcr.PARAGRAPHE,
            "Contenu",
            (),
            TypeDeBlocOcr.PARAGRAPHE,
            id="paragraphe",
        ),
        pytest.param(
            TypeDeBlocOcr.PARAGRAPHE,
            "Introduction",
            ("Premier élément",),
            TypeDeBlocOcr.LISTE,
            id="elements_de_liste",
        ),
        pytest.param(
            TypeDeBlocOcr.PARAGRAPHE,
            "■ Premier élément",
            (),
            TypeDeBlocOcr.LISTE,
            id="marqueur_de_liste",
        ),
        pytest.param(
            TypeDeBlocOcr.RECOMMANDATION,
            "Contenu",
            ("Action",),
            TypeDeBlocOcr.RECOMMANDATION,
            id="recommandation",
        ),
        pytest.param(
            TypeDeBlocOcr.TABLEAU,
            "■ Cellule",
            (),
            TypeDeBlocOcr.TABLEAU,
            id="tableau",
        ),
        pytest.param(
            TypeDeBlocOcr.TABLE_DES_MATIERES,
            "Sommaire",
            (),
            TypeDeBlocOcr.TABLE_DES_MATIERES,
            id="table_des_matieres",
        ),
        pytest.param(
            TypeDeBlocOcr.AUTRE,
            "Encadré",
            (),
            TypeDeBlocOcr.AUTRE,
            id="autre",
        ),
    ],
)
def test_determine_le_type_de_bloc_indexable(
    type_de_bloc,
    texte,
    elements_de_liste,
    type_attendu,
):
    normalisateur = _NormalisateurDeBlocsOcr()
    bloc_ocr = BlocOcr(
        type_de_bloc=type_de_bloc,
        code=None,
        titre=None,
        texte=texte,
        elements_de_liste=elements_de_liste,
    )

    assert normalisateur.determine_le_type_de_bloc_indexable(bloc_ocr) == type_attendu


def test_le_normalisateur_prepare_le_texte_indexable_d_un_tableau():
    normalisateur = _NormalisateurDeBlocsOcr()
    bloc_ocr = BlocOcr(
        type_de_bloc=TypeDeBlocOcr.TABLEAU,
        code=None,
        titre=None,
        texte="Titre",
        lignes_de_tableau=(("Nom", "Valeur"),),
    )

    assert (
        normalisateur.prepare_le_texte_indexable(bloc_ocr)
        == "Titre\nNom\tValeur"
    )


def test_le_gestionnaire_de_sections_conserve_le_chemin_du_titre():
    gestionnaire = _GestionnaireDeSections(_NormalisateurDeBlocsOcr())
    bloc_ocr = BlocOcr(
        type_de_bloc=TypeDeBlocOcr.TITRE,
        code=None,
        titre="2.1 Mesures",
        texte="",
        niveau=1,
    )

    bloc_apres_titre, est_un_titre_traite, titre_precedent = (
        gestionnaire.traite_le_titre(bloc_ocr, numero_page=4)
    )
    titre_en_attente = gestionnaire.consomme_le_titre_en_attente()

    assert bloc_apres_titre is None
    assert est_un_titre_traite
    assert titre_precedent is None
    assert titre_en_attente is not None
    assert titre_en_attente.chemin_des_sections == ("2.1 Mesures",)
    assert titre_en_attente.page == 4


def test_le_rattacheur_fusionne_une_continuation():
    rattacheur = _RattacheurDeBlocs(_NormalisateurDeBlocsOcr())
    contexte = ContexteDuBloc(type_de_bloc=TypeDeBlocOcr.PARAGRAPHE.value)
    bloc_precedent = BlocIndexable(
        texte="Le chiffrement",
        page_debut=1,
        page_fin=1,
        pages_couvertes=(1,),
        contexte=contexte,
    )
    bloc_suivant = BlocIndexable(
        texte="protège les données.",
        page_debut=2,
        page_fin=2,
        pages_couvertes=(2,),
        contexte=contexte,
    )
    bloc_ocr = BlocOcr(
        type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
        code=None,
        titre=None,
        texte="protège les données.",
        est_une_continuation=True,
    )
    blocs_indexables = [bloc_precedent]

    rattacheur.rattache(
        blocs_indexables,
        bloc_ocr,
        bloc_suivant,
        est_le_premier_bloc_utile=True,
    )

    assert [bloc.texte for bloc in blocs_indexables] == [
        "Le chiffrement\nprotège les données."
    ]
