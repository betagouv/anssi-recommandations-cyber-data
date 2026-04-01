from adaptateurs.journal import fabrique_adaptateur_journal
from evaluation.reformulation.evenements.journal import (
    ConsommateurJournalisationReformulationEffectuee,
)
from evenement.bus import BusEvenement, ConsommateurEvenement
from jeopardy.consommateurs_jeopardy import consommateurs_jeopardy


def fabrique_bus_evenements() -> BusEvenement:
    consommateurs: list[ConsommateurEvenement] = [
        ConsommateurJournalisationReformulationEffectuee(fabrique_adaptateur_journal()),
    ]
    consommateurs.extend(consommateurs_jeopardy())
    return BusEvenement(consommateurs)
