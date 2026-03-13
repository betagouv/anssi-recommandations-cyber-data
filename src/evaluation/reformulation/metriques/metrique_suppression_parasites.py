from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

from evaluation.deepeval.client_deepeval_albert import ClientDeepEvalAlbert


class MetriqueSuppressionParasites(GEval):
    def __init__(self):
        super().__init__(
            name="MetriqueSuppressionParasites",
            criteria=(
                """
                        Tu es un juge expert en nettoyage de texte.
                        
                        Ta mission est d'évaluer si la sortie nettoie correctement les éléments parasites
                        présents dans le texte d'entrée, tout en conservant fidèlement l'information utile.
                        
                        Règles de jugement :
                        1. Les éléments parasites doivent être supprimés.
                        2. L'information utile et pertinente doit être conservée.
                        3. Aucun contenu nouveau ne doit être ajouté.
                        4. La reformulation doit rester minimale : on préfère supprimer le bruit, pas réécrire tout le texte.
                        5. Si la sortie supprime une information utile, la note doit baisser fortement.
                        6. Si la sortie conserve encore beaucoup de parasites, la note doit baisser fortement.
                        7. Si la sortie invente, généralise ou résume au-delà du nécessaire, la note doit baisser.
                        
                        Définition des éléments parasites :
                        - répétitions inutiles
                        - hésitations
                        - tics de langage
                        - bruit de transcription
                        - balises, métadonnées ou artefacts techniques
                        - fragments sans valeur informative
                        - remplissage non pertinent
                        
                        Tu dois retourner un JSON strict avec ce format exact :
                        {{
                          "score": <nombre entre 0 et 1>,
                          "reason": "<explication courte, factuelle et précise>"
                        }}
                        
                        Consignes de scoring :
                        - 1.0 = suppression excellente des parasites, conservation fidèle du contenu utile
                        - 0.7 à 0.9 = bon nettoyage avec défauts mineurs
                        - 0.4 à 0.6 = nettoyage partiel ou quelques pertes d'information
                        - 0.1 à 0.3 = nettoyage faible ou pertes importantes
                        - 0.0 = sortie inutilisable, hallucination, ou suppression du contenu important
                        """
            ),
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
                LLMTestCaseParams.EXPECTED_OUTPUT,
            ],
            model=ClientDeepEvalAlbert(),
            _include_g_eval_suffix=False,
        )
