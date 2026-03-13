from evaluation.reformulation.evaluation import (
    QuestionAEvaluer,
    EvaluateurReformulation,
)


def test_evalue_la_metrique_suppression_parasite(
    resultat_collecte_mqc_avec_deux_resultats,
    evaluateur_de_test_avec_metriques,
    un_client_albert,
):
    question = QuestionAEvaluer(
        question="Question ?", reformulation_ideale="Question idéale reformulée ?"
    )
    client_albert = (
        un_client_albert()
        .retourne_la_reformulation_pour_la_question(
            "Question reformulée ?", "Question ?"
        )
        .construis()
    )

    EvaluateurReformulation(
        client_albert, "Prompt", evaluateur_de_test_avec_metriques
    ).evalue([question])

    assert evaluateur_de_test_avec_metriques.nombre_metriques_soumise == 1
    assert len(evaluateur_de_test_avec_metriques.metriques_deepeval_soumises) == 1
    assert (
        evaluateur_de_test_avec_metriques.metriques_deepeval_soumises[0].__name__
        == "MetriqueSuppressionParasites"
    )
