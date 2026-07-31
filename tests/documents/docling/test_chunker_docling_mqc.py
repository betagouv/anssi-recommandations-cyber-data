import pytest

from documents.docling.chunker_docling import TypeFichier
from documents.docling.chunker_docling_mqc import ChunkerDoclingMQC
from documents.html.document_html import DocumentHTML
from documents.pdf.assembleur_blocs_json import (
    BlocOcr,
    PageOcr,
    ResultatOcrPdf,
    TypeDeBlocOcr,
)
from documents.pdf.document_pdf import DocumentPDF


def test_retourne_les_blocs_ocr_json_d_un_pdf(
    un_convertisseur_avec_un_texte,
    un_convertisseur_ocr_json_de_test,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
                        code=None,
                        titre=None,
                        texte="Un texte OCR",
                    ),
                ),
            ),
        ),
    )

    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(resultat_ocr)
    document = ChunkerDoclingMQC(
        converter=un_convertisseur_avec_un_texte(),
        convertisseur_ocr_json=convertisseur_ocr_json,
    ).applique(document=document)

    assert len(document.pages) == 1
    assert document.pages[1].numero_page == 1
    assert document.pages[1].blocs[0].texte == "Un texte OCR"


def test_ocr_les_pages_des_plages_avec_du_contenu(
    un_convertisseur_avec_un_texte,
    un_convertisseur_ocr_json_de_test,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=3,
        pages=(
            PageOcr(numero_page=1, blocs=()),
            PageOcr(numero_page=3, blocs=()),
        ),
    )
    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(resultat_ocr)

    chunker = ChunkerDoclingMQC(
        converter=un_convertisseur_avec_un_texte(),
        identifie_les_plages_de_pages_pdf=lambda _: [(1, 1), (3, 3)],
        convertisseur_ocr_json=convertisseur_ocr_json,
    )
    chunker.applique(document)

    assert convertisseur_ocr_json.plages_recues == [[(1, 1), (3, 3)]]


def test_ocr_toutes_les_pages_si_le_prediagnostic_est_indisponible(
    un_convertisseur_avec_un_texte,
    un_convertisseur_ocr_json_de_test,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = ResultatOcrPdf(nombre_de_pages=2, pages=())
    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(resultat_ocr)

    chunker = ChunkerDoclingMQC(
        converter=un_convertisseur_avec_un_texte(),
        identifie_les_plages_de_pages_pdf=lambda _: None,
        convertisseur_ocr_json=convertisseur_ocr_json,
    )
    chunker.applique(document)

    assert convertisseur_ocr_json.plages_recues == [None]


def test_le_document_retourne_le_nom_du_document(
    fichier_pdf,
    un_convertisseur_avec_un_texte,
    un_convertisseur_ocr_json_de_test,
):
    chemin_fichier_de_test = str(fichier_pdf("document_mqc.pdf").resolve())
    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")

    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(
        ResultatOcrPdf(nombre_de_pages=1, pages=())
    )
    document = ChunkerDoclingMQC(
        converter=un_convertisseur_avec_un_texte(),
        convertisseur_ocr_json=convertisseur_ocr_json,
    ).applique(document=document)

    assert document.nom_document == "document_mqc.pdf"


def test_retourne_le_nom_du_fichier(
    fichier_pdf,
    un_convertisseur_avec_un_texte,
    un_convertisseur_ocr_json_de_test,
):
    chemin_fichier_de_test = str(fichier_pdf("document_mqc.pdf").resolve())
    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")

    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(
        ResultatOcrPdf(nombre_de_pages=1, pages=())
    )
    chunker = ChunkerDoclingMQC(
        converter=un_convertisseur_avec_un_texte(),
        convertisseur_ocr_json=convertisseur_ocr_json,
    )
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


def test_ne_fait_aucun_appel_ocr_si_toutes_les_pages_sont_vides(
    fichier_pdf,
    un_convertisseur_avec_un_texte,
    un_convertisseur_ocr_json_de_test,
):
    document = DocumentPDF(str(fichier_pdf("document.pdf")), "https://example.com")
    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(
        ResultatOcrPdf(nombre_de_pages=2, pages=())
    )

    chunker = ChunkerDoclingMQC(
        converter=un_convertisseur_avec_un_texte(),
        identifie_les_plages_de_pages_pdf=lambda _: [],
        convertisseur_ocr_json=convertisseur_ocr_json,
    )
    document = chunker.applique(document)

    assert convertisseur_ocr_json.plages_recues == []
    assert all(not page.blocs for page in document.pages.values())


def test_conserve_la_page_3_apres_une_page_2_vide(
    un_convertisseur_avec_un_texte,
    un_convertisseur_ocr_json_de_test,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=3,
        pages=(
            PageOcr(numero_page=1, blocs=()),
            PageOcr(
                numero_page=3,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
                        code=None,
                        titre=None,
                        texte="Contenu page 3",
                    ),
                ),
            ),
        ),
    )
    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(resultat_ocr)

    chunker = ChunkerDoclingMQC(
        converter=un_convertisseur_avec_un_texte(),
        identifie_les_plages_de_pages_pdf=lambda _: [(1, 1), (3, 3)],
        convertisseur_ocr_json=convertisseur_ocr_json,
    )
    document = chunker.applique(document)

    assert sorted(document.pages) == [1, 2, 3]
    assert not document.pages[2].blocs
    assert document.pages[3].blocs[0].numero_page == 3
    assert document.pages[3].blocs[0].texte == "Contenu page 3"


