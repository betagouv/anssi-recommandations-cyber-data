import logging
from typing import cast

from evenement.bus import ConsommateurEvenement, Evenement
from jeopardy.evenements import (
    CorpsEvenementQuestionsGenerees,
    CorpsEvenementQuestionsGenereesEnErreur,
    EvenementQuestionsGenereesEnErreur,
    CorpsEvenementJeopardyGenereEnErreur,
    CorpsEvenementJeopardyChunkAjouteEnErreur,
    CorpsEvenementJeopardyChunksAjoutes,
)

logger = logging.getLogger(__name__)


class ConsommateurQuestionGeneree(ConsommateurEvenement):
    def __init__(self):
        super().__init__("QUESTIONS_GENEREES")

    def consomme(self, evenement: Evenement[CorpsEvenementQuestionsGenerees]) -> None:
        logger.info(
            f"{len(evenement.corps.questions_generees)} questions générées "
            f"en {evenement.corps.temps_traitement} secondes "
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
        logger.error(
            f"Événement : {evenement_en_erreur.type} - {evenement_en_erreur.corps}"
        )


class ConsommateurJeopardyEnErreurGenere(ConsommateurEvenement):
    def __init__(self):
        super().__init__("JEOPARDY_GENERE_EN_ERREUR")

    def consomme(
        self, evenement: Evenement[CorpsEvenementJeopardyGenereEnErreur]
    ) -> None:
        logger.error(f"Événement : {evenement.type} - {evenement.corps}")


class ConsommateurJeopardyChunkAjouteEnErreur(ConsommateurEvenement):
    def __init__(self):
        super().__init__("JEOPARDY_CHUNK_AJOUTE_EN_ERREUR")

    def consomme(
        self, evenement: Evenement[CorpsEvenementJeopardyChunkAjouteEnErreur]
    ) -> None:
        logger.error(f"Événement : {evenement.type} - {evenement.corps}")


class ConsommateurJeopardyChunksAjoutes(ConsommateurEvenement):
    def __init__(self):
        super().__init__("JEOPARDY_CHUNKS_AJOUTES")

    def consomme(
        self, evenement: Evenement[CorpsEvenementJeopardyChunksAjoutes]
    ) -> None:
        logger.info(
            f"{len(evenement.corps.chunks)} chunks ajoutés "
            f"en  {evenement.corps.temps} secondes"
        )


def consommateurs_jeopardy() -> list[ConsommateurEvenement]:
    return [
        ConsommateurQuestionGeneree(),
        ConsommateurQuestionGenereeEnErreur(),
        ConsommateurJeopardyEnErreurGenere(),
        ConsommateurJeopardyChunkAjouteEnErreur(),
        ConsommateurJeopardyChunksAjoutes(),
    ]
