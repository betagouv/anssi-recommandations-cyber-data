from deepeval.metrics import GEval
from deepeval.metrics.g_eval import Rubric
from deepeval.test_case import LLMTestCaseParams

from evaluation.deepeval_adaptateur.client_deepeval_albert import ClientDeepEvalAlbert


class MetriqueSuppressionParasites(GEval):
    def __init__(self, **kwargs):
        super().__init__(
            name="MetriqueSuppressionParasites",
            criteria=(
                """
                Tu es un juge expert en reformulation de question RAG pour l'ANSSI.
                Tu notes uniquement la suppression des éléments parasites dans la reformulation.

                Élément parasite = hésitation, tic de langage, répétition vide, bruit de transcription,
                artefact technique (balise, métadonnée), fragment hors sujet ou sans valeur informative.

                Important:
                - N'évalue pas ici l'autoportance, la fidélité métier, ni la conservation de toutes les contraintes.
                - Ne pénalise pas les différences de style, de ponctuation, de casse, ni les reformulations lexicales.
                - Si l'Input contient peu ou pas de parasites, une reformulation propre doit recevoir une note élevée.
                - Pénalise surtout les parasites de l'Input qui restent, ou les nouveaux parasites introduits.
                - Les écarts de sens mineurs sans parasite relèvent surtout d'autres métriques et doivent peu impacter celle-ci.
                """
            ),
            evaluation_steps=[
                "Repère dans 'Input' les segments parasites qui n'apportent aucune information utile à la recherche RAG.",
                "Vérifie que 'Actual Output' supprime ces segments parasites et n'introduit pas de nouveau bruit parasite.",
                "Mesure prioritairement le taux de suppression des parasites (critère dominant du score).",
                "Si l'Input contient peu ou pas de parasites, attribue une note élevée à une sortie propre et concise.",
                "Utilise 'Expected Output' comme repère indicatif de nettoyage, sans imposer une correspondance mot à mot.",
                "Donne un score final uniquement sur la qualité de suppression des parasites.",
            ],
            rubric=[
                Rubric(
                    score_range=(0, 3),
                    expected_outcome=(
                        "Niveau faible: suppression insuffisante des parasites (nombreux parasites conservés "
                        "ou bruit parasite ajouté)."
                    ),
                ),
                Rubric(
                    score_range=(4, 7),
                    expected_outcome=(
                        "Niveau moyen: nettoyage partiel à correct, avec encore quelques parasites résiduels."
                    ),
                ),
                Rubric(
                    score_range=(10, 10),
                    expected_outcome=(
                        "Niveau élevé: suppression très bonne à excellente des parasites, sortie propre et concise. "
                        "Cas sans parasite en entrée: sortie propre attendue dans cette plage."
                    ),
                ),
            ],
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
            model=ClientDeepEvalAlbert(),
            _include_g_eval_suffix=False,
        )
