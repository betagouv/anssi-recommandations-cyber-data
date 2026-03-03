import pytest
from docling_core.types.doc import DocItemLabel

from documents.document import (
    Document,
)
from documents.pdf.document_pdf import DocumentPDF, PagePDF, Position, BlocPagePDF

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
    bloc = BlocPagePDF(texte="[TEXTE] Mon texte", position=position)

    page.ajoute_bloc(bloc)

    assert len(page.blocs) == 1
    assert page.blocs[0] == bloc


def test_pages_peut_etre_creee():
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    assert document is not None


def test_pages_a_une_collection_de_pages_vide_par_defaut():
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    assert document.pages == {}


def test_document_peut_ajouter_un_bloc_dans_une_page(un_constructeur_de_text_item):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    position = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)

    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position)
            .avec_texte("Une page")
            .construis()
        ],
    )

    assert len(document.pages) == 1
    assert document.pages[1] == PagePDF(
        numero_page=1, blocs=[BlocPagePDF(texte="[TEXTE] Une page", position=position)]
    )


def test_document_peut_ajouter_deux_blocs_sur_une_meme_page(
    un_constructeur_de_text_item,
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    position_bloc_1 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=0.0, largeur=100.0, hauteur=5.0)

    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_1)
            .avec_texte("Un titre")
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_2)
            .avec_texte("Un paragraphe")
            .construis(),
        ],
    )

    assert len(document.pages) == 1
    assert document.pages[1].blocs[0].texte == "[TEXTE] Un titre"
    assert document.pages[1].blocs[1].texte == "[TEXTE] Un paragraphe"


def test_document_reordonne_lorsque_l_on_ajoute_un_bloc(un_constructeur_de_text_item):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    position_bloc_1 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)

    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_1)
            .avec_texte("Un paragraphe en seconde position")
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_2)
            .avec_texte("Un paragraphe en première position")
            .construis(),
        ],
    )

    assert len(document.pages) == 1
    assert (
        document.pages[1].blocs[0].texte == "[TEXTE] Un paragraphe en première position"
    )
    assert (
        document.pages[1].blocs[1].texte == "[TEXTE] Un paragraphe en seconde position"
    )


def test_document_fusionne_un_titre_avec_son_contenu(un_constructeur_de_text_item):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    position_bloc_1 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0)
    position_bloc_3 = Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0)
    position_bloc_4 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_5 = Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0)

    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_1)
            .avec_texte("Titre 1")
            .de_type_header()
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_2)
            .avec_texte("Titre 2")
            .de_type_header()
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_3)
            .avec_texte("Contenu 1.")
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_4)
            .avec_texte("Contenu 2.")
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_5)
            .avec_texte("1.1 Sous-titre.")
            .de_type_header()
            .construis(),
        ],
    )

    assert len(document.pages[1].blocs) == 3
    assert document.pages[1].blocs[0].texte == "[TITRE] Titre 1"
    assert (
        document.pages[1].blocs[1].texte
        == "[TITRE] Titre 2\n[TEXTE] Contenu 1.\n[TEXTE] Contenu 2."
    )
    assert document.pages[1].blocs[2].texte == "[SOUS-TITRE] 1.1 Sous-titre."


def test_document_fusionne_un_titre_avec_son_contenu_qui_contient_des_recommandations(
    un_constructeur_de_text_item,
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    position_bloc_1 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0)
    position_bloc_3 = Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0)
    position_bloc_4 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_5 = Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0)

    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_1)
            .avec_texte("Titre")
            .de_type_header()
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_2)
            .avec_texte("R1")
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_3)
            .avec_texte("Recommandation 1.")
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_4)
            .avec_texte("R2")
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_5)
            .avec_texte("Recommandation 2.")
            .construis(),
        ],
    )

    assert len(document.pages[1].blocs) == 1
    assert (
        document.pages[1].blocs[0].texte
        == "[TITRE] Titre\n[RECOMMANDATION] R1\n[TEXTE] Recommandation 1.\n[RECOMMANDATION] R2\n[TEXTE] Recommandation 2."
    )


