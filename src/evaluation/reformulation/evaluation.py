from dataclasses import dataclass

from adaptateurs.clients_albert import ClientAlbertReformulation


@dataclass
class ResultatEvaluation:
    question: str
    reformulation_ideale: str
    question_reformulee: str


@dataclass
class QuestionAEvaluer:
    question: str
    reformulation_ideale: str


class EvaluateurReformulation:
    def __init__(self, client_albert: ClientAlbertReformulation, prompt: str):
        super().__init__()
        self._prompt = prompt
        self._client_albert = client_albert

    def evalue(self, questions: list[QuestionAEvaluer]) -> list[ResultatEvaluation]:
        return [
            ResultatEvaluation(
                question=question.question,
                reformulation_ideale=question.reformulation_ideale,
                question_reformulee=self._client_albert.reformule_la_question(
                    self._prompt, question.question
                ),
            )
            for question in questions
        ]
