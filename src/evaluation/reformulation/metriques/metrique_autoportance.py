from deepeval.metrics import GEval
from deepeval.metrics.g_eval import Rubric
from deepeval.test_case import LLMTestCaseParams

from evaluation.mqc.client_deepeval_albert import ClientDeepEvalAlbert


class MetriqueAutoportance(GEval):
    def __init__(self, **kwargs):
        super().__init__(
            name="MetriqueAutoportance",
            criteria=(
                """
                Tu es un juge expert en reformulation de question RAG pour l'ANSSI.
                Tu notes uniquement l'autoportance de la reformulation MQC ('Actual Output')
                comparée à la reformulation idéale ('Expected Output').

                RÈGLE ABSOLUE : Si 'Actual Output' est EXACTEMENT identique à 'Expected Output' (après normalisation mineure),
                retourne TOUJOURS un score de 1.0, peu importe les autres considérations.

                Autoportance = question compréhensible seule, sans contexte implicite externe.
                Une question autoportante précise suffisamment le sujet, sans pronoms ambigus
                ("ça", "cela", "ce sujet", "ça", "il", "elle") ni références manquantes.

                Important:
                - N'évalue pas ici la suppression des parasites, la fidélité métier, ni la conservation fine des contraintes.
                - Pénalise surtout le manque de contexte indispensable pour comprendre et traiter la question.
                """
            ),
            evaluation_steps=[
                "PREMIÈRE ÉTAPE OBLIGATOIRE : Vérifie si 'Actual Output' est identique à 'Expected Output' (ignore casse, espaces, apostrophes). Si OUI, retourne score 1.0 immédiatement.",
                "Vérifie que 'Actual Output' peut être compris sans le contexte de la conversation précédente.",
                "Détecte les références ambiguës ou incomplètes qui empêchent une compréhension autonome.",
                "Compare à 'Expected Output' pour vérifier que le niveau de contexte nécessaire est présent.",
                "Accorde une note élevée si la question est claire, autonome et exploitable telle quelle en RAG.",
                "Donne un score final uniquement sur l'autoportance.",
            ],
            rubric=[
                Rubric(
                    score_range=(0, 3),
                    expected_outcome=(
                        "Niveau faible: question non autonome, références ambiguës fortes ou contexte essentiel manquant."
                    ),
                ),
                Rubric(
                    score_range=(4, 7),
                    expected_outcome=(
                        "Niveau moyen: question partiellement autonome, avec quelques ambiguïtés ou manques de contexte."
                    ),
                ),
                Rubric(
                    score_range=(8, 10),
                    expected_outcome=(
                        "Niveau élevé: question autonome, claire et directement exploitable sans contexte supplémentaire."
                    ),
                ),
            ],
            evaluation_params=[
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
            model=ClientDeepEvalAlbert(),
            _include_g_eval_suffix=False,
        )
