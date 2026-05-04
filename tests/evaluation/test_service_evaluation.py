from pathlib import Path

import pytest

from adaptateurs.journal import TypeEvenement, AdaptateurJournalMemoire
from evaluation.evaluation_en_cours import (
    EntrepotEvaluationEnCoursMemoire,
    StatutEvaluationEnCours,
)
from evaluation.mqc.lanceur_deepeval import LanceurEvaluationDeepeval
from evaluation.reformulation.evaluation import QuestionAEvaluer
from evaluation.service_evaluation import ServiceEvaluation
from journalisation.evaluation import EntrepotEvaluationMemoire


def test_lance_une_reformulation(
    un_client_albert_de_reformulation,
    evaluateur_de_test_avec_metriques,
    un_bus_d_evenement,
    un_lanceur_deepeval,
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
        entrepot_evaluation_en_cours,
        un_lanceur_deepeval,
        AdaptateurJournalMemoire(),
        EntrepotEvaluationMemoire(),
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


@pytest.mark.asyncio
async def test_lance_une_evaluation(
    un_collecteur_de_reponse,
    evaluateur_de_test_simple,
    cree_fichier_csv_avec_du_contenu,
    tmp_path,
):
    entrepot_evaluation_en_cours = EntrepotEvaluationEnCoursMemoire()
    entrepot_evaluation = EntrepotEvaluationMemoire()
    lanceur_evaluation = LanceurEvaluationDeepeval(
        entrepot_evaluation, evaluateur_de_test_simple
    )
    fichier_evaluation = cree_fichier_csv_avec_du_contenu(
        "Question type\nA?\n", tmp_path
    )

    evaluation = await ServiceEvaluation(
        entrepot_evaluation_en_cours,
        lanceur_evaluation,
        AdaptateurJournalMemoire(),
        entrepot_evaluation,
    ).lance_evaluation(
        fichier_evaluation,
        Path("donnees/jointure-nom-guide.csv"),
        un_collecteur_de_reponse,
    )

    assert isinstance(evaluation, str) is True


@pytest.mark.asyncio
async def test_lance_une_evaluation_consigne_le_resultat(
    un_collecteur_de_reponse,
    evaluateur_de_test_simple,
    cree_fichier_csv_avec_du_contenu,
    tmp_path,
):
    adaptateur_journal: AdaptateurJournalMemoire = AdaptateurJournalMemoire()
    entrepot_evaluation_en_cours = EntrepotEvaluationEnCoursMemoire()
    entrepot_evaluation = EntrepotEvaluationMemoire()
    lanceur_evaluation = LanceurEvaluationDeepeval(
        entrepot_evaluation, evaluateur_de_test_simple
    )
    fichier_evaluation = cree_fichier_csv_avec_du_contenu(
        "Question type\nA?\n", tmp_path
    )

    await ServiceEvaluation(
        entrepot_evaluation_en_cours,
        lanceur_evaluation,
        adaptateur_journal,
        entrepot_evaluation,
    ).lance_evaluation(
        fichier_evaluation,
        Path("donnees/jointure-nom-guide.csv"),
        un_collecteur_de_reponse,
    )

    assert (
        adaptateur_journal.les_evenements()[0]["type"]
        == TypeEvenement.EVALUATION_CALCULEE
    )
    donnees_recues = adaptateur_journal.les_evenements()[0]["donnees"]
    assert donnees_recues["id_experimentation"] is not None
    assert donnees_recues["une_metrique"] == 1.0
