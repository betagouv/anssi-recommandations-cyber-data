import pytest

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


# À VOIR LE CAS DE DEUX TEXTES SANS BBOX (ils seraient tous les 2 ordonnés à 0)


@pytest.mark.skip(
    "On doit modifier extrais_les_chunks afin d’obtenir le texte d’un tableau"
)
def test_retourne_le_guide_en_tenant_compte_de_l_ordre_des_bbox_en_s_appuyant_sur_un_guide_anssi(
    un_convertisseur_se_basant_sur_un_guide_anssi,
) -> None:
    document = DocumentPDF(
        "mon_document_ave_bbox.pdf", url_pdf="http://mon-document-bbox.pdf"
    )

    guide = ChunkerDoclingMQC().applique(
        document=document,
        converter=un_convertisseur_se_basant_sur_un_guide_anssi(),
    )

    assert len(guide.pages[11].blocs) == 13
    assert guide.pages[11].numero_page == 11
    assert guide.pages[11].blocs[0].texte == (
        "[TEXTE] afin d’accélérer leur recherche, puis de comparer automatiquement chacune d’entre "
        "elles à une empreinte volée jusqu’à trouver une égalité qui prouvera que le mot de passe "
        "recherché a été trouvé."
    )
    assert guide.pages[11].blocs[2].texte == ("[TEXTE] Menace")
    assert guide.pages[11].blocs[3].texte == ("[TEXTE] Recherche exhaustive")
    assert guide.pages[11].blocs[5].texte == ("[TEXTE] Contre-mesures")
    assert guide.pages[11].blocs[12].texte == (
        "[TEXTE] TABLE 1 – Récapitulatif des menaces et contre-mesures sur les mots de passe"
    )


# @pytest.mark.skip("Test à venir")
# def test_traite_chunks_avec_ordre_simple(cree_chunk_avec_page):
#     chunker = ChunkerDoclingMQC()
#
#     chunks = [
#         cree_chunk_avec_page("[TEXTE] Premier texte", 1),
#         cree_chunk_avec_page("[TEXTE] Deuxième texte", 1),
#     ]
#     ordres_par_page = {1: [0, 1]}
#     par_page: dict[int, list[BlocPage]] = {}  # type: ignore[annotation-unchecked]
#     _traite_chunks_avec_ordre = chunker._traite_chunks_avec_ordre(
#         chunks, ordres_par_page
#     )
#
#     assert 1 in par_page
#     assert len(par_page[1]) == 2
#     assert par_page[1][0].ordre == 0
#     assert par_page[1][1].ordre == 1
#     assert par_page[1][0].texte == "[TEXTE] Premier texte"
#     assert par_page[1][1].texte == "[TEXTE] Deuxième texte"


# @pytest.mark.skip("Test à venir")
# def test_traite_chunks_pages_multiples(cree_chunk_avec_page):
#     chunker = ChunkerDoclingMQC()
#
#     chunks = [
#         cree_chunk_avec_page("[TEXTE] Page 1", 1),
#         cree_chunk_avec_page("[TEXTE] Page 2", 2),
#     ]
#     ordres_par_page = {1: [0], 2: [0]}
#     par_page: dict[int, list[BlocPage]] = {}  # type: ignore[annotation-unchecked]
#
#     _traite_chunks_avec_ordre = chunker._traite_chunks_avec_ordre(
#         chunks, ordres_par_page, par_page
#     )
#
#     assert 1 in par_page
#     assert 2 in par_page
#     assert par_page[1][0].ordre == 0
#     assert par_page[1][0].texte == "[TEXTE] Page 1"
#     assert par_page[2][0].ordre == 0
#     assert par_page[2][0].texte == "[TEXTE] Page 2"


def test_fusionne_entetes_avec_contenu_simple(un_convertisseur_toto):
    document = DocumentPDF(
        "mon_document_ave_bbox.pdf", url_pdf="http://mon-document-bbox.pdf"
    )

    guide = ChunkerDoclingMQC().applique(
        document=document,
        converter=un_convertisseur_toto(),
    )

    assert len(guide.pages[1].blocs) == 1
    assert (
        guide.pages[1].blocs[0].texte == "[TEXTE] Titre\n[TEXTE] Contenu du paragraphe."
    )


