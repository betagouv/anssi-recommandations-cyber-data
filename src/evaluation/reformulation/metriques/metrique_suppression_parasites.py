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
                INSTRUCTION CRITIQUE PRIORITAIRE :
                Compare 'Actual Output' et 'Expected Output' en ignorant UNIQUEMENT la casse, les espaces multiples et les apostrophes.
                Si les deux textes sont identiques après cette normalisation, tu DOIS retourner un score de 1.0.
                Exemple : "Qu'est-ce que MesQuestionsCyber ?" == "Qu'est-ce que MesQuestionsCyber ?" → SCORE 1.0 OBLIGATOIRE
                
                Tu es un juge expert en reformulation de question RAG pour l'ANSSI.
                Tu notes uniquement la suppression des éléments parasites dans la reformulation.

                Élément parasite = consigne de style (métaphore, analogie, poème, ton, format, longueur, rôle, persona),
                hésitation, tic de langage, répétition vide, bruit de transcription, artefact technique (balise, métadonnée),
                fragment hors sujet ou sans valeur informative.

                COMPORTEMENT ATTENDU DU REFORMULATEUR :
                - Supprime les éléments parasites de l'Input
                - Ajoute la forme développée des acronymes techniques cybersécurité (ex: DDOS → DDoS (distributed denial of service))
                - Rend la question autoportante si nécessaire
                - Retourne "QUESTION_NON_COMPRISE" si l'Input ne contient QUE des consignes de style SANS fond cybersécurité exploitable
                
                RÈGLES D'ÉVALUATION STRICTES :
                
                CAS 1 - 'Actual Output' = "QUESTION_NON_COMPRISE" :
                  → Si 'Input' contient un fond cybersécurité clair (ex: "quelle est la bonne longueur d'un mot de passe en cybersécurité") 
                     MÊME avec des consignes de style → SCORE TRÈS FAIBLE (0-0.2)
                     Raison: Le reformulateur a échoué à extraire le fond cybersécurité exploitable
                  → Si 'Input' ne contient QUE des consignes de style sans aucun fond cybersécurité → SCORE ÉLEVÉ (8-10)
                
                CAS 2 - Input sans parasite :
                  → Si l'Input ne contient AUCUN parasite et que la sortie est propre → SCORE ÉLEVÉ (8-10)
                  → L'ajout de la forme développée d'un acronyme technique est POSITIF, ne le pénalise JAMAIS
                
                CAS 3 - Input avec parasites :
                  → Évalue le taux de suppression des parasites
                  → Pénalise si des parasites restent ou si de nouveaux parasites sont introduits

                Important:
                - Les consignes de style ("avec une métaphore culinaire", "en poème", "réponds comme un expert") sont des parasites à supprimer.
                - N'évalue pas ici l'autoportance, la fidélité métier, ni la conservation de toutes les contraintes.
                - Ne pénalise pas les différences de style, de ponctuation, de casse, ni les reformulations lexicales.
                - Ne pénalise JAMAIS l'ajout de la forme développée d'un acronyme technique.
                """
            ),
            evaluation_steps=[
                'ÉTAPE 0 - VÉRIFICATION D\'ÉGALITÉ STRICTE : Normalise \'Actual Output\' et \'Expected Output\' (minuscules, espaces simples, apostrophes uniformes). Si identiques → retourne {"score": 1.0, "reason": "Match parfait"} IMMÉDIATEMENT.',
                "ÉTAPE 1 - ANALYSE DE L'INPUT : Identifie le fond cybersécurité/IT dans 'Input' (sujet technique, question métier). Identifie séparément les consignes de style parasites.",
                "ÉTAPE 2 - CAS 'QUESTION_NON_COMPRISE' : Si 'Actual Output' = 'QUESTION_NON_COMPRISE', vérifie si l'Input contient un fond cybersécurité exploitable. Si OUI → SCORE 0-0.2 (échec grave). Si NON (que du style) → SCORE 8-10.",
                "ÉTAPE 3 - ÉVALUATION DE LA SUPPRESSION : Vérifie que 'Actual Output' supprime les parasites de l'Input sans introduire de nouveau bruit.",
                "ÉTAPE 4 - VALORISATION DES AJOUTS POSITIFS : L'ajout de la forme développée d'un acronyme technique est un comportement POSITIF, ne le pénalise JAMAIS.",
                "ÉTAPE 5 - INPUT SANS PARASITE : Si l'Input ne contient aucun parasite et que la sortie est propre (avec ou sans forme développée d'acronyme), attribue un score élevé (8-10).",
                "ÉTAPE 6 - SCORE FINAL : Pénalise uniquement si des parasites de l'Input restent présents ou si de nouveaux parasites (hors forme développée d'acronyme) sont introduits.",
            ],
            rubric=[
                Rubric(
                    score_range=(0, 3),
                    expected_outcome=(
                        "Niveau faible: suppression insuffisante des parasites (nombreux parasites/consignes de style conservés) "
                        "ou 'QUESTION_NON_COMPRISE' injustifié sur une question cybersécurité claire."
                    ),
                ),
                Rubric(
                    score_range=(4, 7),
                    expected_outcome=(
                        "Niveau moyen: nettoyage partiel à correct, avec encore quelques parasites résiduels."
                    ),
                ),
                Rubric(
                    score_range=(8, 10),
                    expected_outcome=(
                        "Niveau élevé: suppression excellente des parasites et consignes de style, sortie propre et concise. "
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
