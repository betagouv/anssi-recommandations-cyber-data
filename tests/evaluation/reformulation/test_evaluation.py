from deepeval.evaluate.types import TestResult

from evaluation.reformulation.evaluation import (
    QuestionAEvaluer,
    EvaluateurReformulation,
)


def test_reformule_la_question(
    un_client_albert, evaluateur_de_test_simple, un_bus_d_evenement
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
    resultat = EvaluateurReformulation(
        client_albert, "Prompt", evaluateur_de_test_simple, un_bus_d_evenement
    ).evalue([question])

    assert len(resultat) == 1
    assert resultat[0].question == "Question ?"
    assert resultat[0].question_reformulee == "Question reformulée ?"
    assert resultat[0].reformulation_ideale == "Question idéale reformulée ?"


def test_reformule_toutes_les_questions(
    un_client_albert, evaluateur_de_test_simple, un_bus_d_evenement
):
    premiere_question = QuestionAEvaluer(
        question="Question ?", reformulation_ideale="Question idéale reformulée ?"
    )
    deuxieme_question = QuestionAEvaluer(
        question="Question 2 ?", reformulation_ideale="Question 2 idéale reformulée ?"
    )
    client_albert = (
        un_client_albert()
        .retourne_la_reformulation_pour_la_question(
            "Question reformulée ?", "Question ?"
        )
        .retourne_la_reformulation_pour_la_question(
            "Question 2 reformulée ?", "Question 2 ?"
        )
        .construis()
    )
    resultat = EvaluateurReformulation(
        client_albert, "Prompt", evaluateur_de_test_simple, un_bus_d_evenement
    ).evalue([premiere_question, deuxieme_question])

    assert len(resultat) == 2
    assert resultat[1].question == "Question 2 ?"
    assert resultat[1].question_reformulee == "Question 2 reformulée ?"
    assert resultat[1].reformulation_ideale == "Question 2 idéale reformulée ?"


def test_appelle_le_client_avec_le_prompt(
    un_client_albert, evaluateur_de_test_simple, un_bus_d_evenement
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
        client_albert, "Un prompt fourni", evaluateur_de_test_simple, un_bus_d_evenement
    ).evalue([question])

    assert client_albert.prompt_fourni == "Un prompt fourni"


def test_ajoute_les_resultats_des_evaluations(
    evaluateur_de_test_avec_metriques, un_client_albert, un_bus_d_evenement
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

    resultat = EvaluateurReformulation(
        client_albert, "Prompt", evaluateur_de_test_avec_metriques, un_bus_d_evenement
    ).evalue([question])

    assert len(resultat[0].resultats) == 1
    assert isinstance(resultat[0].resultats[0], TestResult)


def test_emets_l_evenement_EVALUATION_REFORMULATION_TERMINEE(
    evaluateur_de_test_avec_metriques, un_client_albert, un_bus_d_evenement
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
    bus_evenement = un_bus_d_evenement

    EvaluateurReformulation(
        client_albert, "Prompt", evaluateur_de_test_avec_metriques, bus_evenement
    ).evalue([question])

    assert len(bus_evenement.evenements) == 1
    assert bus_evenement.evenements[0].type == "EVALUATION_REFORMULATION_TERMINEE"
    assert bus_evenement.evenements[0].corps.question == "Question ?"
    assert (
        bus_evenement.evenements[0].corps.reformulation_ideale
        == "Question idéale reformulée ?"
    )
    assert (
        bus_evenement.evenements[0].corps.question_reformulee == "Question reformulée ?"
    )
    assert bus_evenement.evenements[0].corps.resultat[0].__dict__ == {
        "metrique": "MetriqueFideliteMetier",
        "score": 1.0,
    }
    assert bus_evenement.evenements[0].corps.resultat[1].__dict__ == {
        "metrique": "MetriqueSuppressionParasites",
        "score": 0.6,
    }
    assert bus_evenement.evenements[0].corps.resultat[2].__dict__ == {
        "metrique": "MetriqueConservationContraintes",
        "score": 0.6,
    }
    assert bus_evenement.evenements[0].corps.resultat[3].__dict__ == {
        "metrique": "MetriqueAutoportance",
        "score": 0.6,
    }


def test_emets_autant_d_evenements_que_de_reformulations(
    evaluateur_de_test_simple, un_client_albert, un_bus_d_evenement
):
    premiere_question = QuestionAEvaluer(
        question="Question ?", reformulation_ideale="Question idéale reformulée ?"
    )
    deuxieme_question = QuestionAEvaluer(
        question="Question 2 ?", reformulation_ideale="Question 2 idéale reformulée ?"
    )
    client_albert = (
        un_client_albert()
        .retourne_la_reformulation_pour_la_question(
            "Question reformulée ?", "Question ?"
        )
        .retourne_la_reformulation_pour_la_question(
            "Question 2 reformulée ?", "Question 2 ?"
        )
        .construis()
    )

    bus_evenement = un_bus_d_evenement
    EvaluateurReformulation(
        client_albert, "Prompt", evaluateur_de_test_simple, bus_evenement
    ).evalue([premiere_question, deuxieme_question])

    assert len(bus_evenement.evenements) == 2
    assert (
        bus_evenement.evenements[0].corps.id_evaluation
        == bus_evenement.evenements[1].corps.id_evaluation
    )
