from documents.pdf.convertisseur_ocr_json import (
    ConvertisseurOcrJson,
    ErreurOcrJson,
    MODELE_OCR_PAR_DEFAUT,
    NOMBRE_MAXIMAL_DE_TOKENS_DE_COMPLETION_OCR,
)


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
