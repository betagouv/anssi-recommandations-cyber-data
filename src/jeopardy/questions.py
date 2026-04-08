from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class QuestionGeneree:
    contenu: str
    contenu_origine: str
    id_document: str
    id_chunk: int
    page: int


class GenerationQuestionEnErreur:
    pass


class EntrepotQuestionGeneree(ABC):
    @abstractmethod
    def persiste(self, question_generee: QuestionGeneree):
        pass

    @abstractmethod
    def tous(self) -> list[QuestionGeneree]:
        pass

    @abstractmethod
    def par_id_document(self, id_document) -> list[QuestionGeneree]:
        pass


class EntrepotQuestionGenereeMemoire(EntrepotQuestionGeneree):
    def __init__(self):
        super().__init__()
        self.questions_generees: dict[str, list[QuestionGeneree]] = {}

    def persiste(self, question_generee: QuestionGeneree):
        self.questions_generees.setdefault(question_generee.id_document, []).append(
            question_generee
        )

    def tous(self) -> list[QuestionGeneree]:
        return [
            question
            for questions in self.questions_generees.values()
            for question in questions
        ]

    def par_id_document(self, id_document) -> list[QuestionGeneree]:
        return self.questions_generees.get(id_document, [])
