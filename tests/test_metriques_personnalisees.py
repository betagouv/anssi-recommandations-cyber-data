import pytest
from metriques_personnalisees_evalap.metriques_personnalisees import (
    _metrique_bon_nom_document_en_contexte,
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
    score, observation, _ = _metrique_bon_nom_document_en_contexte(
        nom_document_reponse_bot=nom_document_reponse_bot,
        nom_document_verite_terrain=nom_document_verite_terrain,
    )
    assert score == score_attendu
    assert observation == observation_attendue
