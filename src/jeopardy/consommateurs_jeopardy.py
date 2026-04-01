import logging
from typing import cast

from evenement.bus import ConsommateurEvenement, Evenement
from jeopardy.evenements import (
    CorpsEvenementQuestionsGenerees,
    CorpsEvenementQuestionsGenereesEnErreur,
    EvenementQuestionsGenereesEnErreur,
)


class ConsommateurQuestionGeneree(ConsommateurEvenement):
    def __init__(self):
        super().__init__("QUESTIONS_GENEREES")

    def consomme(self, evenement: Evenement[CorpsEvenementQuestionsGenerees]) -> None:
        logging.info(f"Événement : {evenement.type} - {evenement.corps}")


class ConsommateurQuestionGenereeEnErreur(ConsommateurEvenement):
    def __init__(self):
        super().__init__("QUESTIONS_GENEREES_EN_ERREUR")

    def consomme(
        self, evenement: Evenement[CorpsEvenementQuestionsGenereesEnErreur]
    ) -> None:
        evenement_en_erreur = cast(EvenementQuestionsGenereesEnErreur, evenement)
        logging.info(
            f"Événement : {evenement_en_erreur.type} - {evenement_en_erreur.corps}"
        )


def consommateurs_jeopardy() -> list[ConsommateurEvenement]:
    return [
        ConsommateurQuestionGeneree(),
        ConsommateurQuestionGenereeEnErreur(),
    ]
