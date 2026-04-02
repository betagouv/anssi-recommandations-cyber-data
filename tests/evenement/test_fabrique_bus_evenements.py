from evaluation.reformulation.evenements.journal import (
    ConsommateurJournalisationReformulationEffectuee,
)
from evenement.fabrique_bus_evenements import fabrique_bus_evenements


def test_initie_les_consommateurs():
    bus_evenement = fabrique_bus_evenements()

    assert len(bus_evenement._consommateurs) == 5
    assert isinstance(
        bus_evenement._consommateurs[0],
        ConsommateurJournalisationReformulationEffectuee,
    )
