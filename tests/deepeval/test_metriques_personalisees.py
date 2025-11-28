from deepeval.test_case import LLMTestCase
from evaluation.metriques_personnalisees.de_deepeval.metrique_bon_nom_document import (
    MetriqueBonNomDocument,
    MetriquesBonNomDocuments,
)
from evaluation.metriques_personnalisees.de_deepeval.metrique_bons_numeros_pages import (
    MetriquesBonsNumerosPages,
    MetriqueBonNumeroPage,
)
from evaluation.metriques_personnalisees.de_deepeval.metrique_longueur_reponse import (
    MetriqueLongueurReponse,
)
from evaluation.metriques_personnalisees.de_deepeval.metrique_score_numero_page import (
    MetriqueScoreNumeropage,
    MetriquesScoreNumeropage,
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


def test_metrique_bon_numero_page_en_contexte_est_en_succes():
    metadatas = {
        "numero_page_reponse_bot_0": "1",
        "numero_page_verite_terrain": "1",
    }

    cas_test = LLMTestCase(
        input="Question test", actual_output="", additional_metadata=metadatas
    )
    metrique = MetriqueBonNumeroPage("numero_page_reponse_bot_0")
    metrique.measure(cas_test)

    assert metrique.is_successful() is True


def test_metrique_bon_numero_page_en_contexte_est_en_echec():
    metadatas = {
        "numero_page_reponse_bot_0": "1",
        "numero_page_verite_terrain": "2",
    }

    cas_test = LLMTestCase(
        input="Question test", actual_output="", additional_metadata=metadatas
    )
    metrique = MetriqueBonNumeroPage("numero_page_reponse_bot_0")
    metrique.measure(cas_test)

    assert metrique.is_successful() is False


def test_metriques_bons_numeros_pages_en_contexte_retourne_1_si_meme_page():
    metadatas = {
        "numero_page_reponse_bot_0": "1",
        "numero_page_reponse_bot_1": "2",
        "numero_page_reponse_bot_2": "1",
        "numero_page_reponse_bot_3": "4",
        "numero_page_reponse_bot_4": "1",
        "numero_page_verite_terrain": "1",
    }

    cas_test = LLMTestCase(
        input="Question test", actual_output="", additional_metadata=metadatas
    )
    metriques = MetriquesBonsNumerosPages.cree_metriques()

    assert len(metriques) == 5
    assert metriques[0].measure(cas_test) == 1
    assert metriques[1].measure(cas_test) == 0
    assert metriques[2].measure(cas_test) == 1
    assert metriques[3].measure(cas_test) == 0
    assert metriques[4].measure(cas_test) == 1


def test_metrique_score_numero_page_en_contexte_est_en_succes():
    metadatas = {
        "numero_page_reponse_bot_0": "1",
        "numero_page_verite_terrain": "1",
    }
    cas_test = LLMTestCase(
        input="Question test", actual_output="", additional_metadata=metadatas
    )
    metrique = MetriqueScoreNumeropage("numero_page_reponse_bot_0")

    resultat = metrique.measure(cas_test)

    assert resultat == 1
    assert metrique.is_successful() is True


def test_metrique_score_numero_page_en_contexte_est_en_echec():
    metadatas = {
        "numero_page_reponse_bot_0": "1",
        "numero_page_verite_terrain": "2",
    }
    cas_test = LLMTestCase(
        input="Question test", actual_output="", additional_metadata=metadatas
    )
    metrique = MetriqueScoreNumeropage("numero_page_reponse_bot_0")

    resultat = metrique.measure(cas_test)

    assert resultat == 0.62
    assert metrique.is_successful() is False


def test_metriques_score_numero_page_en_contexte_retourne_le_score_base_sur_la_distance():
    metadatas = {
        "numero_page_reponse_bot_0": "86",
        "numero_page_reponse_bot_1": "72",
        "numero_page_reponse_bot_2": "11",
        "numero_page_reponse_bot_3": "10",
        "numero_page_reponse_bot_4": "5",
        "numero_page_verite_terrain": "10",
    }
    cas_test = LLMTestCase(
        input="Question test", actual_output="", additional_metadata=metadatas
    )
    metriques = MetriquesScoreNumeropage.cree_metriques()

    assert len(metriques) == 5
    assert metriques[0].measure(cas_test) == 0.22
    assert metriques[1].measure(cas_test) == 0.22
    assert metriques[2].measure(cas_test) == 0.62
    assert metriques[3].measure(cas_test) == 1
    assert metriques[4].measure(cas_test) == 0.35
