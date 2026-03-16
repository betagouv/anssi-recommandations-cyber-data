from dataclasses import dataclass
from uuid import UUID

from deepeval.tracing.api import MetricData

from evenement.bus import Evenement


@dataclass
class CorpsResultat:
    metrique: str
    score: float

    def __init__(self, resultat: MetricData):
        super().__init__()
        self.metrique = resultat.name
        self.score = resultat.score if resultat.score is not None else 0.0


@dataclass
class CorpsEvenementEvaluationReformulationEffectuee:
    id_evaluation: UUID
    question: str
    reformulation_ideale: str
    question_reformulee: str
    resultat: list[CorpsResultat]


class EvenementEvaluationReformulationEffectuee(Evenement):
    def __init__(self, corps: CorpsEvenementEvaluationReformulationEffectuee):
        super().__init__(type="EVALUATION_REFORMULATION_TERMINEE", corps=corps)
