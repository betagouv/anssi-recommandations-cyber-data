from abc import ABC, abstractmethod
from enum import StrEnum
from pydantic import BaseModel


class Donnees(BaseModel):
    pass


class TypeEvenement(StrEnum):
    EVALUATION_CALCULEE = "EVALUATION_CALCULEE"


class AdaptateurJournal(ABC):
    @abstractmethod
    def consigne_evenement(self, type: TypeEvenement, donnees: Donnees) -> None:
        pass
