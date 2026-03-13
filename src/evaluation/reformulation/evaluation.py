from dataclasses import dataclass

from deepeval.test_case import LLMTestCase

from adaptateurs.clients_albert import ClientAlbertReformulation
from evaluation.deepeval.lanceur_deepeval import EvaluateurDeepeval
from evaluation.reformulation.metriques.metrique_suppression_parasites import (
    MetriqueSuppressionParasites,
)


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
    def __init__(
        self,
        client_albert: ClientAlbertReformulation,
        prompt: str,
        evaluateur: EvaluateurDeepeval,
    ):
        super().__init__()
        self._prompt = prompt
        self._client_albert = client_albert
        self._evaluateur = evaluateur

    def evalue(self, questions: list[QuestionAEvaluer]) -> list[ResultatEvaluation]:
        self._evaluateur.evaluate(
            test_cases=[
                LLMTestCase(input="Question test", actual_output="Question reformulée")
            ],
            metrics=[MetriqueSuppressionParasites()],
        )
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
