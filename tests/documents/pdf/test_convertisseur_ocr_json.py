import pytest

from documents.pdf.convertisseur_ocr_json import (
    ExtracteurDeBlocsOcrDepuisUnPdf,
    DELAI_MAXIMAL_OCR,
    ErreurOcrJson,
    MODELE_OCR_PAR_DEFAUT,
    NOMBRE_MAXIMAL_DE_TOKENS_DE_COMPLETION_OCR,
    SCHEMA_BLOCS_OCR,
)

def annotation_ocr_json(**modifications):
    bloc = {
        "type_de_bloc": "paragraphe",
        "code_recommandation": None,
        "titre": None,
        "texte": "Texte OCR",
        "niveau": None,
        "est_une_continuation": False,
        "elements_de_liste": None,
    }
    bloc.update(modifications)
    return {"blocs": [bloc]}


def annotation_ocr_incomplete():
    annotation = annotation_ocr_json()
    del annotation["blocs"][0]["elements_de_liste"]
    return annotation


@pytest.fixture
def un_convertisseur_ocr_json(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    def _cree_un_convertisseur_ocr_json(
        contenu,
        code_http=200,
        nombre_de_pages=1,
    ):
        transport_http = un_transport_http_ocr_json_de_test(contenu, code_http)
        convertisseur = ExtracteurDeBlocsOcrDepuisUnPdf(
            cle_api="cle-secrete",
            url_albert="https://albert.local/v1",
            transport_http=transport_http,
            rendeur_de_pages=un_rendeur_de_page_pdf_de_test(nombre_de_pages),
        )
        return convertisseur, transport_http

    return _cree_un_convertisseur_ocr_json


def test_construit_une_requete_ocr_avec_le_schema_json(un_convertisseur_ocr_json):
    convertisseur, transport_http = un_convertisseur_ocr_json(annotation_ocr_json())

    convertisseur.convertit("document.pdf", None)

    requete = transport_http.requetes[0]
    assert requete["url"] == "https://albert.local/v1/chat/completions"
    assert requete["corps"]["model"] == MODELE_OCR_PAR_DEFAUT
    assert requete["corps"]["response_format"]["type"] == "json_schema"
    assert requete["corps"]["max_completion_tokens"] == (
        NOMBRE_MAXIMAL_DE_TOKENS_DE_COMPLETION_OCR
    )


def test_transmet_un_delai_de_300_secondes_a_albert(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test(annotation_ocr_json())
    convertisseur = ExtracteurDeBlocsOcrDepuisUnPdf(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_pages=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )
    convertisseur.convertit("document.pdf", None)

    assert transport_http.requetes[0]["timeout"] == DELAI_MAXIMAL_OCR


def test_decode_une_reponse_json_valide(un_convertisseur_ocr_json):
    convertisseur, _ = un_convertisseur_ocr_json(annotation_ocr_json())

    resultat_ocr = convertisseur.convertit("document.pdf", None)

    assert resultat_ocr.nombre_de_pages == 1
    assert resultat_ocr.pages[0].numero_page == 1
    assert resultat_ocr.pages[0].blocs[0].texte == "Texte OCR"


def test_decode_une_reponse_contenant_un_tableau_html(un_convertisseur_ocr_json):
    texte_html = (
        "<table><thead><tr><th>Nom</th><th>Valeur</th></tr></thead>"
        "<tbody><tr><td>Risque</td><td>Élevé</td></tr></tbody></table>"
    )
    convertisseur, _ = un_convertisseur_ocr_json(
        annotation_ocr_json(
            type_de_bloc="tableau",
            texte=texte_html,
        )
    )

    resultat_ocr = convertisseur.convertit("document.pdf", None)

    assert resultat_ocr.pages[0].blocs[0].texte == texte_html


def test_interprete_un_code_et_un_titre_vides_comme_absents(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test(
        annotation_ocr_json(code_recommandation="", titre="")
    )
    convertisseur = ExtracteurDeBlocsOcrDepuisUnPdf(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_pages=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    resultat_ocr = convertisseur.convertit("document.pdf", None)

    assert resultat_ocr.pages[0].blocs[0].code is None
    assert resultat_ocr.pages[0].blocs[0].titre is None


@pytest.mark.parametrize(
    "type_de_bloc, code_recommandation",
    [
        pytest.param("paragraphe", None, id="paragraphe"),
        pytest.param("recommandation", "R2", id="recommandation"),
    ],
)
def test_normalise_le_niveau_zero_des_blocs_non_titres(
    type_de_bloc,
    code_recommandation,
    un_convertisseur_ocr_json,
):
    convertisseur, _ = un_convertisseur_ocr_json(
        annotation_ocr_json(
            type_de_bloc=type_de_bloc,
            code_recommandation=code_recommandation,
            niveau=0,
        )
    )

    resultat_ocr = convertisseur.convertit("document.pdf", None)

    assert resultat_ocr.pages[0].blocs[0].niveau is None


def test_conserve_le_niveau_d_un_titre(un_convertisseur_ocr_json):
    convertisseur, _ = un_convertisseur_ocr_json(
        annotation_ocr_json(
            type_de_bloc="titre",
            titre="6.1.2 ESP",
            texte="",
            niveau=3,
        )
    )

    resultat_ocr = convertisseur.convertit("document.pdf", None)

    assert resultat_ocr.pages[0].blocs[0].niveau == 3


@pytest.mark.parametrize(
    "contenu, code_http",
    [
        pytest.param({}, 500, id="reponse_http_en_erreur"),
        pytest.param("pas du json", 200, id="json_invalide"),
        pytest.param(annotation_ocr_incomplete(), 200, id="bloc_incomplet"),
        pytest.param(
            annotation_ocr_json(type_de_bloc="inconnu"),
            200,
            id="type_inconnu",
        ),
    ],
)
def test_refuse_une_reponse_ocr_invalide(
    contenu,
    code_http,
    un_convertisseur_ocr_json,
):
    convertisseur, _ = un_convertisseur_ocr_json(contenu, code_http)

    with pytest.raises(ErreurOcrJson):
        convertisseur.convertit("document.pdf", None)


def test_ne_retourne_jamais_la_cle_api_dans_une_erreur(un_convertisseur_ocr_json):
    convertisseur, _ = un_convertisseur_ocr_json({}, code_http=500)

    with pytest.raises(ErreurOcrJson) as erreur:
        convertisseur.convertit("document.pdf", None)

    assert "cle-secrete" not in str(erreur.value)


def test_le_schema_accepte_une_table_des_matieres():
    types_de_bloc = SCHEMA_BLOCS_OCR["$defs"]["TypeDeBlocOcr"]["enum"]

    assert "table_des_matieres" in types_de_bloc

def test_convertit_une_recommandation_sans_code_en_liste(
    un_convertisseur_ocr_json,
):
    convertisseur, _ = un_convertisseur_ocr_json(
        annotation_ocr_json(
            type_de_bloc="recommandation",
            titre="Mesures à appliquer",
            texte="Un contenu sans code.",
            elements_de_liste=["Première mesure", "Deuxième mesure"],
        )
    )

    resultat_ocr = convertisseur.convertit("document.pdf", None)

    bloc_ocr = resultat_ocr.pages[0].blocs[0]
    assert bloc_ocr.type_de_bloc.value == "liste"
    assert bloc_ocr.code is None
    assert bloc_ocr.titre == "Mesures à appliquer"
    assert bloc_ocr.texte == "Un contenu sans code."
    assert bloc_ocr.elements_de_liste == ("Première mesure", "Deuxième mesure")

def test_normalise_le_code_d_une_recommandation(un_convertisseur_ocr_json):
    convertisseur, _ = un_convertisseur_ocr_json(
        annotation_ocr_json(
            type_de_bloc="recommandation",
            code_recommandation="R24--",
        )
    )

    resultat_ocr = convertisseur.convertit("document.pdf", None)

    assert resultat_ocr.pages[0].blocs[0].code == "R24"
