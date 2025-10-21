import pytest
import importlib.util
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
