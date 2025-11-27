from deepeval.test_case import LLMTestCase
from evaluation.metriques_personnalisees.metrique_longueur_reponse import (
    MetriqueLongueurReponse,
)


def test_la_metrique_qui_mesure_la_longeur_de_la_reponse():
    reponse_bot = "Courte réponse"

    cas_test_court = LLMTestCase(input="Question test", actual_output=reponse_bot)
    metrique = MetriqueLongueurReponse()
    score = metrique.measure(cas_test_court)

    assert score == len(reponse_bot)
    assert metrique.is_successful() is True

def test_la_metrique_qui_mesure_la_longeur_de_la_reponse_renvoie_0_si_reponse_vide():
    reponse_bot = ""

    cas_test_reponse_vide = LLMTestCase(input="Question test", actual_output=reponse_bot)
    metrique = MetriqueLongueurReponse()
    score = metrique.measure(cas_test_reponse_vide)

    assert score == 0
    assert metrique.is_successful() is False

def test_la_metrique_qui_mesure_la_longeur_de_la_reponse_renvoie_0_si_pas_de_reponse():
    reponse_bot = None

    cas_test_pas_de_reponse = LLMTestCase(input="Question test", actual_output=reponse_bot)
    metrique = MetriqueLongueurReponse()
    score = metrique.measure(cas_test_pas_de_reponse)

    assert score == 0
    assert metrique.is_successful() is False
