import pytest
from metriques_personnalisees_evalap.metriques_personnalisees import (
    _metrique_bon_nom_document_en_contexte,
    _metrique_score_numero_page_en_contexte,
    _metrique_bon_numero_page_en_contexte,
)


@pytest.mark.parametrize(
    "nom_document_reponse_bot,nom_document_verite_terrain,score_attendu,observation_attendue",
    [
        ("Guide_ANSSI", "Guide_ANSSI", 1.0, "Nom de document correct"),
        ("guide_anssi", "guide_anssi", 1.0, "Nom de document correct"),
        (
            "Guide_Sécurité",
            "Guide_ANSSI",
            0.0,
            "Nom de document incorrect: attendu 'Guide_ANSSI' mais obtenu 'Guide_Sécurité'",
        ),
        ("Guide_Sécurité", "Guide_Sécurité", 1.0, "Nom de document correct"),
        ("", "", 0.0, "Aucun nom fourni"),
        ("Guide_Sécurité", "", 0.0, "Aucun nom fourni"),
        (
            "",
            "Guide_ANSSI",
            0.0,
            "Nom de document incorrect: attendu 'Guide_ANSSI' mais obtenu ''",
        ),
        (
            "Guide",
            "Guide_ANSSI",
            0.0,
            "Nom de document incorrect: attendu 'Guide_ANSSI' mais obtenu 'Guide'",
        ),
    ],
)
def test_metrique_bon_nom_document_en_contexte(
    nom_document_reponse_bot,
    nom_document_verite_terrain,
    score_attendu,
    observation_attendue,
):
    score, observation = _metrique_bon_nom_document_en_contexte(
        nom_document_reponse_bot=nom_document_reponse_bot,
        nom_document_verite_terrain=nom_document_verite_terrain,
    )
    assert score == score_attendu
    assert observation == observation_attendue


@pytest.mark.parametrize(
    "page_estimee,page_verite,score_min,score_max,mot_cle_observation",
    [
        (3, 3, 1.0, 1.0, "correct"),
        (3, 2, 0.6, 1.0, "proche"),
        (3, 5, 0.4, 0.8, "proche"),
        (3, 12, 0.0, 0.25, "erreur importante"),
        (None, None, 0.0, 0.0, "manquant"),
    ],
)
def test_metrique_score_numero_page(
    page_estimee, page_verite, score_min, score_max, mot_cle_observation
):
    score, observation = _metrique_score_numero_page_en_contexte(
        page_estimee, page_verite
    )

    assert score_min <= score <= score_max
    if mot_cle_observation:
        assert mot_cle_observation in observation.lower()


def test_metrique_score_numero_page_score_symetrie():
    score1, _ = _metrique_score_numero_page_en_contexte(
        numero_page_reponse_bot=3, numero_page_verite_terrain=2
    )
    score2, _ = _metrique_score_numero_page_en_contexte(
        numero_page_reponse_bot=2, numero_page_verite_terrain=3
    )

    assert score1 == score2


@pytest.mark.parametrize(
    "page_estimee,page_verite,score_attendu,observation_attendue",
    [
        (4, 4, 1.0, "correct"),
        (4, 5, 0.0, "incorrect"),
        (4.0, 4.0, 1.0, "correct"),
    ],
)
def test_metrique_bon_numero_page_en_contexte(
    page_estimee, page_verite, score_attendu, observation_attendue
):
    resultat, observation = _metrique_bon_numero_page_en_contexte(
        page_estimee, page_verite
    )

    assert resultat == score_attendu
    assert observation_attendue in observation.lower()


def test_metrique_bon_numero_page_en_contexte_string_invalide():
    resultat, observation = _metrique_bon_numero_page_en_contexte("abc", 4)

    assert resultat == 0.0
    assert "invalide" in observation.lower()
