import pytest

from documents.docling.chunker_docling import TypeFichier
from documents.docling.chunker_docling_mqc import ChunkerDoclingMQC
from documents.html.document_html import DocumentHTML
from documents.pdf.assembleur_blocs_json import PageOcr, TypeDeBlocOcr
from documents.pdf.document_pdf import DocumentPDF


@pytest.fixture
def un_chunker_ocr_json(
    un_convertisseur_avec_un_texte,
    un_convertisseur_ocr_json_de_test,
):
    def _cree_un_chunker_ocr_json(resultat_ocr, plages_de_pages=None):
        convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(resultat_ocr)
        chunker = ChunkerDoclingMQC(
            converter=un_convertisseur_avec_un_texte(),
            identifie_les_plages_de_pages_pdf=lambda _: plages_de_pages,
            convertisseur_ocr_json=convertisseur_ocr_json,
        )
        return chunker, convertisseur_ocr_json

    return _cree_un_chunker_ocr_json


def test_retourne_les_blocs_ocr_json_d_un_pdf(
    un_chunker_ocr_json,
    un_resultat_ocr,
    un_bloc_ocr_json,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=((un_bloc_ocr_json(texte="Un texte OCR"),),)
    )
    chunker, _ = un_chunker_ocr_json(resultat_ocr)

    document = chunker.applique(document=document)

    assert len(document.pages) == 1
    assert document.pages[1].numero_page == 1
    assert document.pages[1].blocs[0].texte == "Un texte OCR"


def test_ocr_les_pages_des_plages_avec_du_contenu(
    un_chunker_ocr_json,
    un_resultat_ocr,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = un_resultat_ocr(blocs_par_page=((), (), ()))
    chunker, convertisseur_ocr_json = un_chunker_ocr_json(
        resultat_ocr,
        plages_de_pages=[(1, 1), (3, 3)],
    )

    chunker.applique(document)

    assert convertisseur_ocr_json.plages_recues == [[(1, 1), (3, 3)]]


def test_ocr_toutes_les_pages_si_le_prediagnostic_est_indisponible(
    un_chunker_ocr_json,
    un_resultat_ocr,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = un_resultat_ocr(nombre_de_pages=2)
    chunker, convertisseur_ocr_json = un_chunker_ocr_json(resultat_ocr)

    chunker.applique(document)

    assert convertisseur_ocr_json.plages_recues == [None]


def test_le_document_retourne_le_nom_du_document(
    fichier_pdf,
    un_chunker_ocr_json,
    un_resultat_ocr,
):
    chemin_fichier_de_test = str(fichier_pdf("document_mqc.pdf").resolve())
    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")
    chunker, _ = un_chunker_ocr_json(un_resultat_ocr(nombre_de_pages=1))

    document = chunker.applique(document=document)

    assert document.nom_document == "document_mqc.pdf"


def test_retourne_le_nom_du_fichier(
    fichier_pdf,
    un_chunker_ocr_json,
    un_resultat_ocr,
):
    chemin_fichier_de_test = str(fichier_pdf("document_mqc.pdf").resolve())
    document = DocumentPDF(chemin_fichier_de_test, "https://example.com/test.pdf")
    chunker, _ = un_chunker_ocr_json(un_resultat_ocr(nombre_de_pages=1))

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
    un_chunker_ocr_json,
    un_resultat_ocr,
):
    document = DocumentPDF(str(fichier_pdf("document.pdf")), "https://example.com")
    resultat_ocr = un_resultat_ocr(nombre_de_pages=2)
    chunker, convertisseur_ocr_json = un_chunker_ocr_json(
        resultat_ocr,
        plages_de_pages=[],
    )

    document = chunker.applique(document)

    assert convertisseur_ocr_json.plages_recues == []
    assert len(document.pages) == 1
    assert document.pages[1].blocs == []


def test_conserve_la_page_3_apres_une_page_2_vide(
    un_chunker_ocr_json,
    un_resultat_ocr,
    un_bloc_ocr_json,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (),
            (),
            (un_bloc_ocr_json(texte="Contenu page 3"),),
        )
    )
    chunker, _ = un_chunker_ocr_json(
        resultat_ocr,
        plages_de_pages=[(1, 1), (3, 3)],
    )

    document = chunker.applique(document)

    assert sorted(document.pages) == [1, 2, 3]
    assert not document.pages[2].blocs
    assert document.pages[3].blocs[0].numero_page == 3
    assert document.pages[3].blocs[0].texte == "Contenu page 3"


