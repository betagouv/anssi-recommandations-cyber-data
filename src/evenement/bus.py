from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

T_Evenement = TypeVar("T_Evenement")


@dataclass
class Evenement(ABC, Generic[T_Evenement]):
    type: str
    corps: T_Evenement


class ConsommateurEvenement(ABC):
    def __init__(self, type_evenenemt_consomme: str):
        super().__init__()
        self.type_evenement_consomme = type_evenenemt_consomme

    @abstractmethod
    def consomme(self, evenement: Evenement) -> None:
        pass


class BusEvenement:
    def __init__(self, consommateurs: list[ConsommateurEvenement]):
        super().__init__()
        self._consommateurs = consommateurs

    def publie(self, evenement: Evenement):
        for consommateur in list(
            filter(
                lambda c: c.type_evenement_consomme == evenement.type,
                self._consommateurs,
            )
        ):
            consommateur.consomme(evenement)
