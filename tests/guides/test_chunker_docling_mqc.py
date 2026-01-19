from guides.chunker_docling_mqc import ChunkerDoclingMQC
from guides.indexeur import DocumentPDF


def test_retourne_le_guide(un_convertisseur_avec_un_texte):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")

    guide = ChunkerDoclingMQC().applique(
        document=document, converter=un_convertisseur_avec_un_texte()
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

    guide = ChunkerDoclingMQC().applique(
        document=document, converter=un_convertisseur_avec_deux_bbox()
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

    guide = ChunkerDoclingMQC().applique(
        document=document,
        converter=un_convertisseur_avec_deux_textes_dont_un_sans_bbox(),
    )

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

    guide = ChunkerDoclingMQC().applique(
        document=document,
        converter=un_convertisseur_avec_un_titre_et_un_texte(),
    )

    assert len(guide.pages[1].blocs) == 1
    assert (
        guide.pages[1].blocs[0].texte == "[TITRE] Titre\n[TEXTE] Contenu du paragraphe."
    )