def test_document_fusionne_tous_les_contenus_d_un_sous_titre(
    un_constructeur_de_text_item,
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    position_bloc_1 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0)
    position_bloc_3 = Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0)
    position_bloc_4 = Position(x=10.0, y=5.0, largeur=100.0, hauteur=5.0)

    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_1)
            .avec_texte("1.2 Sous-titre 1")
            .de_type_header()
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_2)
            .avec_texte("Paragraphe 1.")
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_3)
            .avec_texte("Paragraphe 2.")
            .construis(),
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(position_bloc_4)
            .avec_texte("Paragraphe 3.")
            .construis(),
        ],
    )

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
                    DocItemLabel.SECTION_HEADER,
                    Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0),
                    "Titre",
                ),
                (
                    DocItemLabel.TEXT,
                    Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0),
                    "R1",
                ),
                (
                    DocItemLabel.TEXT,
                    Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0),
                    "Recommandation 1.",
                ),
                (
                    DocItemLabel.TEXT,
                    Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0),
                    "R2",
                ),
                (
                    DocItemLabel.TEXT,
                    Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0),
                    "Recommandation 2.",
                ),
            ],
            "[TITRE] Titre\n[RECOMMANDATION] R1\n[TEXTE] Recommandation 1.\n[RECOMMANDATION] R2\n[TEXTE] Recommandation 2.",
        ),
        (
            "d’un sous titre",
            [
                (
                    DocItemLabel.SECTION_HEADER,
                    Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0),
                    "1.1 Sous-Titre",
                ),
                (
                    DocItemLabel.TEXT,
                    Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0),
                    "R1",
                ),
                (
                    DocItemLabel.TEXT,
                    Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0),
                    "Recommandation 1.",
                ),
                (
                    DocItemLabel.TEXT,
                    Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0),
                    "R2",
                ),
                (
                    DocItemLabel.TEXT,
                    Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0),
                    "Recommandation 2.",
                ),
            ],
            "[SOUS-TITRE] 1.1 Sous-Titre\n[RECOMMANDATION] R1\n[TEXTE] Recommandation 1.\n[RECOMMANDATION] R2\n[TEXTE] Recommandation 2.",
        ),
    ],
)
def test_document_fusionne_les_recommandations(
    _description, textes, attendu, un_constructeur_de_text_item
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)

    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(texte[1])
            .avec_texte(texte[2])
            .de_type(texte[0])
            .construis()
            for texte in textes
        ],
    )

    assert len(document.pages[1].blocs) == 1
    assert document.pages[1].blocs[0].texte == attendu


@pytest.mark.parametrize(
    "_description, textes, attendu",
    [
        (
            "d’un titre",
            [
                (
                    DocItemLabel.SECTION_HEADER,
                    Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0),
                    "Titre",
                ),
                (
                    DocItemLabel.TABLE,
                    Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0),
                    "Un tableau",
                ),
                (
                    DocItemLabel.TEXT,
                    Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0),
                    "Un texte.",
                ),
                (
                    DocItemLabel.TABLE,
                    Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0),
                    "Un autre tableau",
                ),
                (
                    DocItemLabel.TEXT,
                    Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0),
                    "Un autre texte.",
                ),
            ],
            "[TITRE] Titre\n[TABLEAU]\n| Un tableau |\n[TEXTE] Un texte.\n[TABLEAU]\n| Un autre tableau |\n[TEXTE] Un autre texte.",
        ),
        (
            "d’un sous titre",
            [
                (
                    DocItemLabel.SECTION_HEADER,
                    Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0),
                    "1.1 Sous-Titre",
                ),
                (
                    DocItemLabel.TABLE,
                    Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0),
                    "un tableau",
                ),
                (
                    DocItemLabel.TEXT,
                    Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0),
                    "Un texte.",
                ),
                (
                    DocItemLabel.TABLE,
                    Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0),
                    "un autre tableau",
                ),
                (
                    DocItemLabel.TEXT,
                    Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0),
                    "Un autre texte.",
                ),
            ],
            "[SOUS-TITRE] 1.1 Sous-Titre\n[TABLEAU]\n| un tableau |\n[TEXTE] Un texte.\n[TABLEAU]\n| un autre tableau |\n[TEXTE] Un autre texte.",
        ),
    ],
)
def test_document_fusionne_les_tableaux(
    _description, textes, attendu, un_constructeur_de_text_item
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)

    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_de_text_item()
            .avec_numero_page(1)
            .a_la_position(texte[1])
            .avec_texte(texte[2])
            .de_type(texte[0])
            .construis()
            for texte in textes
        ],
    )

    assert len(document.pages[1].blocs) == 1
    assert document.pages[1].blocs[0].texte == attendu
