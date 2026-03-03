from documents.chunker_docling import TypeFichier
from documents.chunker_docling_mqc import ChunkerDoclingMQC
from documents.html.document_html import DocumentHTML
from documents.pdf.document_pdf import DocumentPDF


def test_retourne_le_document(un_convertisseur_avec_un_texte):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")

    document = ChunkerDoclingMQC(un_convertisseur_avec_un_texte()).applique(
        document=document
    )

    assert len(document.pages) == 1
    assert document.pages[1].numero_page == 1
    assert document.pages[1].blocs[0].texte == "[TEXTE] Un texte"


def test_retourne_le_document_en_tenant_compte_de_l_ordre_des_bbox(
    un_convertisseur_avec_deux_bbox,
):
    document = DocumentPDF(
        "mon_document_ave_bbox.pdf", url_pdf="http://mon-document-bbox.pdf"
    )

    document = ChunkerDoclingMQC(un_convertisseur_avec_deux_bbox()).applique(
        document=document
    )

    assert len(document.pages) == 1
    assert document.pages[1].numero_page == 1
    assert document.pages[1].blocs[0].texte == "[TEXTE] Texte première bbox"
    assert document.pages[1].numero_page == 1
    assert document.pages[1].blocs[1].texte == "[TEXTE] Texte seconde bbox"


def test_retourne_le_document_et_ordonne_sans_bbox(
    un_convertisseur_avec_deux_textes_dont_un_sans_bbox,
):
    document = DocumentPDF(
        "mon_document_ave_bbox.pdf", url_pdf="http://mon-document-bbox.pdf"
    )

    document = ChunkerDoclingMQC(
        un_convertisseur_avec_deux_textes_dont_un_sans_bbox()
    ).applique(document=document)

    assert document.pages[1].numero_page == 1
    assert document.pages[1].blocs[0].texte == "[TEXTE] Texte première bbox"
    assert document.pages[1].numero_page == 1
    assert document.pages[1].blocs[1].texte == "[TEXTE] Texte en seconde position"


def test_fusionne_entetes_avec_contenu_simple(
    un_convertisseur_avec_un_titre_et_un_texte,
):
    document = DocumentPDF(
        "mon_document_ave_bbox.pdf", url_pdf="http://mon-document-bbox.pdf"
    )

    document = ChunkerDoclingMQC(un_convertisseur_avec_un_titre_et_un_texte()).applique(
        document=document
    )

    assert len(document.pages[1].blocs) == 1
    assert (
        document.pages[1].blocs[0].texte
        == "[TITRE] Titre\n[TEXTE] Contenu du paragraphe."
    )


def test_le_document_retourne_le_nom_du_document(
    fichier_pdf, un_convertisseur_avec_un_texte
):
    chemin_fichier_de_test = str(fichier_pdf("document_mqc.pdf").resolve())
    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")

    document = ChunkerDoclingMQC(un_convertisseur_avec_un_texte()).applique(
        document=document
    )

    assert document.nom_document == "document_mqc.pdf"


def test_retourne_le_nom_du_fichier(fichier_pdf, un_convertisseur_avec_un_texte):
    chemin_fichier_de_test = str(fichier_pdf("document_mqc.pdf").resolve())
    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")

    chunker = ChunkerDoclingMQC(un_convertisseur_avec_un_texte())
    chunker.applique(document=document)

    assert chunker.nom_fichier == "document_mqc.txt"


def test_retourne_le_type_du_fichier():
    chunker = ChunkerDoclingMQC()

    assert chunker.type_fichier == TypeFichier.TEXTE


def test_prend_en_compte_un_document_html(un_convertisseur_de_test):
    document_html = DocumentHTML("Mon document", "http://mon-document.local/index.html")

    chunker = ChunkerDoclingMQC(un_convertisseur_de_test())
    document = chunker.applique(document=document_html)

    assert chunker.converter.document_recu == "http://mon-document.local/index.html"
    assert chunker.nom_fichier == "index.txt"
    assert len(document.pages) == 1
