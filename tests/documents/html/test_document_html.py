from documents.docling.document import Document
from documents.html.document_html import BlocPageHTML, PageHTML, DocumentHTML


def test_page_peut_creer_une_page():
    page = PageHTML()

    assert page is not None
    assert page.blocs == []
    assert page.numero_page is None


def test_peut_creer_un_document_avec_du_contenu_issu_d_une_page_html(
    un_constructeur_d_element_filtrable,
):
    nom_document = "test.html"
    url_document = "https://mon-document.local/test.html"
    document = Document(nom_document=nom_document, url=url_document)

    document_html = DocumentHTML(nom_document, url_document)
    document.genere_les_pages(
        document_html.generateur,
        [
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_texte("Un texte")
            .construis()
        ],
    )

    assert document is not None
    assert len(document.pages) == 1
    assert document.pages[0] == PageHTML(blocs=[BlocPageHTML(texte="Un texte")])


def test_peut_creer_un_document_avec_les_differentes_sections(
    un_constructeur_d_element_filtrable,
):
    nom_document = "test.html"
    url_document = "https://mon-document.local/test.html"
    document = Document(nom_document=nom_document, url=url_document)

    document_html = DocumentHTML(nom_document, url_document)
    document.genere_les_pages(
        document_html.generateur,
        [
            un_constructeur_d_element_filtrable()
            .de_type_header()
            .avec_texte("Un titre")
            .ayant_les_enfants(["enf/1", "enf/2", "enf/3"])
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_texte("Un sous-titre")
            .portant_la_reference("enf/1")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_texte("Un premier paragraphe")
            .portant_la_reference("enf/2")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_texte("Un deuxième paragraphe")
            .portant_la_reference("enf/3")
            .construis(),
        ],
    )

    assert document is not None
    assert len(document.pages) == 1
    assert document.pages[0] == PageHTML(
        blocs=[
            BlocPageHTML(
                texte="Un titre\nUn sous-titre\nUn premier paragraphe\nUn deuxième paragraphe"
            )
        ]
    )


def test_peut_creer_un_document_avec_les_contenus_adjacents(
    un_constructeur_d_element_filtrable,
):
    nom_document = "test.html"
    url_document = "https://mon-document.local/test.html"
    document = Document(nom_document=nom_document, url=url_document)

    document_html = DocumentHTML(nom_document, url_document)
    document.genere_les_pages(
        document_html.generateur,
        [
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_texte("Un premier paragraphe")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_texte("Un deuxième paragraphe")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_texte("Un troisième paragraphe")
            .construis(),
        ],
    )

    assert document is not None
    assert len(document.pages) == 1
    assert document.pages[0] == PageHTML(
        blocs=[
            BlocPageHTML(
                texte="Un premier paragraphe\nUn deuxième paragraphe\nUn troisième paragraphe"
            )
        ]
    )


def test_peut_creer_un_document_avec_des_tableaux(
    un_constructeur_d_element_filtrable,
):
    nom_document = "test.html"
    url_document = "https://mon-document.local/test.html"
    document = Document(nom_document=nom_document, url=url_document)

    document_html = DocumentHTML(nom_document, url_document)
    document.genere_les_pages(
        document_html.generateur,
        [
            un_constructeur_d_element_filtrable()
            .de_type_header()
            .avec_texte("Des tableaux")
            .ayant_les_enfants(["tableau/1", "tableau/2"])
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_tableau()
            .portant_la_reference("tableau/1")
            .avec_texte("Un premier tableau")
            .avec_une_cellule("Une cellule dans tableau 1")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_tableau()
            .portant_la_reference("tableau/2")
            .avec_texte("Un deuxième tableau")
            .avec_une_cellule("Une cellule dans tableau 2")
            .construis(),
        ],
    )

    assert document is not None
    assert len(document.pages) == 1
    assert document.pages[0] == PageHTML(
        blocs=[
            BlocPageHTML(
                texte="Des tableaux\n"
                "| Un premier tableau         |\n|----------------------------|\n"
                "| Une cellule dans tableau 1 |\n"
                "| Un deuxième tableau        |\n|----------------------------|\n"
                "| Une cellule dans tableau 2 |"
            )
        ]
    )


def test_peut_créer_un_document_avec_des_tableaux_sous_un_titre(
    un_constructeur_d_element_filtrable,
):
    nom_document = "test.html"
    url_document = "https://mon-document.local/test.html"
    document = Document(nom_document=nom_document, url=url_document)

    document_html = DocumentHTML(nom_document, url_document)
    document.genere_les_pages(
        document_html.generateur,
        [
            un_constructeur_d_element_filtrable()
            .de_type_titre()
            .avec_texte("Des tableaux")
            .ayant_les_enfants(["tableau/1", "tableau/2"])
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_tableau()
            .portant_la_reference("tableau/1")
            .avec_texte("Un premier tableau")
            .avec_une_cellule("Une cellule dans tableau 1")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_tableau()
            .portant_la_reference("tableau/2")
            .avec_texte("Un deuxième tableau")
            .avec_une_cellule("Une cellule dans tableau 2")
            .construis(),
        ],
    )

    assert document is not None
    assert len(document.pages) == 1
    assert document.pages[0] == PageHTML(
        blocs=[
            BlocPageHTML(
                texte="Des tableaux\n"
                "| Un premier tableau         |\n|----------------------------|\n"
                "| Une cellule dans tableau 1 |\n"
                "| Un deuxième tableau        |\n|----------------------------|\n"
                "| Une cellule dans tableau 2 |"
            )
        ]
    )
