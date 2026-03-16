from adaptateurs.journal import AdaptateurJournal, TypeEvenement, Donnees
from evaluation.reformulation.evenements.evenements_publies import (
    CorpsEvenementEvaluationReformulationEffectuee,
)
from evenement.bus import ConsommateurEvenement, Evenement


class ConsommateurJournalisationReformulationEffectuee(ConsommateurEvenement):
    def __init__(self, adaptateur_journal: AdaptateurJournal):
        super().__init__("EVALUATION_REFORMULATION_TERMINEE")
        self._adaptateur_journal = adaptateur_journal

    def consomme(
        self, evenement: Evenement[CorpsEvenementEvaluationReformulationEffectuee]
    ) -> None:
        donnees_evaluation = Donnees.model_validate(
            {
                "id_evaluation": evenement.corps.id_evaluation,
                "question": evenement.corps.question,
                "reformulation_ideale": evenement.corps.reformulation_ideale,
                "question_reformulee": evenement.corps.question_reformulee,
                "resultat": evenement.corps.resultat,
            }
        )
        self._adaptateur_journal.enregistre(
            TypeEvenement.EVALUATION_REFORMULATION_TERMINEE, donnees_evaluation
        )
