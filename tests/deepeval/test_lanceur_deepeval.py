from deepeval.test_case import LLMTestCase
from evaluation.lanceur_deepeval import LanceurExperienceDeepeval
from journalisation.experience import (
    EntrepotExperienceMemoire,
)


def test_evalue_un_jeu_de_donnees(
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test
):
    entrepot_experience = EntrepotExperienceMemoire()
    lanceur_experience = LanceurExperienceDeepeval(
        entrepot_experience, evaluateur_de_test
    )

    id_experience = lanceur_experience.lance_l_experience(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant
    )

    experience_creee = entrepot_experience.lit(id_experience)
    assert experience_creee.metriques[0]["bon_nom_document_en_contexte_2"] == 1
    assert experience_creee.metriques[0]["score_bon_nom_document_en_contexte_2"] == 0.7
    assert experience_creee.metriques[0]["hallucination"] == 0.6


def test_evalue_un_jeu_de_donnees_avec_des_cas_de_test(
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test
):
    entrepot_experience = EntrepotExperienceMemoire()

    evaluateur_deepeval = evaluateur_de_test
    lanceur_experience = LanceurExperienceDeepeval(
        entrepot_experience, evaluateur_deepeval
    )
    lanceur_experience.lance_l_experience(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant
    )

    assert len(evaluateur_deepeval.cas_de_test_executes) == 2
    assert (
        evaluateur_deepeval.cas_de_test_executes[0].__dict__
        == LLMTestCase(
            input="Qu'est-ce que l'authentification ?",
            actual_output="réponse mqc",
            retrieval_context=["test"],
            context=["test"],
            additional_metadata={},
            expected_output="réponse envisagée",
        ).__dict__
    )

    assert (
        evaluateur_deepeval.cas_de_test_executes[1].__dict__
        == LLMTestCase(
            input="Qu'elle est la bonne longueur d'un mot de passe?",
            actual_output="réponse mqc",
            retrieval_context=["test"],
            context=["test"],
            additional_metadata={},
            expected_output="réponse envisagée",
        ).__dict__
    )


def test_evalue_un_jeu_de_donnees_avec_les_metriques_deepeval(
    resultat_collecte_mqc_avec_deux_resultats, evaluateur_de_test
):
    entrepot_experience = EntrepotExperienceMemoire()

    evaluateur_deepeval = evaluateur_de_test
    lanceur_experience = LanceurExperienceDeepeval(
        entrepot_experience, evaluateur_deepeval
    )
    lanceur_experience.lance_l_experience(
        resultat_collecte_mqc_avec_deux_resultats._chemin_courant
    )

    assert len(evaluateur_deepeval.metriques_soumises) == 4
    assert evaluateur_deepeval.metriques_soumises[0].__name__ == "Hallucination"
    assert evaluateur_deepeval.metriques_soumises[1].__name__ == "Answer Relevancy"
    assert evaluateur_deepeval.metriques_soumises[2].__name__ == "Faithfulness"
    assert evaluateur_deepeval.metriques_soumises[3].__name__ == "Toxicity"
