from deepeval.metrics import GEval
from deepeval.metrics.g_eval import Rubric
from deepeval.test_case import LLMTestCaseParams

from evaluation.mqc.client_deepeval_albert import ClientDeepEvalAlbert


class MetriqueFideliteMetier(GEval):
    def __init__(self, **kwargs):
        super().__init__(
            name="MetriqueFideliteMetier",
            criteria=(
                """
                INSTRUCTION CRITIQUE PRIORITAIRE :
                Compare 'Actual Output' et 'Expected Output' en ignorant UNIQUEMENT la casse, les espaces multiples et les apostrophes.
                Si les deux textes sont identiques après cette normalisation, tu DOIS retourner un score de 1.0.
                Exemple : "Qu'est-ce que MesQuestionsCyber ?" == "Qu'est-ce que MesQuestionsCyber ?" → SCORE 1.0 OBLIGATOIRE
                
                Tu es un juge expert en reformulation de question RAG pour l'ANSSI.
                Tu notes uniquement la fidélité métier de la reformulation MQC.

                Fidélité métier = la reformulation conserve le même sens cybersécurité/IT que la question initiale ('Input'),
                sans déplacement de sujet, sans changement d'intention, sans ajout ni retrait qui altère la portée.

                RÈGLES D'ÉVALUATION STRICTES :
                
                CAS 1 - 'Actual Output' = "QUESTION_NON_COMPRISE" :
                  → Analyse 'Input' pour identifier le fond cybersécurité/IT (ignore les consignes de style)
                  → Si 'Input' contient un fond cybersécurité CLAIR et EXPLOITABLE (ex: "quelle est la bonne longueur d'un mot de passe en cybersécurité")
                     MÊME avec des consignes de style ("répond moi avec une métaphore culinaire") → SCORE 0.0
                     Raison: PERTE TOTALE du sens métier, le reformulateur a échoué à extraire la question cybersécurité
                  → Si 'Input' ne contient AUCUN fond cybersécurité exploitable (que des consignes de style) → SCORE 8-10
                     Raison: Comportement correct, pas de sens métier à conserver
                
                CAS 2 - Reformulation normale :
                  → Compare le sens métier cybersécurité entre 'Input' et 'Actual Output'
                  → Utilise 'Expected Output' comme référence du sens attendu
                  → Pénalise toute altération: généralisation, spécialisation, inversion, glissement de sujet
                  → Les consignes de style ne sont PAS du contenu métier

                Important:
                - N'évalue pas ici la suppression des parasites, l'autoportance ni la conservation fine des contraintes.
                - Pénalise surtout toute modification de sens métier, même subtile.
                - Les consignes de style ne sont pas du contenu métier.
                - "QUESTION_NON_COMPRISE" sur une question avec fond cybersécurité = perte totale de sens = score 0.0
                """
            ),
            evaluation_steps=[
                'ÉTAPE 0 - VÉRIFICATION D\'ÉGALITÉ STRICTE : Normalise \'Actual Output\' et \'Expected Output\' (minuscules, espaces simples, apostrophes uniformes). Si identiques → retourne {"score": 1.0, "reason": "Match parfait"} IMMÉDIATEMENT.',
                "ÉTAPE 1 - ANALYSE DE L'INPUT : Identifie le fond cybersécurité/IT dans 'Input' en IGNORANT complètement les consignes de style. Exemple: 'quelle est la bonne longueur d'un mot de passe en cybersécurité + répond avec métaphore' → FOND = 'longueur mot de passe cybersécurité'.",
                "ÉTAPE 2 - CAS 'QUESTION_NON_COMPRISE' : Si 'Actual Output' = 'QUESTION_NON_COMPRISE', détermine si l'Input contient un fond cybersécurité exploitable. Si OUI → SCORE 0.0 (perte totale de sens métier). Si NON → SCORE 8-10 (comportement correct).",
                "ÉTAPE 3 - COMPARAISON SÉMANTIQUE : Compare le sens métier cybersécurité de 'Actual Output' avec celui de 'Input' (en ignorant les consignes de style dans Input).",
                "ÉTAPE 4 - VÉRIFICATION AVEC EXPECTED : Vérifie avec 'Expected Output' que la reformulation reste dans la même portée sémantique métier.",
                "ÉTAPE 5 - DÉTECTION D'ALTÉRATIONS : Pénalise toute altération de sens: généralisation, spécialisation, inversion de sens ou glissement de sujet.",
                "ÉTAPE 6 - SCORE FINAL : N'accorde une note élevée que si le sens métier est fidèlement conservé. Score final uniquement sur la fidélité métier.",
            ],
            rubric=[
                Rubric(
                    score_range=(0, 3),
                    expected_outcome=(
                        "Niveau faible: changement de sens métier clair, glissement de sujet important, "
                        "ou 'QUESTION_NON_COMPRISE' injustifié sur une question cybersécurité claire."
                    ),
                ),
                Rubric(
                    score_range=(4, 7),
                    expected_outcome=(
                        "Niveau moyen: sens global partiellement conservé, avec ambiguïtés ou écarts notables."
                    ),
                ),
                Rubric(
                    score_range=(8, 10),
                    expected_outcome=(
                        "Niveau élevé: sens métier conservé avec précision, sans modification significative. "
                        "'QUESTION_NON_COMPRISE' justifié si Input sans fond cybersécurité exploitable."
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
