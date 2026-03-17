from deepeval.metrics import GEval
from deepeval.metrics.g_eval import Rubric
from deepeval.test_case import LLMTestCaseParams

from evaluation.mqc.client_deepeval_albert import ClientDeepEvalAlbert


class MetriqueSuppressionParasites(GEval):
    def __init__(self, **kwargs):
        super().__init__(
            name="MetriqueSuppressionParasites",
            criteria=(
                """
                Tu es un juge spécialisé dans l'évaluation d'un reformulateur de requêtes pour un système RAG ANSSI.

                Ta mission est STRICTEMENT limitée à évaluer la suppression des parasites.

                Tu disposes de trois éléments :
                - 'Input' = question utilisateur d'origine, potentiellement bruitée
                - 'Actual Output' = reformulation produite par le reformulateur évalué
                - 'Expected Output' = vérité terrain / reformulation idéale

                RÈGLE FONDAMENTALE :
                - 'Expected Output' est une vérité terrain déjà nettoyée.
                - 'Expected Output' ne contient AUCUN parasite.
                - 'Expected Output' conserve uniquement le contenu utile à la recherche documentaire.
                - Donc tout élément parasite encore visible dans 'Actual Output' doit être considéré comme un échec de suppression.
                - À l'inverse, l'absence dans 'Actual Output' d'un élément présent dans 'Input' n'est PAS une faute si cet élément était parasite et ne figure pas dans 'Expected Output'.

                Définition d'un parasite :
                - consigne de style, de ton ou de format,
                - demande de métaphore, analogie, poème, humour, persona, rôle,
                - demande de longueur, structure ou mise en forme,
                - hésitation, répétition vide, tic de langage,
                - bruit de transcription,
                - artefact technique, balise, métadonnée,
                - fragment hors sujet sans valeur informative pour la recherche.

                Exemples de parasites :
                - "avec une métaphore de cuisine"
                - "réponds comme un expert"
                - "en trois points"
                - "en mode humoristique"
                - "fais court"
                - "euh", "ben", répétitions inutiles
                - balises, fragments techniques ou métadonnées sans valeur métier

                IMPORTANT :
                - N'évalue PAS ici l'autoportance.
                - N'évalue PAS ici la fidélité métier globale.
                - N'évalue PAS ici la conservation fine des contraintes.
                - N'évalue PAS la qualité stylistique générale.
                - Ne pénalise PAS une reformulation plus explicite si elle reste propre.
                - Ne pénalise PAS le développement d'un acronyme technique.
                - Ne pénalise PAS les différences de formulation si les parasites ont bien été supprimés.

                LOGIQUE D'ÉVALUATION :
                - Utilise 'Input' pour repérer les éléments potentiellement parasites.
                - Utilise 'Expected Output' comme référence de ce qui doit rester après nettoyage.
                - Si un élément de 'Input' disparaît dans 'Expected Output', il est probablement parasite ou non essentiel à cette métrique.
                - Si un parasite de 'Input' se retrouve encore dans 'Actual Output', cela doit être pénalisé.
                - Si 'Actual Output' contient des formulations de style, ton, format ou bruit absentes de 'Expected Output', cela doit être pénalisé.
                - Si 'Actual Output' est aussi propre que 'Expected Output' concernant les parasites, le score doit être élevé, même si la formulation diffère.

                CAS SPÉCIAL : 'QUESTION_NON_COMPRISE'
                - Si 'Actual Output' vaut exactement 'QUESTION_NON_COMPRISE', détermine si 'Input' contenait malgré tout un fond cybersécurité/IT exploitable.
                - Si OUI : score très faible, car le reformulateur n'a pas extrait le fond utile.
                - Si NON : score élevé, car il n'y avait pas de contenu métier exploitable derrière le bruit ou les consignes parasites.
                """
            ),
            evaluation_steps=[
                "Analyse 'Input' et distingue clairement le fond cyber/IT exploitable des éléments parasites.",
                "Identifie les parasites présents dans 'Input' : style, ton, format, rôle, métaphore, bruit, hésitations, artefacts ou fragments hors sujet.",
                "Examine 'Actual Output' et vérifie si ces parasites ont été supprimés.",
                "Vérifie qu'aucun nouveau parasite n'a été introduit dans 'Actual Output'.",
                "Si 'Actual Output' vaut 'QUESTION_NON_COMPRISE', décide si 'Input' contenait ou non un fond cyber/IT exploitable.",
                "Ignore les différences de style, de longueur, de structure grammaticale et le développement d'acronymes.",
                "Attribue un score élevé dès lors que les parasites ont disparu et que la sortie reste propre."
            ],
            rubric=[
                Rubric(
                    score_range=(0, 2),
                    expected_outcome=(
                        "Suppression très insuffisante : les parasites restent présents, de nouveaux parasites sont introduits, ou 'QUESTION_NON_COMPRISE' est utilisé alors qu'un fond cyber/IT exploitable était présent."
                    ),
                ),
                Rubric(
                    score_range=(3, 5),
                    expected_outcome=(
                        "Suppression partielle : une partie des parasites a disparu, mais il reste encore des traces notables de style, de bruit ou de consignes parasites."
                    ),
                ),
                Rubric(
                    score_range=(6, 8),
                    expected_outcome=(
                        "Bonne suppression : la plupart des parasites ont été retirés ; les écarts restants sont mineurs et n'empêchent pas une sortie propre."
                    ),
                ),
                Rubric(
                    score_range=(9, 10),
                    expected_outcome=(
                        "Excellente suppression : les parasites ont été retirés proprement, aucun parasite significatif ne subsiste, et 'QUESTION_NON_COMPRISE' est utilisé seulement quand aucun fond métier exploitable n'était présent."
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