from adaptateurs.journal import fabrique_adaptateur_journal
from evaluation.reformulation.evenements.journal import (
    ConsommateurJournalisationReformulationEffectuee,
)
from evenement.bus import BusEvenement


def fabrique_bus_evenements() -> BusEvenement:
    return BusEvenement(
        [
            ConsommateurJournalisationReformulationEffectuee(
                fabrique_adaptateur_journal()
            )
        ]
    )
