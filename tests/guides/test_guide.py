from guides.chunker_docling_mqc import Position
from guides.guide import (
    Page,
    Guide,
    BlocPage,
)


def test_page_peut_creer_une_page():
    page = Page(numero_page=1)
    assert page.numero_page == 1


def test_page_a_une_liste_de_blocs_vide_par_defaut():
    page = Page(numero_page=1)
    assert page.blocs == []


def test_guide_peut_ajouter_un_bloc():
    page = Page(numero_page=1)
    position = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    bloc = BlocPage(texte="Mon texte", position=position)

    page.ajoute_bloc(bloc)

    assert len(page.blocs) == 1
    assert page.blocs[0] == bloc


def test_pages_peut_etre_creee():
    guide = Guide()
    assert guide is not None


def test_pages_a_une_collection_de_pages_vide_par_defaut():
    guide = Guide()
    assert guide.pages == {}


def test_guide_peut_ajouter_un_bloc_dans_une_page():
    guide = Guide()
    position = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)

    guide.ajoute_bloc_a_la_page(1, position, "Une page")

    assert len(guide.pages) == 1
    assert guide.pages[1] == Page(
        numero_page=1, blocs=[BlocPage(texte="Une page", position=position)]
    )


def test_guide_peut_ajouter_deux_blocs_sur_une_meme_page():
    guide = Guide()
    position_bloc_1 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=0.0, largeur=100.0, hauteur=5.0)

    guide.ajoute_bloc_a_la_page(1, position_bloc_1, "Un titre")
    guide.ajoute_bloc_a_la_page(1, position_bloc_2, "Un paragraphe")

    assert len(guide.pages) == 1
    assert guide.pages[1].blocs[0].texte == "Un titre"
    assert guide.pages[1].blocs[1].texte == "Un paragraphe"


def test_guide_reordonne_lorsque_l_on_ajoute_un_bloc():
    guide = Guide()
    position_bloc_1 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)

    guide.ajoute_bloc_a_la_page(1, position_bloc_1, "Un paragraphe en seconde position")
    guide.ajoute_bloc_a_la_page(
        1, position_bloc_2, "Un paragraphe en première position"
    )

    assert len(guide.pages) == 1
    assert guide.pages[1].blocs[0].texte == "Un paragraphe en première position"
    assert guide.pages[1].blocs[1].texte == "Un paragraphe en seconde position"


def test_guide_fusionne_un_titre_avec_son_contenu():
    guide = Guide()
    position_bloc_1 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0)
    position_bloc_3 = Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0)

    guide.ajoute_bloc_a_la_page(1, position_bloc_1, "Titre 1")
    guide.ajoute_bloc_a_la_page(1, position_bloc_2, "Titre 2")
    guide.ajoute_bloc_a_la_page(1, position_bloc_3, "Contenu.")

    assert len(guide.pages[1].blocs) == 2
    assert guide.pages[1].blocs[0].texte == "Titre 1"
    assert guide.pages[1].blocs[1].texte == "Titre 2\nContenu."


def test_guide_fusionne_un_titre_avec_son_contenu_ne_duplique_pas_les_sections():
    guide = Guide()
    position_bloc_1 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0)
    position_bloc_3 = Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0)

    guide.ajoute_bloc_a_la_page(
        1, position_bloc_1, "[SECTION] 2.1 Authentification et premières définitions"
    )
    guide.ajoute_bloc_a_la_page(
        1,
        position_bloc_2,
        "[SECTION] 2.1 Authentification et premières définitions\n[TEXTE] L'authentification est un mécanisme faisant intervenir deux entités distinctes : un prouveur et un vérifieur comme illustré par la figure 1 .",
    )
    guide.ajoute_bloc_a_la_page(1, position_bloc_3, "Titre 3")

    assert len(guide.pages[1].blocs) == 2
    assert (
        guide.pages[1].blocs[0].texte
        == "[SECTION] 2.1 Authentification et premières définitions\n[TEXTE] L'authentification est un mécanisme faisant intervenir deux entités distinctes : un prouveur et un vérifieur comme illustré par la figure 1 ."
    )
    assert guide.pages[1].blocs[1].texte == "Titre 3"
