from abc import ABC, abstractmethod
from enum import StrEnum
from pydantic import BaseModel, ConfigDict


class Donnees(BaseModel):
    model_config = ConfigDict(extra="allow")


class TypeEvenement(StrEnum):
    EVALUATION_CALCULEE = "EVALUATION_CALCULEE"


class AdaptateurJournal(ABC):
    @abstractmethod
    def consigne_evenement(self, type: TypeEvenement, donnees: Donnees) -> None:
        pass


class AdaptateurJournalMemoire(AdaptateurJournal):
    def consigne_evenement(self, type: TypeEvenement, donnees: Donnees) -> None:
        self._evenements.append({"type": type, "donnees": donnees.model_dump()})

    def __init__(self):
        self._evenements = []

    def enregistrer(self, evenement):
        self._evenements.append(evenement)

    def les_evenements(self):
        return self._evenements
