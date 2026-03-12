from evaluation.reformulation.evaluation import (
    QuestionAEvaluer,
    EvaluateurReformulation,
)


def test_reformule_la_question(un_client_albert):
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
    resultat = EvaluateurReformulation(client_albert).evalue([question])

    assert len(resultat) == 1
    assert resultat[0].question == "Question ?"
    assert resultat[0].question_reformulee == "Question reformulée ?"
    assert resultat[0].reformulation_ideale == "Question idéale reformulée ?"
