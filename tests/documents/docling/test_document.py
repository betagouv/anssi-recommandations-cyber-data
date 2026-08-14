import json

from unittest.mock import MagicMock

from documents.docling.document import Document
from documents.html.document_html import BlocPageReponse
from documents.page import BlocPage, ContexteDuBloc


def _un_document_a_indexer(nom="doc.pdf", url="https://example.com"):
    mock = MagicMock()
    mock.nom_document = nom
    mock.url = url
    return mock


def test_metadata_contient_reponse_maitrisee_vrai_quand_active():
    document = Document(_un_document_a_indexer(), reponse_maitrisee=True)
    bloc = BlocPage(texte="contenu", numero_page=1)

    metadata = document.metadata(bloc)

    assert metadata["reponse_maitrisee"] is True


def test_metadata_contient_id_reponse_quand_bloc_a_un_slug():
    document = Document(_un_document_a_indexer())
    bloc = BlocPageReponse(
        texte="Qui est le directeur ?", id_reponse="qui-est-le-directeur"
    )

    metadata = document.metadata(bloc)

    assert metadata["id_reponse"] == "qui-est-le-directeur"
    assert "reponse" not in metadata


def test_metadata_contient_position_page():
    document = Document(_un_document_a_indexer())
    bloc = BlocPage(texte="contenu", numero_page=1, position_page=3)

    metadata = document.metadata(bloc)

    assert metadata["position_page"] == 3


def test_metadata_ne_contient_pas_position_page_si_absente():
    document = Document(_un_document_a_indexer())
    bloc = BlocPage(texte="contenu", numero_page=1)

    metadata = document.metadata(bloc)

    assert "position_page" not in metadata


def test_metadata_contient_derniere_page_meme_pour_un_bloc_mono_page():
    document = Document(_un_document_a_indexer())
    bloc = BlocPage(texte="contenu", numero_page=1, derniere_page=1)

    metadata = document.metadata(bloc)

    assert metadata["derniere_page"] == 1


def test_metadata_ne_contient_pas_derniere_page_si_absente():
    document = Document(_un_document_a_indexer())
    bloc = BlocPage(texte="contenu", numero_page=1)

    metadata = document.metadata(bloc)

    assert "derniere_page" not in metadata


def test_metadata_contient_les_pages_d_un_bloc_multi_pages():
    document = Document(_un_document_a_indexer())
    bloc = BlocPage(
        texte="contenu",
        numero_page=2,
        position_page=0,
        derniere_page=3,
        pages=(2, 3),
    )

    metadata = document.metadata(bloc)

    assert metadata["page"] == 2
    assert metadata["position_page"] == 0
    assert metadata["derniere_page"] == 3
    assert "pages" not in metadata


def test_metadata_contient_le_contexte_de_section():
    document = Document(_un_document_a_indexer())
    bloc = BlocPage(
        texte="contenu",
        numero_page=2,
        contexte=ContexteDuBloc(
            type_de_bloc="paragraphe",
            titre="Titre de section",
            section="Titre de section",
            chemin_des_sections=("Section 1", "Titre de section"),
            niveau=2,
        ),
    )

    metadata = document.metadata(bloc)

    assert metadata["type_de_bloc"] == "paragraphe"
    assert metadata["titre"] == "Titre de section"
    assert metadata["chemin_sections"] == '["Section 1", "Titre de section"]'
    assert metadata["niveau"] == 2
    assert "section" not in metadata


def test_metadata_contient_le_code_de_recommandation():
    document = Document(_un_document_a_indexer())
    bloc = BlocPage(
        texte="R24\nTitre\nContenu",
        numero_page=2,
        contexte=ContexteDuBloc(
            type_de_bloc="recommandation",
            code_recommandation="R24",
            titre="Titre",
        ),
    )

    metadata = document.metadata(bloc)

    assert metadata["code_recommandation"] == "R24"
    assert metadata["titre"] == "Titre"


def test_metadata_limite_la_longueur_du_titre():
    document = Document(_un_document_a_indexer())
    bloc = BlocPage(
        texte="contenu",
        numero_page=1,
        contexte=ContexteDuBloc(titre="a" * 256),
    )

    metadata = document.metadata(bloc)

    assert metadata["titre"] == "a" * 255


def test_metadata_resume_un_chemin_de_sections_trop_long():
    document = Document(_un_document_a_indexer())
    bloc = BlocPage(
        texte="contenu",
        numero_page=1,
        contexte=ContexteDuBloc(
            chemin_des_sections=("Racine", "a" * 231, "Feuille"),
        ),
    )

    chemin = document.metadata(bloc)["chemin_sections"]

    assert isinstance(chemin, str)
    assert len(chemin) <= 255
    assert json.loads(chemin) == ["Racine", "…", "Feuille"]


def test_metadata_resume_un_intitule_de_section_trop_long():
    document = Document(_un_document_a_indexer())
    bloc = BlocPage(
        texte="contenu",
        numero_page=1,
        contexte=ContexteDuBloc(chemin_des_sections=("a" * 500,)),
    )

    chemin = document.metadata(bloc)["chemin_sections"]
    section = json.loads(chemin)[0]

    assert len(chemin) <= 255
    assert section.startswith("a")
    assert section.endswith("a")
    assert "…" in section
