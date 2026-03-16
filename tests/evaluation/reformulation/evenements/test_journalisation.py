import uuid

from adaptateurs.journal import AdaptateurJournalMemoire
from evaluation.reformulation.evenements.evenements_publies import (
    EvenementEvaluationReformulationEffectuee,
    CorpsEvenementEvaluationReformulationEffectuee,
)
from evaluation.reformulation.evenements.journal import (
    ConsommateurJournalisationReformulationEffectuee,
)


def test_journalise_un_evenement():
    adaptateur_journal = AdaptateurJournalMemoire()

    consommateur = ConsommateurJournalisationReformulationEffectuee(adaptateur_journal)
    consommateur.consomme(
        EvenementEvaluationReformulationEffectuee(
            corps=CorpsEvenementEvaluationReformulationEffectuee(
                question="Q ?",
                reformulation_ideale="R ?",
                question_reformulee="Q' ?",
                resultat=[],
                id_evaluation=uuid.uuid4(),
            )
        )
    )

    les_evenements = adaptateur_journal.les_evenements()
    assert len(les_evenements) == 1
    assert les_evenements[0]["type"] == "EVALUATION_REFORMULATION_TERMINEE"
    assert les_evenements[0]["donnees"]["id_evaluation"] is not None
    assert les_evenements[0]["donnees"]["question"] == "Q ?"
    assert les_evenements[0]["donnees"]["reformulation_ideale"] == "R ?"
    assert les_evenements[0]["donnees"]["question_reformulee"] == "Q' ?"
    assert les_evenements[0]["donnees"]["resultat"] == []
