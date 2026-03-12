from abc import ABC, abstractmethod
from pathlib import Path


class LanceurEvaluation(ABC):
    @abstractmethod
    def lance_l_evaluation(self, fichier_csv: Path) -> int | str | None:
        pass


class LanceurEvaluationMemoire(LanceurEvaluation):
    def lance_l_evaluation(self, fichier_csv: Path | None) -> int | None:
        return 1
