import logging
from typing import cast

from evenement.bus import ConsommateurEvenement, Evenement
from jeopardy.evenements import (
    CorpsEvenementQuestionsGenerees,
    CorpsEvenementQuestionsGenereesEnErreur,
    EvenementQuestionsGenereesEnErreur,
    CorpsEvenementJeopardyGenereEnErreur,
    CorpsEvenementJeopardyChunkAjouteEnErreur,
)


class ConsommateurQuestionGeneree(ConsommateurEvenement):
    def __init__(self):
        super().__init__("QUESTIONS_GENEREES")

    def consomme(self, evenement: Evenement[CorpsEvenementQuestionsGenerees]) -> None:
        logging.info(
            f"{len(evenement.corps.questions_generees)} questions générées "
            f"depuis : {evenement.corps.id_document_origine} "
            f"contenant {evenement.corps.nombre_chunks_origine} chunks  "
            f"dans la collection {evenement.corps.id_collection_jeopardy} "
            f"sur le document {evenement.corps.id_document_jeopardy}"
        )


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


class ConsommateurJeopardyEnErreurGenere(ConsommateurEvenement):
    def __init__(self):
        super().__init__("JEOPARDY_GENERE_EN_ERREUR")

    def consomme(
        self, evenement: Evenement[CorpsEvenementJeopardyGenereEnErreur]
    ) -> None:
        logging.info(f"Événement : {evenement.type} - {evenement.corps}")


class ConsommateurJeopardyChunkAjouteEnErreur(ConsommateurEvenement):
    def __init__(self):
        super().__init__("JEOPARDY_CHUNK_AJOUTE_EN_ERREUR")

    def consomme(
        self, evenement: Evenement[CorpsEvenementJeopardyChunkAjouteEnErreur]
    ) -> None:
        logging.info(f"Événement : {evenement.type} - {evenement.corps}")


def consommateurs_jeopardy() -> list[ConsommateurEvenement]:
    return [
        ConsommateurQuestionGeneree(),
        ConsommateurQuestionGenereeEnErreur(),
        ConsommateurJeopardyEnErreurGenere(),
        ConsommateurJeopardyChunkAjouteEnErreur(),
    ]
