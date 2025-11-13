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
