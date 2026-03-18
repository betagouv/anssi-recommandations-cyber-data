from evaluation.evaluation_en_cours import (
    EntrepotEvaluationEnCoursMemoire,
    StatutEvaluationEnCours,
)
from evaluation.reformulation.evaluation import QuestionAEvaluer
from evaluation.service_evaluation import ServiceEvaluation


def test_lance_une_reformulation(
    un_client_albert_de_reformulation,
    evaluateur_de_test_avec_metriques,
    un_bus_d_evenement,
):
    entrepot_evaluation_en_cours = EntrepotEvaluationEnCoursMemoire()
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

    evaluation_en_cours = ServiceEvaluation(
        entrepot_evaluation_en_cours
    ).lance_reformulation(
        client_albert,
        un_bus_d_evenement,
        "Prompt",
        [question],
        evaluateur_de_test_avec_metriques,
    )

    assert len(entrepot_evaluation_en_cours.evaluations) == 1
    assert (
        entrepot_evaluation_en_cours.lit(evaluation_en_cours.id) == evaluation_en_cours
    )
    assert evaluation_en_cours.id is not None
    assert evaluation_en_cours.nombre_questions == 1
    assert evaluation_en_cours.statut == StatutEvaluationEnCours.EN_COURS
