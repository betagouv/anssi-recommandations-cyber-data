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
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    assert document is not None


def test_pages_a_une_collection_de_pages_vide_par_defaut():
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    assert document.pages == {}


def test_document_peut_ajouter_un_bloc_dans_une_page(un_constructeur_de_base_chunk):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    position = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)

    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position)
            .avec_le_texte("[TEXTE] Une page")
            .construis()
        )
    )

    assert len(document.pages) == 1
    assert document.pages[1] == PagePDF(
        numero_page=1, blocs=[BlocPage(texte="[TEXTE] Une page", position=position)]
    )


def test_document_peut_ajouter_deux_blocs_sur_une_meme_page(
    un_constructeur_de_base_chunk,
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    position_bloc_1 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=0.0, largeur=100.0, hauteur=5.0)

    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_1)
            .avec_le_texte("[TEXTE] Un titre")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_2)
            .avec_le_texte("[TEXTE] Un paragraphe")
            .construis()
        )
    )

    assert len(document.pages) == 1
    assert document.pages[1].blocs[0].texte == "[TEXTE] Un titre"
    assert document.pages[1].blocs[1].texte == "[TEXTE] Un paragraphe"


def test_document_reordonne_lorsque_l_on_ajoute_un_bloc(un_constructeur_de_base_chunk):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    position_bloc_1 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)

    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_1)
            .avec_le_texte("[TEXTE] Un paragraphe en seconde position")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_2)
            .avec_le_texte("[TEXTE] Un paragraphe en première position")
            .construis()
        )
    )

    assert len(document.pages) == 1
    assert (
        document.pages[1].blocs[0].texte == "[TEXTE] Un paragraphe en première position"
    )
    assert (
        document.pages[1].blocs[1].texte == "[TEXTE] Un paragraphe en seconde position"
    )


def test_document_fusionne_un_titre_avec_son_contenu(un_constructeur_de_base_chunk):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    position_bloc_1 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0)
    position_bloc_3 = Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0)
    position_bloc_4 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_5 = Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0)

    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_1)
            .avec_le_texte("[TITRE] Titre 1")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_2)
            .avec_le_texte("[TITRE] Titre 2")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_3)
            .avec_le_texte("[TEXTE] Contenu 1.")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_4)
            .avec_le_texte("[TEXTE] Contenu 2.")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_5)
            .avec_le_texte("[SOUS-TITRE] 1.1 Sous-titre.")
            .construis()
        )
    )

    assert len(document.pages[1].blocs) == 3
    assert document.pages[1].blocs[0].texte == "[TITRE] Titre 1"
    assert (
        document.pages[1].blocs[1].texte
        == "[TITRE] Titre 2\n[TEXTE] Contenu 1.\n[TEXTE] Contenu 2."
    )
    assert document.pages[1].blocs[2].texte == "[SOUS-TITRE] 1.1 Sous-titre."


def test_document_fusionne_un_titre_avec_son_contenu_qui_contient_des_recommandations(
    un_constructeur_de_base_chunk,
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    position_bloc_1 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=40.0, largeur=100.0, hauteur=5.0)
    position_bloc_3 = Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0)
    position_bloc_4 = Position(x=10.0, y=20.0, largeur=100.0, hauteur=5.0)
    position_bloc_5 = Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0)

    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_1)
            .avec_le_texte("[TITRE] Titre")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_2)
            .avec_le_texte("[RECOMMANDATION] R1")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_3)
            .avec_le_texte("[TEXTE] Recommandation 1.")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_4)
            .avec_le_texte("[RECOMMANDATION] R2")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_5)
            .avec_le_texte("[TEXTE] Recommandation 2.")
            .construis()
        )
    )

    assert len(document.pages[1].blocs) == 1
    assert (
        document.pages[1].blocs[0].texte
        == "[TITRE] Titre\n[RECOMMANDATION] R1\n[TEXTE] Recommandation 1.\n[RECOMMANDATION] R2\n[TEXTE] Recommandation 2."
    )


def test_document_fusionne_tous_les_contenus_d_un_sous_titre(
    un_constructeur_de_base_chunk,
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    position_bloc_1 = Position(x=10.0, y=50.0, largeur=100.0, hauteur=5.0)
    position_bloc_2 = Position(x=10.0, y=30.0, largeur=100.0, hauteur=5.0)
    position_bloc_3 = Position(x=10.0, y=10.0, largeur=100.0, hauteur=5.0)
    position_bloc_4 = Position(x=10.0, y=5.0, largeur=100.0, hauteur=5.0)

    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_1)
            .avec_le_texte("[SOUS-TITRE] 1.2 Sous-titre 1")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_2)
            .avec_le_texte("[TEXTE] Paragraphe 1.")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_3)
            .avec_le_texte("[TEXTE] Paragraphe 2.")
            .construis()
        )
    )
    document.ajoute(
        document_pdf.generateur.genere(
            un_constructeur_de_base_chunk()
            .a_la_page(1)
            .a_la_position(position_bloc_4)
            .avec_le_texte("[TEXTE] Paragraphe 3.")
            .construis()
        )
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
def test_document_fusionne_les_recommandations(
    _description, textes, attendu, un_constructeur_de_base_chunk
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)

    for texte in textes:
        document.ajoute(
            document_pdf.generateur.genere(
                un_constructeur_de_base_chunk()
                .a_la_page(1)
                .a_la_position(texte[0])
                .avec_le_texte(texte[1])
                .construis()
            )
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
def test_document_fusionne_les_tableaux(
    _description, textes, attendu, un_constructeur_de_base_chunk
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)

    for texte in textes:
        document.ajoute(
            document_pdf.generateur.genere(
                un_constructeur_de_base_chunk()
                .a_la_page(1)
                .a_la_position(texte[0])
                .avec_le_texte(texte[1])
                .construis()
            )
        )

    assert len(document.pages[1].blocs) == 1
    assert document.pages[1].blocs[0].texte == attendu
