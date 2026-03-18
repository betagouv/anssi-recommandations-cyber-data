from abc import ABC, abstractmethod
from enum import StrEnum
from uuid import UUID


class StatutEvaluationEnCours(StrEnum):
    EN_COURS = "EN_COURS"


class EvaluationEnCours:
    def __init__(self, id: UUID, nombre_questions: int):
        super().__init__()
        self._id = id
        self._nombre_questions = nombre_questions
        self._statut = StatutEvaluationEnCours.EN_COURS

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def nombre_questions(self) -> int:
        return self._nombre_questions

    @property
    def statut(self) -> StatutEvaluationEnCours:
        return self._statut


class EntrepotEvaluationEnCours(ABC):
    @abstractmethod
    def lit(self, id_evaluation: int | str) -> EvaluationEnCours:
        pass

    @abstractmethod
    def persiste(self, evaluation: EvaluationEnCours) -> None:
        pass


class EntrepotEvaluationEnCoursMemoire(EntrepotEvaluationEnCours):
    def __init__(self):
        super().__init__()
        self.evaluations = []

    def lit(self, id_evaluation: int | str) -> EvaluationEnCours:
        return list(
            filter(lambda evaluation: evaluation.id == id_evaluation, self.evaluations)
        )[0]

    def persiste(self, evaluation: EvaluationEnCours) -> None:
        self.evaluations.append(evaluation)
