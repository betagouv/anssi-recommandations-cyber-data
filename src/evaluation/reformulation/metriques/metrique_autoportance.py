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
                Tu es un juge spécialisé dans l'évaluation d'un reformulateur de requêtes pour un système RAG ANSSI.

                Ta mission est STRICTEMENT limitée à évaluer l'autoportance de la reformulation produite.

                Tu disposes de :
                - 'Input' = question utilisateur d'origine
                - 'Actual Output' = reformulation produite
                - 'Expected Output' = reformulation idéale

                DÉFINITION DE L'AUTOPORTANCE :
                Une question est autoportante si elle peut être comprise et traitée seule,
                sans avoir besoin du contexte conversationnel précédent.

                Une question autoportante :
                - nomme explicitement son sujet ou son objet principal,
                - n'a pas besoin du tour précédent pour être comprise,
                - ne contient pas de référence implicite non résolue,
                - est exploitable telle quelle pour une recherche RAG.

                RÔLE DES TROIS CHAMPS :
                - 'Actual Output' est le texte principal à évaluer.
                - 'Input' sert à repérer si la question d'origine contenait des ellipses, pronoms flous ou dépendances contextuelles qui auraient dû être levés.
                - 'Expected Output' sert uniquement de repère secondaire sur le niveau d'explicitation attendu.

                TU DOIS PÉNALISER UNIQUEMENT SI 'Actual Output' dépend d'un contexte absent, par exemple :
                - pronoms ou démonstratifs ambigus : ça, cela, ce sujet, ce point, celui-ci, celui-là,
                - références conversationnelles : et pour ça, dans ce cas, sur ce point, comme avant,
                - entité non nommée ou référent manquant,
                - formulation trop elliptique pour être comprise seule.

                TU NE DOIS PAS PÉNALISER :
                - une reformulation plus longue ou plus explicite,
                - le développement d'un acronyme,
                - une paraphrase,
                - une structure grammaticale différente,
                - une question plus précise que l'attendu, tant qu'elle reste autonome.

                RÈGLE FONDAMENTALE :
                Le score doit être fondé d'abord sur la capacité de 'Actual Output' à être compris seul.
                'Input' et 'Expected Output' ne doivent servir qu'à confirmer si une dépendance contextuelle a bien été levée,
                et non à exiger une similarité textuelle.
                """
            ),
            evaluation_steps=[
                "Examine d'abord 'Actual Output' seul, sans supposer l'existence d'un historique.",
                "Détermine si un lecteur peut comprendre immédiatement le sujet principal et l'objet de la question.",
                "Recherche dans 'Actual Output' des références implicites non résolues : pronoms ambigus, démonstratifs, ellipses, références au tour précédent ou contexte manquant.",
                "Utilise 'Input' pour vérifier si la question d'origine contenait une dépendance contextuelle qui aurait dû être explicitée dans 'Actual Output'.",
                "Utilise 'Expected Output' seulement comme repère secondaire sur le niveau d'explicitation attendu, sans pénaliser une formulation autonome mais différente.",
                "Ignore les différences de style, de longueur, de richesse lexicale et de formulation interrogative.",
                "Attribue un score élevé dès lors que 'Actual Output' est compréhensible et exploitable seul.",
            ],
            rubric=[
                Rubric(
                    score_range=(0, 2),
                    expected_outcome=(
                        "Question non autoportante : elle dépend clairement du contexte précédent, contient des références ambiguës non résolues ou ne permet pas d'identifier le sujet sans historique."
                    ),
                ),
                Rubric(
                    score_range=(3, 5),
                    expected_outcome=(
                        "Question partiellement autoportante : le sujet général est devinable, mais au moins une référence reste ambiguë ou un élément contextuel important manque."
                    ),
                ),
                Rubric(
                    score_range=(6, 8),
                    expected_outcome=(
                        "Question globalement autoportante : elle est compréhensible seule et exploitable, malgré de légères ambiguïtés mineures qui ne bloquent pas l'interprétation."
                    ),
                ),
                Rubric(
                    score_range=(9, 10),
                    expected_outcome=(
                        "Question pleinement autoportante : elle est immédiatement compréhensible seule, sans anaphore ambiguë, sans dépendance au contexte conversationnel, et directement exploitable en RAG."
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
