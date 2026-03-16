from evenement.bus import Evenement, BusEvenement, ConsommateurEvenement


class ConsommateurDeTest(ConsommateurEvenement):
    def __init__(self):
        super().__init__("TEST_PUBLIE")
        self.a_consomme = False
        self.evenement = None

    def consomme(self, evenement: Evenement):
        self.a_consomme = True
        self.evenement = evenement


def test_consomme_un_evenement_publie():
    consommateur = ConsommateurDeTest()
    bus_evenement = BusEvenement([consommateur])

    bus_evenement.publie(Evenement(type="TEST_PUBLIE", corps={"nom": "test"}))

    assert consommateur.a_consomme
    assert consommateur.evenement.type == "TEST_PUBLIE"
    assert consommateur.evenement.corps == {"nom": "test"}


def test_ne_consomme_pas_un_evenement_qui_ne_l_interesse_pas():
    consommateur = ConsommateurDeTest()
    bus_evenement = BusEvenement([consommateur])

    bus_evenement.publie(Evenement(type="EVENEMENT_PUBLIE", corps={"nom": "test"}))

    assert not consommateur.a_consomme
    assert consommateur.evenement is None
