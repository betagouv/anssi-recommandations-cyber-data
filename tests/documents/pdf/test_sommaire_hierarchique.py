from documents.pdf._sommaire_hierarchique import extrait_le_sommaire_hierarchique
from documents.pdf.modeles_ocr_json import (
    BlocOcr,
    PageOcr,
    ResultatOcrPdf,
    TypeDeBlocOcr,
)


def test_construit_une_hierarchie_depuis_des_entrees_numerotees() -> None:
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.TABLE_DES_MATIERES,
                        code=None,
                        titre="Table des matieres",
                        texte="",
                        elements_de_liste=(
                            "2 Methodologie de cloisonnement logique",
                            "2.3 Le cloisonnement du SI en Tiers",
                            "2.3.2 Analyse des chemins d'attaque",
                        ),
                    ),
                ),
            ),
        ),
    )

    assert extrait_le_sommaire_hierarchique(resultat_ocr) == {
        "Methodologie de cloisonnement logique": {
            "Le cloisonnement du SI en Tiers": {
                "Analyse des chemins d'attaque": {},
            },
        },
    }


def test_reunit_les_entrees_d_un_sommaire_reparti_sur_deux_pages() -> None:
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=2,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.TABLE_DES_MATIERES,
                        code=None,
                        titre="Table des matieres",
                        texte="",
                        elements_de_liste=(
                            "5 Choix d'architecture",
                            "5.1 Surface d'attaque",
                        ),
                    ),
                ),
            ),
            PageOcr(
                numero_page=2,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.TABLE_DES_MATIERES,
                        code=None,
                        titre=None,
                        texte="5.1.1 Clients de connexion distante",
                        est_une_continuation=True,
                    ),
                ),
            ),
        ),
    )

    assert extrait_le_sommaire_hierarchique(resultat_ocr) == {
        "Choix d'architecture": {
            "Surface d'attaque": {
                "Clients de connexion distante": {},
            },
        },
    }


def test_retire_les_pointilles_et_la_pagination_d_une_entree() -> None:
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.TABLE_DES_MATIERES,
                        code=None,
                        titre="Table des matieres",
                        texte="",
                        elements_de_liste=(
                            "5 Choix d'architecture",
                            "5.2 Mutualisation des postes d'administration . . . 106",
                        ),
                    ),
                ),
            ),
        ),
    )

    assert extrait_le_sommaire_hierarchique(resultat_ocr) == {
        "Choix d'architecture": {
            "Mutualisation des postes d'administration": {},
        },
    }


def test_ignore_une_entree_ambigue_qui_reutilise_un_numero() -> None:
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.TABLE_DES_MATIERES,
                        code=None,
                        titre="Table des matieres",
                        texte="",
                        elements_de_liste=(
                            "5 Choix d'architecture",
                            "5.2 Mutualisation des postes",
                            "5.2 Titre OCR contradictoire",
                        ),
                    ),
                ),
            ),
        ),
    )

    assert extrait_le_sommaire_hierarchique(resultat_ocr) == {
        "Choix d'architecture": {
            "Mutualisation des postes": {},
        },
    }


def test_reconnait_une_annexe_et_ses_sections() -> None:
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.TABLE_DES_MATIERES,
                        code=None,
                        titre="Table des matieres",
                        texte="",
                        elements_de_liste=(
                            "Annexe A Details complementaires",
                            "A.1 Conteneurs systeme",
                        ),
                    ),
                ),
            ),
        ),
    )

    assert extrait_le_sommaire_hierarchique(resultat_ocr) == {
        "Details complementaires": {
            "Conteneurs systeme": {},
        },
    }


def test_ignore_une_entree_sans_parent_connu() -> None:
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.TABLE_DES_MATIERES,
                        code=None,
                        titre="Table des matieres",
                        texte="",
                        elements_de_liste=("2.3.2 Analyse des chemins d'attaque",),
                    ),
                ),
            ),
        ),
    )

    assert extrait_le_sommaire_hierarchique(resultat_ocr) == {}


def test_ignore_une_entree_au_titre_ambigu_dans_le_meme_parent() -> None:
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.TABLE_DES_MATIERES,
                        code=None,
                        titre="Table des matieres",
                        texte="",
                        elements_de_liste=(
                            "1 Introduction",
                            "1.1 Objectif",
                            "1.2 Objectif",
                            "1.2.1 Detail ambigu",
                        ),
                    ),
                ),
            ),
        ),
    )

    assert extrait_le_sommaire_hierarchique(resultat_ocr) == {
        "Introduction": {
            "Objectif": {},
        },
    }
