from documents.pdf.convertisseur_ocr_json import (
    ConvertisseurOcrJson,
    DELAI_MAXIMAL_OCR,
    MODELE_OCR_PAR_DEFAUT,
    NOMBRE_MAXIMAL_DE_TOKENS_DE_COMPLETION_OCR,
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
        "lignes_de_tableau": None,
    }
    bloc.update(modifications)
    return {"blocs": [bloc]}


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


def test_transmet_un_delai_de_300_secondes_a_albert(
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

    assert transport_http.requetes[0]["timeout"] == DELAI_MAXIMAL_OCR


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
            type_de_bloc="tableau",
            texte="",
            lignes_de_tableau=[["Nom", "Valeur"]],
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
