import pytest

from documents.pdf.convertisseur_ocr_json import (
    ConvertisseurOcrJson,
    ErreurOcrJson,
    MODELE_OCR_PAR_DEFAUT,
    NOMBRE_MAXIMAL_DE_TOKENS_DE_COMPLETION_OCR,
)
from documents.pdf.prompt_ocr_json import PROMPT_OCR_JSON


def annotation_ocr_json(**modifications):
    bloc = {
        "type": "paragraph",
        "code": None,
        "title": None,
        "text": "Texte OCR",
        "level": None,
        "continues_previous": False,
        "items": None,
        "rows": None,
    }
    bloc.update(modifications)
    return {"blocks": [bloc]}


def test_construit_une_requete_ocr_avec_le_schema_json(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test(annotation_ocr_json())
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    convertisseur.convertit("document.pdf", None)

    requete = transport_http.requetes[0]
    assert requete["url"] == "https://albert.local/v1/chat/completions"
    assert requete["corps"]["model"] == MODELE_OCR_PAR_DEFAUT
    assert requete["corps"]["response_format"]["type"] == "json_schema"


def test_demande_le_modele_mistral_small_24b(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test(annotation_ocr_json())
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    convertisseur.convertit("document.pdf", None)

    assert transport_http.requetes[0]["corps"]["model"] == (
        "mistralai/Mistral-Small-3.2-24B-Instruct-2506"
    )


def test_limite_la_taille_de_la_reponse_ocr(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test(annotation_ocr_json())
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    convertisseur.convertit("document.pdf", None)

    assert transport_http.requetes[0]["corps"]["max_completion_tokens"] == (
        NOMBRE_MAXIMAL_DE_TOKENS_DE_COMPLETION_OCR
    )


def test_decode_une_reponse_json_valide(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test(annotation_ocr_json())
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    resultat_ocr = convertisseur.convertit("document.pdf", None)

    assert resultat_ocr.nombre_de_pages == 1
    assert resultat_ocr.pages[0].numero_page == 1
    assert resultat_ocr.pages[0].blocs[0].texte == "Texte OCR"


def test_decode_une_reponse_contenant_un_tableau(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test(
        annotation_ocr_json(
            type="table",
            text="",
            rows=[["Nom", "Valeur"]],
        )
    )
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    resultat_ocr = convertisseur.convertit("document.pdf", None)

    assert resultat_ocr.pages[0].blocs[0].lignes_de_tableau == (("Nom", "Valeur"),)


def test_normalise_le_niveau_zero_d_un_paragraphe(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test(
        annotation_ocr_json(level=0)
    )
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    resultat_ocr = convertisseur.convertit("document.pdf", None)

    assert resultat_ocr.pages[0].blocs[0].niveau is None


def test_normalise_le_niveau_zero_d_une_recommandation(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test(
        annotation_ocr_json(type="recommendation", code="R2", level=0)
    )
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    resultat_ocr = convertisseur.convertit("document.pdf", None)

    assert resultat_ocr.pages[0].blocs[0].niveau is None


def test_conserve_le_niveau_d_un_titre(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test(
        annotation_ocr_json(
            type="heading",
            title="6.1.2 ESP",
            text="",
            level=3,
        )
    )
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    resultat_ocr = convertisseur.convertit("document.pdf", None)

    assert resultat_ocr.pages[0].blocs[0].niveau == 3


def test_refuse_une_reponse_http_en_erreur(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test({}, code_http=500)
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    with pytest.raises(ErreurOcrJson):
        convertisseur.convertit("document.pdf", None)


def test_refuse_une_reponse_json_invalide(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test("pas du json")
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    with pytest.raises(ErreurOcrJson):
        convertisseur.convertit("document.pdf", None)


def test_refuse_un_bloc_json_incomplet(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    bloc_incomplet = annotation_ocr_json()
    del bloc_incomplet["blocks"][0]["rows"]
    transport_http = un_transport_http_ocr_json_de_test(bloc_incomplet)
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    with pytest.raises(ErreurOcrJson):
        convertisseur.convertit("document.pdf", None)


def test_refuse_un_type_de_bloc_inconnu(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test(
        annotation_ocr_json(type="unknown")
    )
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    with pytest.raises(ErreurOcrJson):
        convertisseur.convertit("document.pdf", None)


def test_refuse_un_code_de_recommandation_invalide(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test(
        annotation_ocr_json(type="recommendation", code="R-24")
    )
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    with pytest.raises(ErreurOcrJson):
        convertisseur.convertit("document.pdf", None)


def test_ne_retourne_jamais_la_cle_api_dans_une_erreur(
    un_transport_http_ocr_json_de_test,
    un_rendeur_de_page_pdf_de_test,
):
    transport_http = un_transport_http_ocr_json_de_test({}, code_http=500)
    convertisseur = ConvertisseurOcrJson(
        cle_api="cle-secrete",
        url_albert="https://albert.local/v1",
        transport_http=transport_http,
        rendeur_de_page=un_rendeur_de_page_pdf_de_test(nombre_de_pages=1),
    )

    with pytest.raises(ErreurOcrJson) as erreur:
        convertisseur.convertit("document.pdf", None)

    assert "cle-secrete" not in str(erreur.value)


def test_le_prompt_demande_un_titre_complet():
    assert "title contient le titre complet, y compris sa numérotation" in PROMPT_OCR_JSON
    assert "et text vaut une chaîne vide" in PROMPT_OCR_JSON
    assert "Un titre visuel et sémantique est toujours un bloc heading distinct" in PROMPT_OCR_JSON
    assert "un paragraphe ne possède jamais de title" in PROMPT_OCR_JSON


def test_le_prompt_demande_un_niveau_uniquement_pour_les_titres():
    assert "level est renseigné uniquement pour les headings" in PROMPT_OCR_JSON
    assert "6 vaut 1, 6.1 vaut 2 et 6.1.2 vaut 3" in PROMPT_OCR_JSON
    assert "Les paragraphes, recommandations, listes et tableaux ont level à null" in PROMPT_OCR_JSON


def test_le_prompt_demande_une_liste_avec_son_introduction():
    assert "Une liste avec une introduction est un unique bloc list" in PROMPT_OCR_JSON
    assert "text contient l'introduction et items contient les puces" in PROMPT_OCR_JSON


def test_le_prompt_demande_la_continuation_d_une_liste_en_debut_de_page():
    assert "commence par une puce qui poursuit une liste" in PROMPT_OCR_JSON
    assert "continues_previous vaut true" in PROMPT_OCR_JSON
