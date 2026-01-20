from guides.chunker_docling import TypeFichier
from guides.chunker_docling_mqc import ChunkerDoclingMQC
from guides.indexeur import DocumentPDF


def test_retourne_le_guide(un_convertisseur_avec_un_texte):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")

    guide = ChunkerDoclingMQC(un_convertisseur_avec_un_texte()).applique(
        document=document
    )

    assert len(guide.pages) == 1
    assert guide.pages[1].numero_page == 1
    assert guide.pages[1].blocs[0].texte == "[TEXTE] Un texte"


def test_retourne_le_guide_en_tenant_compte_de_l_ordre_des_bbox(
    un_convertisseur_avec_deux_bbox,
):
    document = DocumentPDF(
        "mon_document_ave_bbox.pdf", url_pdf="http://mon-document-bbox.pdf"
    )

    guide = ChunkerDoclingMQC(un_convertisseur_avec_deux_bbox()).applique(
        document=document
    )

    assert len(guide.pages) == 1
    assert guide.pages[1].numero_page == 1
    assert guide.pages[1].blocs[0].texte == "[TEXTE] Texte première bbox"
    assert guide.pages[1].numero_page == 1
    assert guide.pages[1].blocs[1].texte == "[TEXTE] Texte seconde bbox"


def test_retourne_le_guide_et_ordonne_sans_bbox(
    un_convertisseur_avec_deux_textes_dont_un_sans_bbox,
):
    document = DocumentPDF(
        "mon_document_ave_bbox.pdf", url_pdf="http://mon-document-bbox.pdf"
    )

    guide = ChunkerDoclingMQC(
        un_convertisseur_avec_deux_textes_dont_un_sans_bbox()
    ).applique(document=document)

    assert guide.pages[1].numero_page == 1
    assert guide.pages[1].blocs[0].texte == "[TEXTE] Texte première bbox"
    assert guide.pages[1].numero_page == 1
    assert guide.pages[1].blocs[1].texte == "[TEXTE] Texte en seconde position"


def test_fusionne_entetes_avec_contenu_simple(
    un_convertisseur_avec_un_titre_et_un_texte,
):
    document = DocumentPDF(
        "mon_document_ave_bbox.pdf", url_pdf="http://mon-document-bbox.pdf"
    )

    guide = ChunkerDoclingMQC(un_convertisseur_avec_un_titre_et_un_texte()).applique(
        document=document
    )

    assert len(guide.pages[1].blocs) == 1
    assert (
        guide.pages[1].blocs[0].texte == "[TITRE] Titre\n[TEXTE] Contenu du paragraphe."
    )


def test_le_guide_retourne_le_nom_du_document(
    fichier_pdf, un_convertisseur_avec_un_texte
):
    chemin_fichier_de_test = str(fichier_pdf("document_mqc.pdf").resolve())
    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")

    guide = ChunkerDoclingMQC(un_convertisseur_avec_un_texte()).applique(
        document=document
    )

    assert guide.nom_document == "document_mqc.pdf"


def test_retourne_le_nom_du_fichier(fichier_pdf, un_convertisseur_avec_un_texte):
    chemin_fichier_de_test = str(fichier_pdf("document_mqc.pdf").resolve())
    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")

    chunker = ChunkerDoclingMQC(un_convertisseur_avec_un_texte())
    chunker.applique(document=document)

    assert chunker.nom_fichier == "document_mqc.txt"


def test_retourne_le_type_du_fichier():
    chunker = ChunkerDoclingMQC()

    assert chunker.type_fichier == TypeFichier.TEXTE
