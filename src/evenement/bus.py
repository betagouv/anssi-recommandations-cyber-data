from abc import ABC
from dataclasses import dataclass


@dataclass
class Evenement:
    type: str
    corps: dict


class BusEvenement(ABC):
    def publie(self, evenement: Evenement):
        pass
