from deepeval.test_case import LLMTestCase

from evaluation.metriques_personnalisees.de_deepeval.metrique_bon_nom_document import (
    MetriqueBonNomDocument,
    MetriquesBonNomDocuments,
)
from evaluation.metriques_personnalisees.de_deepeval.metrique_longueur_reponse import (
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

    cas_test_reponse_vide = LLMTestCase(
        input="Question test", actual_output=reponse_bot
    )
    metrique = MetriqueLongueurReponse()
    score = metrique.measure(cas_test_reponse_vide)

    assert score == 0
    assert metrique.is_successful() is False


def test_la_metrique_qui_mesure_la_longeur_de_la_reponse_renvoie_0_si_pas_de_reponse():
    reponse_bot = None

    cas_test_pas_de_reponse = LLMTestCase(
        input="Question test", actual_output=reponse_bot
    )
    metrique = MetriqueLongueurReponse()
    score = metrique.measure(cas_test_pas_de_reponse)

    assert score == 0
    assert metrique.is_successful() is False


def test_metrique_bon_nom_document_en_contexte_retourne_1_si_meme_document():
    metadatas = {
        "nom_document_reponse_bot_0": "document_test",
        "nom_document_verite_terrain_0": "document_test",
    }

    cas_test = LLMTestCase(
        input="Question test", actual_output="", additional_metadata=metadatas
    )
    metrique = MetriqueBonNomDocument(
        nom_document_reponse="nom_document_reponse_bot_0",
        nom_document_verite_terrain="nom_document_verite_terrain_0",
    )
    score = metrique.measure(cas_test)

    assert score == 1
    assert metrique.is_successful() is True


def test_metrique_bon_nom_document_en_contexte_retourne_0_si_document_different():
    metadatas = {
        "nom_document_reponse_bot_0": "document_test",
        "nom_document_verite_terrain_0": "document_autre",
    }

    cas_test = LLMTestCase(
        input="Question test", actual_output="", additional_metadata=metadatas
    )
    metrique = MetriqueBonNomDocument(
        nom_document_reponse="nom_document_reponse_bot_0",
        nom_document_verite_terrain="nom_document_verite_terrain_0",
    )
    score = metrique.measure(cas_test)

    assert score == 0
    assert metrique.is_successful() is False


def test_metriques_bon_nom_documents_en_contexte_retourne_1_si_meme_document():
    metadatas = {
        "nom_document_reponse_bot_0": "document_test",
        "nom_document_reponse_bot_1": "document_test",
        "nom_document_reponse_bot_2": "document_test",
        "nom_document_reponse_bot_3": "document_test",
        "nom_document_reponse_bot_4": "document_test",
        "nom_document_verite_terrain": "document_test",
    }

    cas_test = LLMTestCase(
        input="Question test", actual_output="", additional_metadata=metadatas
    )
    metriques = MetriquesBonNomDocuments.cree_metriques()

    assert len(metriques) == 5
    assert metriques[0].measure(cas_test) == 1
    assert metriques[1].measure(cas_test) == 1
    assert metriques[2].measure(cas_test) == 1
    assert metriques[3].measure(cas_test) == 1
    assert metriques[4].measure(cas_test) == 1
