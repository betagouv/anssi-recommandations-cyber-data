from pathlib import Path

import pytest

from documents.docling.document import Document
from documents.pdf.document_pdf import DocumentPDF, PagePDF, BlocPagePDF

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
    bloc = BlocPagePDF(texte="Mon texte", numero_page=1)
    page.ajoute_bloc(bloc)
    assert len(page.blocs) == 1
    assert page.blocs[0] == bloc


def test_pages_peut_etre_creee():
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    assert document is not None


def test_pages_a_une_collection_de_pages_vide_par_defaut():
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    assert document.pages == {}


def test_document_pdf_cree_correctement():
    doc = DocumentPDF("chemin/vers/fichier.pdf", "https://example.com/fichier.pdf")
    assert doc.chemin == Path("chemin/vers/fichier.pdf")
    assert doc.url == "https://example.com/fichier.pdf"


def test_generateur_produit_un_bloc_par_texte_sans_header(
    un_constructeur_d_element_filtrable,
    resultat_conversion,
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_numero_page(1)
            .avec_texte("Mon texte")
            .construis()
        ],
        resultat_conversion.document,
    )
    assert len(document.pages) == 1
    assert document.pages[1].blocs[0].numero_page == 1
    assert document.pages[1].blocs[0].texte == "Mon texte"


def test_generateur_groupe_les_textes_sous_leur_header(
    un_constructeur_d_element_filtrable,
    resultat_conversion,
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_d_element_filtrable()
            .de_type_header()
            .avec_numero_page(1)
            .avec_titre("Section 1")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_numero_page(1)
            .avec_texte("Contenu 1")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_numero_page(1)
            .avec_texte("Contenu 2")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_header()
            .avec_numero_page(1)
            .avec_titre("Section 2")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_numero_page(1)
            .avec_texte("Contenu 3")
            .construis(),
        ],
        resultat_conversion.document,
    )
    assert len(document.pages[1].blocs) == 2
    assert document.pages[1].blocs[0].texte == "Section 1\nContenu 1\nContenu 2"
    assert document.pages[1].blocs[1].texte == "Section 2\nContenu 3"


@pytest.mark.skip(reason="à implémenter plus tard")
def test_generateur_groupe_les_textes_titre_et_sous_titre_avec_texte(
    un_constructeur_d_element_filtrable,
    resultat_conversion,
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_d_element_filtrable()
            .de_type_header()
            .avec_numero_page(1)
            .avec_titre("Section 1")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_header()
            .avec_numero_page(1)
            .avec_titre("Sous section 1.1")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_numero_page(1)
            .avec_texte("Contenu 1")
            .construis(),
        ],
        resultat_conversion.document,
    )
    assert len(document.pages[1].blocs) == 1
    assert document.pages[1].blocs[0].texte == "Section 1\nSous section 1.1\nContenu 1"


def test_generateur_cree_un_bloc_par_header_sans_contenu(
    un_constructeur_d_element_filtrable,
    resultat_conversion,
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_d_element_filtrable()
            .de_type_header()
            .avec_numero_page(1)
            .avec_titre("Section A")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_header()
            .avec_numero_page(1)
            .avec_titre("Section B")
            .construis(),
        ],
        resultat_conversion.document,
    )
    assert len(document.pages[1].blocs) == 2
    assert document.pages[1].blocs[0].texte == "Section A"
    assert document.pages[1].blocs[1].texte == "Section B"


def test_generateur_gere_les_pages_multiples(
    un_constructeur_d_element_filtrable,
    resultat_conversion,
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_d_element_filtrable()
            .de_type_header()
            .avec_numero_page(1)
            .avec_titre("Section page 1")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_numero_page(1)
            .avec_texte("Contenu page 1")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_header()
            .avec_numero_page(2)
            .avec_titre("Section page 2")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_texte()
            .avec_numero_page(2)
            .avec_texte("Contenu page 2")
            .construis(),
        ],
        resultat_conversion.document,
    )
    assert 1 in document.pages
    assert 2 in document.pages
    assert document.pages[1].blocs[0].texte == "Section page 1\nContenu page 1"
    assert document.pages[2].blocs[0].texte == "Section page 2\nContenu page 2"


def test_generateur_groupe_les_tableaux_sous_leur_header(
    un_constructeur_d_element_filtrable,
    resultat_conversion,
):
    document = Document(nom_document=document_pdf.nom_document, url=document_pdf.url)
    document.genere_les_pages(
        document_pdf.generateur,
        [
            un_constructeur_d_element_filtrable()
            .de_type_header()
            .avec_numero_page(1)
            .avec_titre("Section avec tableau")
            .construis(),
            un_constructeur_d_element_filtrable()
            .de_type_tableau()
            .avec_numero_page(1)
            .avec_texte("Une cellule")
            .construis(),
        ],
        resultat_conversion.document,
    )
    assert len(document.pages[1].blocs) == 1
    assert document.pages[1].blocs[0].texte.startswith("Section avec tableau\n")
    assert "Une cellule" in document.pages[1].blocs[0].texte
