from abc import ABC, abstractmethod
from pathlib import Path


class LanceurExperience(ABC):
    @abstractmethod
    def lance_l_experience(self, fichier_csv: Path) -> int | str | None:
        pass


class LanceurExperienceMemoire(LanceurExperience):
    def lance_l_experience(self, fichier_csv: Path | None) -> int | None:
        return 1