def test_conserve_les_blocs_multi_pages(
    un_chunker_ocr_json,
    un_resultat_ocr,
    un_bloc_ocr_json,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (un_bloc_ocr_json(texte="Début"),),
            (un_bloc_ocr_json(texte="Suite", est_une_continuation=True),),
        )
    )
    chunker, _ = un_chunker_ocr_json(resultat_ocr)

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
        identifie_les_plages_de_pages_pdf=lambda _: None,
    )

    with pytest.raises(ValueError, match="JSON invalide"):
        chunker.applique(document)


def test_n_utilise_pas_docling_pour_un_pdf(
    un_convertisseur_ocr_json_de_test,
    un_resultat_ocr,
):
    class ConvertisseurDoclingInterdit:
        def convert(self, *args, **kwargs):
            raise AssertionError("Docling ne doit pas être appelé pour un PDF")

    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    convertisseur_ocr_json = un_convertisseur_ocr_json_de_test(
        un_resultat_ocr(nombre_de_pages=1)
    )
    chunker = ChunkerDoclingMQC(
        converter=ConvertisseurDoclingInterdit,
        convertisseur_ocr_json=convertisseur_ocr_json,
        identifie_les_plages_de_pages_pdf=lambda _: None,
    )

    chunker.applique(document)


def test_conserve_les_sections_et_recommandations_dans_le_chunker(
    un_chunker_ocr_json,
    un_resultat_ocr,
    un_bloc_ocr_json,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.TITRE,
                    titre="Section 5",
                    texte="Section 5",
                    niveau=1,
                ),
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.RECOMMANDATION,
                    code="R24",
                    titre="Titre de la recommandation",
                    texte="Contenu de la recommandation",
                ),
            ),
        )
    )
    chunker, _ = un_chunker_ocr_json(resultat_ocr)

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


def test_conserve_la_table_des_matieres_comme_un_chunk_pdf_unique(
    un_chunker_ocr_json,
    un_resultat_ocr,
    un_bloc_ocr_json,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.TABLE_DES_MATIERES,
                    titre="Sommaire",
                    texte="1 Introduction\n2 Authentification",
                    niveau=1,
                ),
            ),
        )
    )
    chunker, _ = un_chunker_ocr_json(resultat_ocr)

    document = chunker.applique(document)
    bloc = document.pages[1].blocs[0]
    metadata = document.metadata(bloc)

    assert len(document.pages[1].blocs) == 1
    assert bloc.texte == "1 Introduction\n2 Authentification"
    assert metadata["source_url"] == "http://mon-document.pdf"
    assert metadata["page"] == 1
    assert metadata["nom_document"] == "mon_document.pdf"
    assert metadata["type_de_bloc"] == "table_des_matieres"
    assert metadata["niveau"] == 1
    assert "chemin_sections" not in metadata


def test_conserve_une_recommandation_codee_coupee_sur_deux_pages(
    un_chunker_ocr_json,
    un_resultat_ocr,
    un_bloc_ocr_json,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.TITRE,
                    titre="Section 5",
                    texte="Section 5",
                    niveau=1,
                ),
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.RECOMMANDATION,
                    code="R23",
                    titre="Réviser la politique",
                    texte="La politique d'authentification",
                ),
            ),
            (un_bloc_ocr_json(texte="doit être révisée."),),
        )
    )
    chunker, _ = un_chunker_ocr_json(resultat_ocr)

    document = chunker.applique(document)
    bloc = document.pages[1].blocs[0]
    metadata = document.metadata(bloc)

    assert bloc.texte == (
        "Section 5\nR23\nRéviser la politique\n"
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
    un_chunker_ocr_json,
    un_resultat_ocr,
    un_bloc_ocr_json,
):
    document = DocumentPDF("mon_document.pdf", url_pdf="http://mon-document.pdf")
    resultat_ocr = un_resultat_ocr(
        blocs_par_page=(
            (
                un_bloc_ocr_json(
                    type_de_bloc=TypeDeBlocOcr.LISTE,
                    texte="Les mesures recommandées sont les suivantes :",
                    elements_de_liste=(
                        "Analyser les risques.",
                        "Protéger les accès.",
                    ),
                ),
            ),
        )
    )
    chunker, _ = un_chunker_ocr_json(resultat_ocr)

    document = chunker.applique(document)
    bloc = document.pages[1].blocs[0]
    metadata = document.metadata(bloc)

    assert metadata["type_de_bloc"] == "liste"
    assert "code_recommandation" not in metadata
    assert bloc.texte == (
        "Les mesures recommandées sont les suivantes :\n"
        "- Analyser les risques.\n- Protéger les accès."
    )
