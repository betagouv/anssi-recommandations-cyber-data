from dataclasses import dataclass

from evenement.bus import Evenement
from jeopardy.questions import QuestionGeneree


@dataclass
class CorpsEvenementQuestionsGenerees:
    questions_generees: list[QuestionGeneree]
    id_collection_jeopardy: str
    id_document_origine: str
    id_document_jeopardy: str
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


@dataclass
class CorpsEvenementJeopardyGenereEnErreur:
    erreur: str


class EvenementJeopardyGenereEnErreur(Evenement):
    def __init__(self, corps: CorpsEvenementJeopardyGenereEnErreur):
        super().__init__(type="JEOPARDY_GENERE_EN_ERREUR", corps=corps)


@dataclass
class CorpsEvenementJeopardyChunkAjouteEnErreur:
    erreur: str


class EvenementJeopardyChunkAjouteEnErreur(Evenement):
    def __init__(self, corps: CorpsEvenementJeopardyChunkAjouteEnErreur):
        super().__init__(type="JEOPARDY_CHUNK_AJOUTE_EN_ERREUR", corps=corps)
