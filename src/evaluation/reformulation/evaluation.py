from dataclasses import dataclass
from itertools import chain

from deepeval.evaluate.types import TestResult
from deepeval.test_case import LLMTestCase

from adaptateurs.clients_albert import ClientAlbertReformulation
from evaluation.deepeval_adaptateur.lanceur_deepeval import EvaluateurDeepeval
from evaluation.reformulation.metriques.metrique_suppression_parasites import (
    MetriqueSuppressionParasites,
)


@dataclass
class ResultatEvaluation:
    question: str
    reformulation_ideale: str
    question_reformulee: str
    resultats: list[TestResult]


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
        return [
            ResultatEvaluation(
                question=question.question,
                reformulation_ideale=question.reformulation_ideale,
                question_reformulee=self._client_albert.reformule_la_question(
                    self._prompt, question.question
                ),
                resultats=self._execute_les_cas_de_test(question),
            )
            for question in questions
        ]

    def _execute_les_cas_de_test(self, question: QuestionAEvaluer) -> list[TestResult]:
        resultats_evaluation = self._evaluateur.evaluate(
            test_cases=[
                LLMTestCase(
                    input=question.question,
                    actual_output=self._client_albert.reformule_la_question(
                        self._prompt, question.question
                    ),
                    expected_output=question.reformulation_ideale,
                )
            ],
            metrics=[MetriqueSuppressionParasites()],
        )
        return list(
            chain.from_iterable(
                map(lambda resultats: resultats.test_results, resultats_evaluation)
            )
        )