# def test_fusionne_entetes_avec_contenu_sans_fusion():
#     chunker = ChunkerDoclingMQC()
#
#     blocs = [
#         BlocPage(
#             texte="Contenu normal.",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=0,
#         ),
#         BlocPage(
#             texte="Autre contenu.",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=1,
#         ),
#     ]
#
#     resultat = chunker._fusionne_les_blocs_avec_entetes(blocs)
#
#     assert len(resultat) == 2
#     assert resultat[0].texte == "Contenu normal."
#     assert resultat[1].texte == "Autre contenu."


# def test_fusionne_entetes_avec_contenu_entetes_consecutifs():
#     chunker = ChunkerDoclingMQC()
#
#     blocs = [
#         BlocPage(
#             texte="Titre 1",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=0,
#         ),
#         BlocPage(
#             texte="Titre 2",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=1,
#         ),
#         BlocPage(
#             texte="Contenu.",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=2,
#         ),
#     ]
#
#     resultat = chunker._fusionne_les_blocs_avec_entetes(blocs)
#
#     assert len(resultat) == 2
#     assert resultat[0].texte == "Titre 1"
#     assert resultat[1].texte == "Titre 2\nContenu."


# def test_fusionne_entetes_avec_contenu_limite_taille():
#     chunker = ChunkerDoclingMQC()
#
#     blocs = [
#         BlocPage(
#             texte="Titre",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=0,
#         ),
#         BlocPage(
#             texte="Contenu très long qui dépasse la limite.",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=1,
#         ),
#     ]
#
#     resultat = chunker._fusionne_les_blocs_avec_entetes(blocs, taille_maximale=20)
#
#     assert len(resultat) == 2
#     assert resultat[0].texte == "Titre"
#     assert resultat[1].texte == "Contenu très long qui dépasse la limite."


# def test_fusionne_entetes_avec_contenu_respecte_limite():
#     chunker = ChunkerDoclingMQC()
#
#     blocs = [
#         BlocPage(
#             texte="Titre",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=0,
#         ),
#         BlocPage(
#             texte="Court.",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=1,
#         ),
#     ]
#
#     resultat = chunker._fusionne_les_blocs_avec_entetes(blocs, taille_maximale=20)
#
#     assert len(resultat) == 1
#     assert resultat[0].texte == "Titre\nCourt."


# def test_fusionne_avec_un_premier_message_plus_long_que_la_taille_ne_genere_pas_d_erreur():
#     chunker = ChunkerDoclingMQC()
#
#     blocs = [
#         BlocPage(
#             texte="Déjà un long message",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=0,
#         ),
#         BlocPage(
#             texte="Un autre",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=1,
#         ),
#     ]
#
#     resultat = chunker._fusionne_les_blocs_avec_entetes(blocs, taille_maximale=6)
#
#     assert len(resultat) == 2
#     assert resultat[0].texte == "Déjà un long message"
#     assert resultat[1].texte == "Un autre"


# def test_fusionne_entetes_evite_duplication_section():
#     chunker = ChunkerDoclingMQC()
#
#     blocs = [
#         BlocPage(
#             texte="[SECTION] 2.1 Authentification et premières définitions",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=0,
#         ),
#         BlocPage(
#             texte="[SECTION] 2.1 Authentification et premières définitions\n[TEXTE] L'authentification est un mécanisme faisant intervenir deux entités distinctes : un prouveur et un vérifieur comme illustré par la figure 1 .",
#             position=Position(x=0.0, y=0.0, largeur=0.0, hauteur=0.0),
#             ordre=1,
#         ),
#     ]
#
#     resultat = chunker._fusionne_les_blocs_avec_entetes(blocs)
#
#     assert len(resultat) == 1
#     assert (
#             resultat[0].texte
#             == "[SECTION] 2.1 Authentification et premières définitions\n[TEXTE] L'authentification est un mécanisme faisant intervenir deux entités distinctes : un prouveur et un vérifieur comme illustré par la figure 1 ."
#     )
#     assert resultat[0].ordre == 0
