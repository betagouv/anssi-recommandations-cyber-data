from dataclasses import dataclass

from evenement.bus import Evenement
from jeopardy.questions import QuestionGeneree


@dataclass
class CorpsEvenementQuestionsGenerees:
    questions_generees: list[QuestionGeneree]
    id_document: str
    nombre_chunks_origine: int


class EvenementQuestionsGenerees(Evenement):
    def __init__(self, corps: CorpsEvenementQuestionsGenerees):
        super().__init__(type="QUESTIONS_GENEREES", corps=corps)


@dataclass
class CorpsEvenementQuestionsGenereesEnErreur:
    id_document: str
    erreur: str


class EvenementQuestionsGenereesEnErreur(Evenement):
    def __init__(self, corps: CorpsEvenementQuestionsGenereesEnErreur):
        super().__init__(type="QUESTIONS_GENEREES_EN_ERREUR", corps=corps)
