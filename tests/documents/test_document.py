import pytest

from documents.chunker_docling_mqc import Position
from documents.document import (
    PagePDF,
    Document,
    BlocPage,
)
from documents.document_pdf import DocumentPDF

document_pdf = DocumentPDF(
    chemin_pdf="tests/data/guide_test.pdf",
    url_pdf="http://document.local/guide_test.pdf",
)


def test_page_peut_creer_une_page():
    page = PagePDF(numero_page=1)
    assert page.numero_page == 1


def test_page_a_une_liste_de_blocs_vide_par_defaut():
    page = PagePDF(numero_page=1)
    assert page.blocs == []


def test_page_peut_ajouter_un_bloc():
    page = PagePDF(numero_page=1)
    position = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    bloc = BlocPage(texte="[TEXTE] Mon texte", position=position)

    page.ajoute_bloc(bloc)

    assert len(page.blocs) == 1
    assert page.blocs[0] == bloc


def test_pages_peut_etre_creee():
    document = Document(document=document_pdf)
    assert document is not None


def test_pages_a_une_collection_de_pages_vide_par_defaut():
    document = Document(document=document_pdf)
    assert document.pages == {}


def test_document_peut_ajouter_un_bloc_dans_une_page():
    document = Document(document=document_pdf)
    position = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)

    document.ajoute_bloc_a_la_page(1, position, "[TEXTE] Une page")

    assert len(document.pages) == 1
    assert document.pages[1] == PagePDF(
        numero_page=1, blocs=[BlocPage(texte="[TEXTE] Une page", position=position)]
    )


def test_document_peut_ajouter_deux_blocs_sur_une_meme_page():
    document = Document(document=document_pdf)
    position_bloc_1 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=0.0, largeur=100.0, hauteur=5.0)

    document.ajoute_bloc_a_la_page(1, position_bloc_1, "[TEXTE] Un titre")
    document.ajoute_bloc_a_la_page(1, position_bloc_2, "[TEXTE] Un paragraphe")

    assert len(document.pages) == 1
    assert document.pages[1].blocs[0].texte == "[TEXTE] Un titre"
    assert document.pages[1].blocs[1].texte == "[TEXTE] Un paragraphe"


def test_document_reordonne_lorsque_l_on_ajoute_un_bloc():
    document = Document(document=document_pdf)
    position_bloc_1 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)

    document.ajoute_bloc_a_la_page(
        1, position_bloc_1, "[TEXTE] Un paragraphe en seconde position"
    )
    document.ajoute_bloc_a_la_page(
        1, position_bloc_2, "[TEXTE] Un paragraphe en première position"
    )

    assert len(document.pages) == 1
    assert (
        document.pages[1].blocs[0].texte == "[TEXTE] Un paragraphe en première position"
    )
    assert (
        document.pages[1].blocs[1].texte == "[TEXTE] Un paragraphe en seconde position"
    )


def test_document_fusionne_un_titre_avec_son_contenu():
    document = Document(document=document_pdf)
    position_bloc_1 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0)
    position_bloc_3 = Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0)
    position_bloc_4 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_5 = Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0)

    document.ajoute_bloc_a_la_page(1, position_bloc_1, "[TITRE] Titre 1")
    document.ajoute_bloc_a_la_page(1, position_bloc_2, "[TITRE] Titre 2")
    document.ajoute_bloc_a_la_page(1, position_bloc_3, "[TEXTE] Contenu 1.")
    document.ajoute_bloc_a_la_page(1, position_bloc_4, "[TEXTE] Contenu 2.")
    document.ajoute_bloc_a_la_page(1, position_bloc_5, "[SOUS-TITRE] 1.1 Sous-titre.")

    assert len(document.pages[1].blocs) == 3
    assert document.pages[1].blocs[0].texte == "[TITRE] Titre 1"
    assert (
        document.pages[1].blocs[1].texte
        == "[TITRE] Titre 2\n[TEXTE] Contenu 1.\n[TEXTE] Contenu 2."
    )
    assert document.pages[1].blocs[2].texte == "[SOUS-TITRE] 1.1 Sous-titre."


def test_document_fusionne_un_titre_avec_son_contenu_qui_contient_des_recommandations():
    document = Document(document=document_pdf)
    position_bloc_1 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0)
    position_bloc_3 = Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0)
    position_bloc_4 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_5 = Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0)

    document.ajoute_bloc_a_la_page(1, position_bloc_1, "[TITRE] Titre")
    document.ajoute_bloc_a_la_page(1, position_bloc_2, "[RECOMMANDATION] R1")
    document.ajoute_bloc_a_la_page(1, position_bloc_3, "[TEXTE] Recommandation 1.")
    document.ajoute_bloc_a_la_page(1, position_bloc_4, "[RECOMMANDATION] R2")
    document.ajoute_bloc_a_la_page(1, position_bloc_5, "[TEXTE] Recommandation 2.")

    assert len(document.pages[1].blocs) == 1
    assert (
        document.pages[1].blocs[0].texte
        == "[TITRE] Titre\n[RECOMMANDATION] R1\n[TEXTE] Recommandation 1.\n[RECOMMANDATION] R2\n[TEXTE] Recommandation 2."
    )


