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
                Tu es un juge spécialisé dans l'évaluation d'un reformulateur de requêtes pour un système RAG ANSSI.

                Ta mission est STRICTEMENT limitée à évaluer la fidélité métier.

                Tu disposes de :
                - 'Input' = question utilisateur d'origine, pouvant contenir des parasites de style
                - 'Actual Output' = reformulation produite
                - 'Expected Output' = reformulation idéale
                - 'Expected Output' ne doit pas être utilisé comme cible de similarité textuelle.
                - 'Expected Output' sert uniquement à confirmer le besoin métier attendu.
                - Une différence de formulation entre 'Actual Output' et 'Expected Output' n'est pas une erreur si le sujet, l'intention et la portée métier restent identiques.

                DÉFINITION DE LA FIDÉLITÉ MÉTIER :
                La fidélité métier est élevée si 'Actual Output' conserve le même besoin cybersécurité/IT que 'Input',
                une fois les éléments parasites ignorés.

                Le besoin métier comprend :
                - le sujet principal,
                - l'intention de la question,
                - le problème cyber/IT posé,
                - la portée métier utile.

                IMPORTANT :
                - Les consignes de style, ton, format, métaphore, humour, persona, rôle, longueur ou structure de réponse
                  ne font PAS partie du sens métier.
                - Supprimer ces éléments parasites ne doit JAMAIS faire baisser fortement la fidélité métier.
                - Une reformulation syntaxiquement différente peut être parfaitement fidèle métier.
                - Le développement d'un acronyme ne modifie pas à lui seul la fidélité métier.
                - Le changement d'ordre des mots ne doit pas être pénalisé s'il ne change pas le sens.
                - N'évalue PAS ici l'autoportance.
                - N'évalue PAS ici la suppression des parasites comme critère autonome.
                - N'évalue PAS ici la conservation fine de toutes les contraintes lexicales.

                CAS SPÉCIAL : 'QUESTION_NON_COMPRISE'
                - Si 'Actual Output' vaut exactement 'QUESTION_NON_COMPRISE', détermine si 'Input' contient,
                  après retrait des parasites éventuels, un besoin cybersécurité/IT identifiable et exploitable.
                - Si OUI : la fidélité métier est très faible.
                - Si NON : la fidélité métier peut être élevée.

                RÈGLE FONDAMENTALE :
                Le score doit être fondé d'abord sur la relation entre 'Input' et 'Actual Output'.
                'Expected Output' ne sert que de repère secondaire pour confirmer le sens attendu.

                TU DOIS PÉNALISER UNIQUEMENT LES CAS SUIVANTS :
                - changement de sujet principal,
                - changement d'intention,
                - glissement vers un autre problème cyber/IT,
                - généralisation abusive qui fait perdre la question réelle,
                - spécialisation non demandée,
                - inversion du sens,
                - 'QUESTION_NON_COMPRISE' alors que l'input contenait bien une demande cyber/IT exploitable.

                TU NE DOIS PAS PÉNALISER :
                - la suppression d'une consigne de style,
                - une reformulation lexicale proche,
                - une reformulation syntaxique,
                - le déplacement d'un complément dans la phrase,
                - une reformulation plus explicite,
                - un développement d'acronyme,
                - une différence de formulation avec 'Expected Output' si le besoin métier reste identique.
                """
            ),
            evaluation_steps=[
                "Analyse d'abord 'Input' et retire mentalement tous les éléments parasites de style, ton, format, métaphore, humour, rôle ou longueur.",
                "Identifie dans 'Input' nettoyé le besoin cybersécurité/IT central : sujet, intention et portée métier.",
                "Analyse ensuite 'Actual Output' et identifie son besoin cybersécurité/IT central.",
                "Détermine si 'Actual Output' conserve le même sujet principal et la même intention métier que 'Input' nettoyé.",
                "Ignore complètement les différences de style, de structure grammaticale, d'ordre des mots, de ponctuation et les suppressions de parasites.",
                "Utilise 'Expected Output' seulement comme repère secondaire pour confirmer le sens attendu, sans exiger de similarité de surface.",
                "Si 'Actual Output' vaut 'QUESTION_NON_COMPRISE', décide si 'Input' nettoyé contenait ou non un besoin cyber/IT exploitable.",
                "Attribue un score élevé dès lors que le besoin métier reste le même, même si la formulation diffère nettement.",
            ],
            rubric=[
                Rubric(
                    score_range=(0, 2),
                    expected_outcome=(
                        "Le besoin métier n'est pas conservé : sujet changé, intention modifiée, glissement important, inversion de sens ou rejet injustifié en QUESTION_NON_COMPRISE."
                    ),
                ),
                Rubric(
                    score_range=(3, 5),
                    expected_outcome=(
                        "Le besoin métier est seulement partiellement conservé : le sujet général reste proche, mais un écart notable de portée ou d'intention est présent."
                    ),
                ),
                Rubric(
                    score_range=(6, 8),
                    expected_outcome=(
                        "Le besoin métier est globalement conservé : mêmes sujet et intention, avec seulement des écarts mineurs qui n'altèrent pas fortement la demande."
                    ),
                ),
                Rubric(
                    score_range=(9, 10),
                    expected_outcome=(
                        "Le besoin métier est conservé de façon très fidèle : même sujet, même intention, même portée utile, sans glissement sémantique, même si la formulation diffère ou que des parasites ont été supprimés."
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
