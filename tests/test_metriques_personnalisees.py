import pytest
from metriques_personnalisees_evalap.metriques_personnalisees import (
    _metrique_bon_nom_document_en_contexte,
    _metrique_score_numero_page_en_contexte,
    _metrique_bon_numero_page_en_contexte,
)


@pytest.mark.parametrize(
    "nom_document_reponse_bot,nom_document_verite_terrain,score_attendu",
    [
        ("Guide_ANSSI", "Guide_ANSSI", 1.0),
        ("guide_anssi", "guide_anssi", 1.0),
        ("Guide_Sécurité", "Guide_ANSSI", 0.0),
        ("Guide_Sécurité", "Guide_Sécurité", 1.0),
        ("", "", 0.0),
        ("Guide_Sécurité", "", 0.0),
        ("", "Guide_ANSSI", 0.0),
        ("Guide", "Guide_ANSSI", 0.0),
    ],
)
def test_metrique_bon_nom_document_en_contexte(
    nom_document_reponse_bot,
    nom_document_verite_terrain,
    score_attendu,
):
    score = _metrique_bon_nom_document_en_contexte(
        nom_document_reponse_bot=nom_document_reponse_bot,
        nom_document_verite_terrain=nom_document_verite_terrain,
    )
    assert score == score_attendu


@pytest.mark.parametrize(
    "page_estimee,page_verite,score_min,score_max",
    [
        (3, 3, 1.0, 1.0),
        (3, 2, 0.6, 1.0),
        (3, 5, 0.4, 0.8),
        (3, 12, 0.0, 0.25),
        (None, None, 0.0, 0.0),
    ],
)
def test_metrique_score_numero_page(page_estimee, page_verite, score_min, score_max):
    score = _metrique_score_numero_page_en_contexte(page_estimee, page_verite)

    assert score_min <= score <= score_max


def test_metrique_score_numero_page_score_symetrie():
    score1 = _metrique_score_numero_page_en_contexte(
        numero_page_reponse_bot=3, numero_page_verite_terrain=2
    )
    score2 = _metrique_score_numero_page_en_contexte(
        numero_page_reponse_bot=2, numero_page_verite_terrain=3
    )

    assert score1 == score2


@pytest.mark.parametrize(
    "page_estimee,page_verite,score_attendu",
    [
        (4, 4, 1.0),
        (4, 5, 0.0),
        (4.0, 4.0, 1.0),
    ],
)
def test_metrique_bon_numero_page_en_contexte(page_estimee, page_verite, score_attendu):
    resultat = _metrique_bon_numero_page_en_contexte(page_estimee, page_verite)

    assert resultat == score_attendu


def test_metrique_bon_numero_page_en_contexte_string_invalide():
    resultat = _metrique_bon_numero_page_en_contexte("abc", 4)

    assert resultat == 0.0