def test_document_fusionne_tous_les_contenus_d_un_sous_titre():
    document = Document(document=document_pdf)
    position_bloc_1 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0)
    position_bloc_3 = Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0)
    position_bloc_4 = Position(x=10.0, y=5.0, largeur=100.0, hauteur=5.0)

    document.ajoute_bloc_a_la_page(1, position_bloc_1, "[SOUS-TITRE] 1.2 Sous-titre 1")
    document.ajoute_bloc_a_la_page(1, position_bloc_2, "[TEXTE] Paragraphe 1.")
    document.ajoute_bloc_a_la_page(1, position_bloc_3, "[TEXTE] Paragraphe 2.")
    document.ajoute_bloc_a_la_page(1, position_bloc_4, "[TEXTE] Paragraphe 3.")

    assert len(document.pages[1].blocs) == 1
    assert (
        document.pages[1].blocs[0].texte
        == "[SOUS-TITRE] 1.2 Sous-titre 1\n[TEXTE] Paragraphe 1.\n[TEXTE] Paragraphe 2.\n[TEXTE] Paragraphe 3."
    )


@pytest.mark.parametrize(
    "_description, textes, attendu",
    [
        (
            "d’un titre",
            [
                (
                    Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0),
                    "[TITRE] Titre",
                ),
                (
                    Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0),
                    "[RECOMMANDATION] R1",
                ),
                (
                    Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0),
                    "[TEXTE] Recommandation 1.",
                ),
                (
                    Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0),
                    "[RECOMMANDATION] R2",
                ),
                (
                    Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0),
                    "[TEXTE] Recommandation 2.",
                ),
            ],
            "[TITRE] Titre\n[RECOMMANDATION] R1\n[TEXTE] Recommandation 1.\n[RECOMMANDATION] R2\n[TEXTE] Recommandation 2.",
        ),
        (
            "d’un sous titre",
            [
                (
                    Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0),
                    "[SOUS-TITRE] Sous-Titre",
                ),
                (
                    Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0),
                    "[RECOMMANDATION] R1",
                ),
                (
                    Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0),
                    "[TEXTE] Recommandation 1.",
                ),
                (
                    Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0),
                    "[RECOMMANDATION] R2",
                ),
                (
                    Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0),
                    "[TEXTE] Recommandation 2.",
                ),
            ],
            "[SOUS-TITRE] Sous-Titre\n[RECOMMANDATION] R1\n[TEXTE] Recommandation 1.\n[RECOMMANDATION] R2\n[TEXTE] Recommandation 2.",
        ),
    ],
)
def test_document_fusionne_les_recommandations(_description, textes, attendu):
    document = Document(document=document_pdf)

    for texte in textes:
        document.ajoute_bloc_a_la_page(1, texte[0], texte[1])

    assert len(document.pages[1].blocs) == 1
    assert document.pages[1].blocs[0].texte == attendu


@pytest.mark.parametrize(
    "_description, textes, attendu",
    [
        (
            "d’un titre",
            [
                (
                    Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0),
                    "[TITRE] Titre",
                ),
                (
                    Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0),
                    "[TABLEAU] Un tableau",
                ),
                (
                    Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0),
                    "[TEXTE] Un texte.",
                ),
                (
                    Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0),
                    "[TABLEAU] Un autre tableau",
                ),
                (
                    Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0),
                    "[TEXTE] Un autre texte.",
                ),
            ],
            "[TITRE] Titre\n[TABLEAU] Un tableau\n[TEXTE] Un texte.\n[TABLEAU] Un autre tableau\n[TEXTE] Un autre texte.",
        ),
        (
            "d’un sous titre",
            [
                (
                    Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0),
                    "[SOUS-TITRE] Sous-Titre",
                ),
                (
                    Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0),
                    "[TABLEAU] un tableau",
                ),
                (
                    Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0),
                    "[TEXTE] Un texte.",
                ),
                (
                    Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0),
                    "[TABLEAU] un autre tableau",
                ),
                (
                    Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0),
                    "[TEXTE] Un autre texte.",
                ),
            ],
            "[SOUS-TITRE] Sous-Titre\n[TABLEAU] un tableau\n[TEXTE] Un texte.\n[TABLEAU] un autre tableau\n[TEXTE] Un autre texte.",
        ),
    ],
)
def test_document_fusionne_les_tableaux(_description, textes, attendu):
    document = Document(document=document_pdf)

    for texte in textes:
        document.ajoute_bloc_a_la_page(1, texte[0], texte[1])

    assert len(document.pages[1].blocs) == 1
    assert document.pages[1].blocs[0].texte == attendu
