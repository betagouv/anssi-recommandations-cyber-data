from evaluation.reformulation.evaluation import (
    QuestionAEvaluer,
    EvaluateurReformulation,
)


def test_evalue_les_metriques_de_reformulation(
    evaluateur_de_test_avec_metriques,
    un_client_albert_de_reformulation,
    un_bus_d_evenement,
):
    question = QuestionAEvaluer(
        question="Question ?", reformulation_ideale="Question idéale reformulée ?"
    )
    client_albert = (
        un_client_albert_de_reformulation()
        .retourne_la_reformulation_pour_la_question(
            "Question reformulée ?", "Question ?"
        )
        .construis()
    )

    EvaluateurReformulation(
        client_albert, "Prompt", evaluateur_de_test_avec_metriques, un_bus_d_evenement
    ).evalue([question])

    assert evaluateur_de_test_avec_metriques.nombre_metriques_soumise == 4

    metriques_soumises = (
        evaluateur_de_test_avec_metriques.metriques_deepeval_soumises
        + evaluateur_de_test_avec_metriques.metriques_personnalisees_soumises
    )
    assert [metrique.__name__ for metrique in metriques_soumises] == [
        "MetriqueSuppressionParasites",
        "MetriqueConservationContraintes",
        "MetriqueAutoportance",
        "MetriqueFideliteMetier",
    ]


def test_evalue_les_cas_de_tests(
    evaluateur_de_test_avec_metriques,
    un_client_albert_de_reformulation,
    un_bus_d_evenement,
):
    premiere_question = QuestionAEvaluer(
        question="Question ?", reformulation_ideale="Question idéale reformulée ?"
    )
    deuxieme_question = QuestionAEvaluer(
        question="Question 2 ?", reformulation_ideale="Question 2 idéale reformulée ?"
    )
    client_albert = (
        un_client_albert_de_reformulation()
        .retourne_la_reformulation_pour_la_question(
            "Question reformulée ?", "Question ?"
        )
        .retourne_la_reformulation_pour_la_question(
            "Question reformulée 2 ?", "Question 2 ?"
        )
        .construis()
    )

    EvaluateurReformulation(
        client_albert, "Prompt", evaluateur_de_test_avec_metriques, un_bus_d_evenement
    ).evalue([premiere_question, deuxieme_question])

    assert len(evaluateur_de_test_avec_metriques.cas_de_test_executes) == 2
    premier_cas = evaluateur_de_test_avec_metriques.cas_de_test_executes[0]
    assert premier_cas.input == "Question ?"
    assert premier_cas.actual_output == "Question reformulée ?"
    assert premier_cas.expected_output == "Question idéale reformulée ?"

    deuxieme_cas = evaluateur_de_test_avec_metriques.cas_de_test_executes[1]
    assert deuxieme_cas.input == "Question 2 ?"
    assert deuxieme_cas.actual_output == "Question reformulée 2 ?"
    assert deuxieme_cas.expected_output == "Question 2 idéale reformulée ?"
