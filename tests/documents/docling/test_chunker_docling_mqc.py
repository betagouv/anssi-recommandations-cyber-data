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


def test_convertit_uniquement_les_plages_avec_du_texte(
    fichier_pdf,
    un_convertisseur_qui_enregistre_les_plages,
):
    document = DocumentPDF(str(fichier_pdf("document.pdf")), "https://example.com")

    chunker = ChunkerDoclingMQC(
        un_convertisseur_qui_enregistre_les_plages(),
        identifie_les_plages_de_pages_pdf=lambda _: [(1, 1), (3, 4)],
    )
    document = chunker.applique(document)

    assert chunker.converter.plages_recues == [(1, 1), (3, 4)]
    assert sorted(document.pages) == [1, 3, 4]
    assert document.pages[1].blocs[0].texte == "Page 1\nContenu de la page 1"
    assert document.pages[3].blocs[0].texte == "Page 3\nContenu de la page 3"
    assert document.pages[4].blocs[0].texte == "Page 4\nContenu de la page 4"


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
    assert len(document.pages) == 1
    assert document.pages[1].blocs == []
    


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


def test_conserve_une_recommandation_codee_coupee_sur_deux_pages(
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
                        type_de_bloc=TypeDeBlocOcr.RECOMMANDATION,
                        code="R23",
                        titre="Réviser la politique",
                        texte="La politique d'authentification",
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
                        texte="doit être révisée.",
                    ),
                ),
            ),
        ),
    )
    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(resultat_ocr)
    chunker = ChunkerDoclingMQC(
        converter=un_convertisseur_avec_un_texte(),
        convertisseur_ocr_json=convertisseur_ocr_json,
        identifie_les_plages_de_pages_pdf=lambda _: None,
    )

    document = chunker.applique(document)
    bloc = document.pages[1].blocs[0]
    metadata = document.metadata(bloc)

    assert bloc.texte == (
        "R23\nRéviser la politique\n"
        "La politique d'authentification\ndoit être révisée."
    )
    assert metadata["type_de_bloc"] == "recommandation"
    assert metadata["code_recommandation"] == "R23"
    assert metadata["page"] == 1
    assert metadata["derniere_page"] == 2


def test_conserve_une_recommandation_avec_une_liste_sur_deux_pages(
    un_chunker_ocr_json,
    un_resultat_ocr,
    un_bloc_ocr_json,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = un_resultat_ocr(
        pages_ocr=(
            PageOcr(
                numero_page=29,
                blocs=(
                    un_bloc_ocr_json(
                        type_de_bloc=TypeDeBlocOcr.RECOMMANDATION,
                        code="R33",
                        titre="Durcir les mesures de sécurité",
                        texte="Les mesures suivantes sont recommandées :",
                        elements_de_liste=(
                            "Protéger les données.",
                            "Contrôler les accès.",
                        ),
                    ),
                ),
            ),
            PageOcr(
                numero_page=30,
                blocs=(
                    un_bloc_ocr_json(texte="- Sécuriser les services exposés."),
                ),
            ),
        ),
        nombre_de_pages=30,
    )
    chunker, _ = un_chunker_ocr_json(resultat_ocr)

    document = chunker.applique(document)
    bloc = document.pages[29].blocs[0]
    metadata = document.metadata(bloc)

    assert len(document.pages[29].blocs) == 1
    assert not document.pages[30].blocs
    assert bloc.texte == (
        "R33\nDurcir les mesures de sécurité\n"
        "Les mesures suivantes sont recommandées :\n"
        "- Protéger les données.\n- Contrôler les accès.\n"
        "- Sécuriser les services exposés."
    )
    assert metadata["type_de_bloc"] == "recommandation"
    assert metadata["code_recommandation"] == "R33"
    assert metadata["page"] == 29
    assert metadata["derniere_page"] == 30


def test_conserve_une_liste_de_recommandations_sans_code(
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
                        type_de_bloc=TypeDeBlocOcr.LISTE,
                        code=None,
                        titre=None,
                        texte="Les mesures recommandées sont les suivantes :",
                        elements_de_liste=(
                            "Analyser les risques.",
                            "Protéger les accès.",
                        ),
                    ),
                ),
            ),
        ),
    )
    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(resultat_ocr)
    chunker = ChunkerDoclingMQC(
        converter=un_convertisseur_avec_un_texte(),
        convertisseur_ocr_json=convertisseur_ocr_json,
        identifie_les_plages_de_pages_pdf=lambda _: None,
    )

    document = chunker.applique(document)
    bloc = document.pages[1].blocs[0]
    metadata = document.metadata(bloc)

    assert metadata["type_de_bloc"] == "liste"
    assert "code_recommandation" not in metadata
    assert bloc.texte == (
        "Les mesures recommandées sont les suivantes :\n"
        "- Analyser les risques.\n- Protéger les accès."
    )
