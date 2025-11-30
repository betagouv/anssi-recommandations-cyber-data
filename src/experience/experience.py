import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from configuration import Configuration
from evalap import EvalapClient
from evalap.lance_experience import lance_experience


class LanceurExperience(ABC):
    @abstractmethod
    def lance_l_experience(self, fichier_csv: Path) -> int | str | None:
        pass


class LanceurExperienceEvalap(LanceurExperience):
    def __init__(self, le_client: EvalapClient, configuration: Configuration):
        super().__init__()
        self.client = le_client
        self.configuration = configuration

    def lance_l_experience(self, fichier_csv: Path | None) -> int | None:
        return lance_experience(
            self.client, self.configuration, 10_000, str(uuid.uuid4()), fichier_csv
        )


class LanceurExperienceMemoire(LanceurExperience):
    def lance_l_experience(self, fichier_csv: Path | None) -> int | None:
        return 1
