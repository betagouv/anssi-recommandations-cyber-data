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
                Tu es un juge spécialisé dans l'évaluation d'un reformulateur de requêtes pour un système RAG ANSSI.

                Ta mission est STRICTEMENT limitée à évaluer la conservation des contraintes utiles entre :
                - 'Input' = question utilisateur d'origine
                - 'Expected Output' = reformulation idéale
                - 'Actual Output' = reformulation produite

                RÔLE DES TROIS CHAMPS :
                - 'Input' sert à repérer les contraintes initialement présentes dans la question utilisateur.
                - 'Expected Output' sert de référence sur les contraintes qui doivent être conservées après reformulation.
                - 'Actual Output' est la sortie à évaluer.

                Définition d'une contrainte utile :
                - entité métier, réglementaire ou technique,
                - acronyme ou nom développé,
                - produit, service, protocole, technologie ou concept précis,
                - acteur, population, périmètre, objet ciblé,
                - restriction explicite ou précision indispensable à la recherche.

                RÈGLE FONDAMENTALE :
                Une contrainte est considérée comme conservée si 'Actual Output' exprime le même référent utile que
                celui attendu, même avec une forme différente.

                Sont considérées comme ÉQUIVALENTES :
                - acronyme ↔ forme développée,
                - variante typographique ou de casse,
                - traduction usuelle du même concept,
                - reformulation explicative du même terme métier,
                - singulier/pluriel si le sens ne change pas.

                Exemples d'équivalences à accepter :
                - DDoS == DDOS == Distributed Denial of Service == attaque par déni de service distribué
                - MFA == authentification multifacteur
                - DSI == direction des systèmes d'information
                - SIIV == système d'information d'importance vitale
                - OIV == opérateur d'importance vitale

                IMPORTANT :
                - N'évalue PAS ici la fidélité métier globale.
                - N'évalue PAS ici la suppression des parasites.
                - N'évalue PAS ici l'autoportance.
                - N'évalue PAS la fluidité ou la qualité stylistique.
                - Ne pénalise PAS une reformulation plus explicite.
                - Ne pénalise PAS une expansion correcte d'acronyme.
                - Ne pénalise PAS une traduction usuelle correcte du même concept.

                TU DOIS RAISONNER AINSI :
                - Identifie d'abord dans 'Input' les contraintes utiles portées par la question d'origine.
                - Vérifie ensuite lesquelles de ces contraintes sont confirmées ou précisées dans 'Expected Output'.
                - Évalue enfin si 'Actual Output' conserve bien ces contraintes attendues, même sous une autre forme.
                - Si 'Actual Output' ajoute une contrainte absente de 'Input' et de 'Expected Output', pénalise-la.
                - Si 'Actual Output' remplace une contrainte précise par une notion plus vague, pénalise-la.
                - Si 'Actual Output' conserve la même contrainte via acronyme, forme développée ou traduction usuelle, ne pénalise pas.

                Exemple important :
                - Input : "Qu'est-ce qu'une attaque DDOS ?"
                - Expected Output : "Qu'est-ce qu'une attaque DDOS (attaque par déni de service distribué) ?"
                - Actual Output : "Qu'est-ce qu'une attaque DDoS (Distributed Denial of Service) ?"
                => Score élevé attendu, car la contrainte utile "attaque DDoS/DDOS" est conservée.
                La différence de casse, de langue ou d'expansion ne doit pas être considérée comme une perte de contrainte.
                """
            ),
            evaluation_steps=[
                "Identifie dans 'Input' les contraintes utiles présentes dans la question d'origine : entités métier, acronymes, concepts techniques, périmètres, acteurs, objets ciblés.",
                "Utilise 'Expected Output' pour confirmer quelles contraintes doivent être conservées après reformulation.",
                "Pour chaque contrainte attendue, vérifie si 'Actual Output' conserve le même référent, même sous une autre forme acceptable : acronyme, forme développée, traduction usuelle ou reformulation explicative.",
                "Ignore complètement les différences de style, de ponctuation, d'ordre des mots, de casse et de structure grammaticale.",
                "Ne pénalise pas une reformulation qui ajoute une expansion correcte d'acronyme ou une précision équivalente.",
                "Pénalise seulement les pertes réelles de contrainte, les généralisations abusives, les remplacements vagues ou les ajouts incompatibles avec l'input et l'attendu.",
                "Attribue un score élevé dès lors que les contraintes utiles issues de l'input et confirmées par l'attendu sont conservées en substance dans 'Actual Output', même si leur forme textuelle diffère.",
            ],
            rubric=[
                Rubric(
                    score_range=(0, 2),
                    expected_outcome=(
                        "Plusieurs contraintes explicites importantes issues de la question d'origine et attendues dans la reformulation ne sont plus conservées, ou sont remplacées par des notions vagues, incorrectes ou incompatibles."
                    ),
                ),
                Rubric(
                    score_range=(3, 5),
                    expected_outcome=(
                        "La conservation des contraintes est partielle : au moins une contrainte importante de l'input ou de l'attendu est perdue, affaiblie ou mal préservée."
                    ),
                ),
                Rubric(
                    score_range=(6, 8),
                    expected_outcome=(
                        "La plupart des contraintes utiles issues de l'input et confirmées par l'attendu sont conservées ; les écarts restants sont mineurs et n'altèrent pas fortement la précision recherchée."
                    ),
                ),
                Rubric(
                    score_range=(9, 10),
                    expected_outcome=(
                        "Toutes les contraintes utiles issues de l'input et confirmées par l'attendu sont conservées, y compris via acronymes, formes développées, traductions usuelles ou reformulations équivalentes, sans perte de précision."
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
