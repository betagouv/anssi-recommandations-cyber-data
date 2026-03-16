import uuid
from dataclasses import dataclass
from itertools import chain

from deepeval.evaluate.types import TestResult
from deepeval.test_case import LLMTestCase

from adaptateurs.clients_albert import ClientAlbertReformulation
from evaluation.evaluateur_deepeval import EvaluateurDeepeval
from evaluation.reformulation.evenements.evenements_publies import (
    EvenementEvaluationReformulationEffectuee,
    CorpsEvenementEvaluationReformulationEffectuee,
    CorpsResultat,
)
from evaluation.reformulation.metriques.metrique_autoportance import (
    MetriqueAutoportance,
)
from evaluation.reformulation.metriques.metrique_conservation_contraintes import (
    MetriqueConservationContraintes,
)
from evaluation.reformulation.metriques.metrique_fidelite_metier import (
    MetriqueFideliteMetier,
)
from evaluation.reformulation.metriques.metrique_suppression_parasites import (
    MetriqueSuppressionParasites,
)
from evenement.bus import BusEvenement


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
        bus_evenement: BusEvenement,
    ):
        super().__init__()
        self._prompt = prompt
        self._client_albert = client_albert
        self._evaluateur = evaluateur
        self._bus_evenement = bus_evenement

    def evalue(self, questions: list[QuestionAEvaluer]) -> list[ResultatEvaluation]:
        resultats = [
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
        id_evalualtion = uuid.uuid4()
        for resultat in resultats:
            self._bus_evenement.publie(
                EvenementEvaluationReformulationEffectuee(
                    corps=CorpsEvenementEvaluationReformulationEffectuee(
                        id_evaluation=id_evalualtion,
                        question=resultat.question,
                        reformulation_ideale=resultat.reformulation_ideale,
                        question_reformulee=resultat.question_reformulee,
                        resultat=[
                            CorpsResultat(res)
                            for res in resultat.resultats[0].metrics_data
                        ]
                        if resultat.resultats[0].metrics_data is not None
                        else [],
                    ),
                )
            )
        return resultats

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
            metrics=[
                MetriqueSuppressionParasites(),
                MetriqueConservationContraintes(),
                MetriqueAutoportance(),
                MetriqueFideliteMetier(),
            ],
        )
        return list(
            chain.from_iterable(
                map(lambda resultats: resultats.test_results, resultats_evaluation)
            )
        )