def test_conserve_les_blocs_multi_pages(
    un_convertisseur_avec_un_texte,
    un_convertisseur_ocr_json_de_test,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=2,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
                        code=None,
                        titre=None,
                        texte="Début",
                    ),
                ),
            ),
            PageOcr(
                numero_page=2,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.PARAGRAPHE,
                        code=None,
                        titre=None,
                        texte="Suite",
                        est_une_continuation=True,
                    ),
                ),
            ),
        ),
    )
    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(resultat_ocr)

    chunker = ChunkerDoclingMQC(
        converter=un_convertisseur_avec_un_texte(),
        identifie_les_plages_de_pages_pdf=lambda _: None,
        convertisseur_ocr_json=convertisseur_ocr_json,
    )
    document = chunker.applique(document)

    assert len(document.pages[1].blocs) == 1
    assert document.pages[1].blocs[0].texte == "Début\nSuite"
    assert not document.pages[2].blocs


def test_echoue_si_la_reponse_ocr_json_est_invalide(
    un_convertisseur_avec_un_texte,
):
    class ConvertisseurOcrJsonEnErreur:
        def convertit(self, chemin, plages_de_pages):
            raise ValueError("JSON invalide")

    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    chunker = ChunkerDoclingMQC(
        converter=un_convertisseur_avec_un_texte(),
        convertisseur_ocr_json=ConvertisseurOcrJsonEnErreur(),
    )

    with pytest.raises(ValueError, match="JSON invalide"):
        chunker.applique(document)


def test_n_utilise_pas_docling_pour_un_pdf(
    un_convertisseur_ocr_json_de_test,
):
    class ConvertisseurDoclingInterdit:
        def convert(self, *args, **kwargs):
            raise AssertionError("Docling ne doit pas être appelé pour un PDF")

    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = ResultatOcrPdf(nombre_de_pages=1, pages=())
    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(resultat_ocr)
    chunker = ChunkerDoclingMQC(
        converter=ConvertisseurDoclingInterdit,
        convertisseur_ocr_json=convertisseur_ocr_json,
        identifie_les_plages_de_pages_pdf=lambda _: None,
    )

    chunker.applique(document)


def test_conserve_les_sections_et_recommandations_dans_le_chunker(
    un_convertisseur_avec_un_texte,
    un_convertisseur_ocr_json_de_test,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = ResultatOcrPdf(
        nombre_de_pages=1,
        pages=(
            PageOcr(
                numero_page=1,
                blocs=(
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.TITRE,
                        code=None,
                        titre="Section 5",
                        texte="Section 5",
                        niveau=1,
                    ),
                    BlocOcr(
                        type_de_bloc=TypeDeBlocOcr.RECOMMANDATION,
                        code="R24",
                        titre="Titre de la recommandation",
                        texte="Contenu de la recommandation",
                    ),
                ),
            ),
        ),
    )
    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(resultat_ocr)
    chunker = ChunkerDoclingMQC(
        converter=un_convertisseur_avec_un_texte(),
        convertisseur_ocr_json=convertisseur_ocr_json,
    )

    document = chunker.applique(document)
    bloc = document.pages[1].blocs[0]
    metadata = document.metadata(bloc)

    assert bloc.texte == (
        "Section 5\nR24\nTitre de la recommandation\n"
        "Contenu de la recommandation"
    )
    assert metadata["type_de_bloc"] == "recommandation"
    assert metadata["code_recommandation"] == "R24"
    assert metadata["chemin_sections"] == '["Section 5"]'
