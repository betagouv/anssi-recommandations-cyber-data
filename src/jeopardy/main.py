from __future__ import annotations

import argparse

from configuration import recupere_configuration
from jeopardy.client_albert_jeopardy_reel import ClientAlbertJeopardyReel
from jeopardy.questions import EntrepotQuestionGenereeMemoire
from jeopardy.service import ServiceJeopardy


def _construis_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m jeopardy.main",
        description="Génère des questions Jeopardy à partir d'un document chunké.",
    )
    parser.add_argument(
        "--nom-collection",
        required=True,
        help="Nom de la collection source.",
    )
    parser.add_argument(
        "--description-collection",
        required=True,
        help="Description de la collection source.",
    )
    parser.add_argument(
        "--id-collection",
        required=True,
        help="Identifiant de la collection Albert source.",
    )
    return parser


def main():
    parser = _construis_parser()
    arguments = parser.parse_args()

    configuration = recupere_configuration().jeopardy

    client_albert = ClientAlbertJeopardyReel(configuration)
    entrepot_questions = EntrepotQuestionGenereeMemoire()

    ServiceJeopardy(client_albert, entrepot_questions).jeopardyse(
        arguments.nom_collection,
        arguments.description_collection,
        arguments.id_collection,
    )
    questions = entrepot_questions.tous()

    for index, question in enumerate(questions[:20], start=1):
        print(
            f"{index}. [chunk={question.id_chunk} page={question.page}] {question.contenu}"
        )


if __name__ == "__main__":
    main()
