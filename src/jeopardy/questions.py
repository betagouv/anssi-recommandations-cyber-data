from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class QuestionGeneree:
    contenu: str
    contenu_origine: str
    id_document: str
    id_chunk: str
    numero_page: int


class EntrepotQuestionGeneree(ABC):
    @abstractmethod
    def persiste(self, question_generee: QuestionGeneree):
        pass

    @abstractmethod
    def tous(self) -> list[QuestionGeneree]:
        pass


class EntrepotQuestionGenereeMemoire(EntrepotQuestionGeneree):
    def __init__(self):
        super().__init__()
        self.questions_generees = []

    def persiste(self, question_generee: QuestionGeneree):
        self.questions_generees.append(question_generee)

    def tous(self) -> list[QuestionGeneree]:
        return self.questions_generees
