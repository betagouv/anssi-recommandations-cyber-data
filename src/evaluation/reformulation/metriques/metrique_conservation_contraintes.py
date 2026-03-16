from deepeval.metrics import GEval
from deepeval.metrics.g_eval import Rubric
from deepeval.test_case import LLMTestCaseParams

from evaluation.mqc.client_deepeval_albert import ClientDeepEvalAlbert


class MetriqueConservationContraintes(GEval):
    def __init__(self, **kwargs):
        super().__init__(
            name="MetriqueConservationContraintes",
            criteria=(
                """
                INSTRUCTION CRITIQUE PRIORITAIRE :
                Compare 'Actual Output' et 'Expected Output' en ignorant UNIQUEMENT la casse, les espaces multiples et les apostrophes.
                Si les deux textes sont identiques après cette normalisation, tu DOIS retourner un score de 1.0.
                Exemple : "Qu'est-ce que MesQuestionsCyber ?" == "Qu'est-ce que MesQuestionsCyber ?" → SCORE 1.0 OBLIGATOIRE
                
                Tu es un juge expert en reformulation de question RAG pour l'ANSSI.
                Tu notes uniquement la conservation des contraintes entre:
                - la reformulation idéale ('Expected Output')
                - la reformulation MQC ('Actual Output')

                Contrainte = condition explicite, restriction, précision de périmètre, terme métier imposé,
                format de réponse demandé, temporalité, acteur ou objet obligatoire.

                Important:
                - N'évalue pas ici la suppression des parasites, l'autoportance ou la fidélité sémantique globale.
                - Pénalise surtout les contraintes manquantes, affaiblies, ou remplacées.
                - Pénalise les nouvelles contraintes ajoutées qui n'existent pas dans l'attendu.
                """
            ),
            evaluation_steps=[
                'ÉTAPE 0 - VÉRIFICATION D\'ÉGALITÉ STRICTE : Normalise \'Actual Output\' et \'Expected Output\' (minuscules, espaces simples, apostrophes uniformes). Si identiques → retourne {"score": 1.0, "reason": "Match parfait"} IMMÉDIATEMENT.',
                "Identifie dans 'Expected Output' les contraintes explicites à conserver.",
                "Vérifie que 'Actual Output' conserve ces contraintes sans les affaiblir ni les supprimer.",
                "Vérifie qu'aucune contrainte nouvelle non demandée n'est ajoutée dans 'Actual Output'.",
                "Accorde une note élevée si les contraintes et termes métier attendus sont bien conservés.",
                "Donne un score final uniquement sur la conservation des contraintes.",
            ],
            rubric=[
                Rubric(
                    score_range=(0, 3),
                    expected_outcome=(
                        "Niveau faible: contraintes importantes perdues, modifiées ou ajoutées de façon incorrecte."
                    ),
                ),
                Rubric(
                    score_range=(4, 7),
                    expected_outcome=(
                        "Niveau moyen: conservation partielle des contraintes, avec quelques oublis ou écarts."
                    ),
                ),
                Rubric(
                    score_range=(8, 10),
                    expected_outcome=(
                        "Niveau élevé: contraintes et termes métier attendus bien conservés, sans ajout contraignant indu."
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
