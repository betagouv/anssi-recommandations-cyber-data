from evenement.bus import BusEvenement


class BusEvenementMemoire(BusEvenement):
    def __init__(self):
        super().__init__()
        self._evenements = []

    def publie(self, evenement):
        self._evenements.append(evenement)
        super().publie(evenement)
