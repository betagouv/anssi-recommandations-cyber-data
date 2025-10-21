import pytest
from pathlib import Path


class MockMetricRegistry:
    def register(self, **kwargs):
        def decorator(func):
            return func

        return decorator


### Astuce pour importer le code de la métrique dans le test sans rajouter
### dans le dossier src/metriques_personnalisees_evalap un registry
file_path = Path("src/metriques_personnalisees_evalap/bon_nom_document_en_contexte.py")
code = file_path.read_text()
code = code.replace(
    "from . import metric_registry  # type: ignore[attr-defined]",
    "# Mock metric_registry injecté",
)
namespace = {"metric_registry": MockMetricRegistry()}
exec(code, namespace)
metrique_bon_nom_document_en_contexte = namespace[
    "metrique_bon_nom_document_en_contexte"
]

# Métrique numéro page
file_path_page = Path(
    "src/metriques_personnalisees_evalap/bon_numero_page_en_contexte.py"
)
code_page = file_path_page.read_text()
code_page = code_page.replace(
    "from . import metric_registry  # type: ignore[attr-defined]",
    "# Mock metric_registry injecté",
)
namespace_page = {"metric_registry": MockMetricRegistry()}
exec(code_page, namespace_page)
metrique_bon_numero_page_en_contexte = namespace_page[
    "metrique_bon_numero_page_en_contexte"
]


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
        ("", "", 1.0, "Nom de document correct"),
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
    score, observation, _ = metrique_bon_nom_document_en_contexte(
        "output",
        "output_true",
        nom_document_reponse_bot=nom_document_reponse_bot,
        nom_document_verite_terrain=nom_document_verite_terrain,
    )
    assert score == score_attendu
    assert observation == observation_attendue


@pytest.mark.parametrize(
    "page_bot,page_verite,score_min,score_max,mot_cle_observation",
    [
        (3, 3, 1.0, 1.0, "correct"),
        (3, 2, 0.7, 1.0, "proche"),
        (3, 5, 0.4, 0.8, None),
        (3, 12, 0.0, 0.2, None),
        (None, None, 0.0, 0.0, "manquant"),
    ],
)
def test_metrique_bon_numero_page_en_contexte(
    page_bot, page_verite, score_min, score_max, mot_cle_observation
):
    kwargs = {}
    if page_bot is not None:
        kwargs["numero_page_reponse_bot"] = page_bot
    if page_verite is not None:
        kwargs["numero_page_verite_terrain"] = page_verite

    score, observation, _ = metrique_bon_numero_page_en_contexte(
        "output", "output_true", **kwargs
    )

    assert score_min <= score <= score_max
    if mot_cle_observation:
        assert mot_cle_observation in observation.lower()


def test_metrique_numero_page_score_symetrie():
    score1, _, _ = metrique_bon_numero_page_en_contexte(
        "output", "output_true", numero_page_reponse_bot=3, numero_page_verite_terrain=2
    )

    score2, _, _ = metrique_bon_numero_page_en_contexte(
        "output", "output_true", numero_page_reponse_bot=1, numero_page_verite_terrain=2
    )

    assert score1 == score2


@pytest.mark.parametrize(
    "page_bot,page_verite",
    [
        ("abc", 3),
        (3, "def"),
        ("abc", "def"),
        ([], 3),
        ({}, 2),
    ],
)
def test_metrique_numero_page_types_invalides(page_bot, page_verite):
    score, observation, _ = metrique_bon_numero_page_en_contexte(
        "output",
        "output_true",
        numero_page_reponse_bot=page_bot,
        numero_page_verite_terrain=page_verite,
    )

    assert score == 0.0
    assert "invalide" in observation.lower()
