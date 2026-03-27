from __future__ import annotations

import argparse

from configuration import recupere_configuration
from jeopardy.client_albert_jeopardy_reel import ClientAlbertJeopardyReel
from jeopardy.collecteur import Document
from jeopardy.questions import EntrepotQuestionGenereeMemoire
from jeopardy.service import ServiceJepoardy


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
    return parser


def main():
    parser = _construis_parser()
    arguments = parser.parse_args()

    document = Document(
        {
            "document_test.txt": {
                "id": "doc-test-1",
                "chunks": [
                    {
                        "id": 1,
                        "contenu": "L’authentification multifacteur réduit le risque de compromission des comptes.",
                        "numero_page": 1,
                    },
                    {
                        "id": 2,
                        "contenu": "Une politique de mots de passe seule ne suffit pas contre le phishing.",
                        "numero_page": 1,
                    },
                    {
                        "id": 3,
                        "contenu": "La sensibilisation des utilisateurs permet de réduire le risque lié aux courriels frauduleux.",
                        "numero_page": 1,
                    },
                    {
                        "id": 4,
                        "contenu": "Le cloisonnement des accès limite les mouvements latéraux d’un attaquant.",
                        "numero_page": 2,
                    },
                    {
                        "id": 5,
                        "contenu": "La journalisation centralisée facilite la détection des activités suspectes.",
                        "numero_page": 2,
                    },
                    {
                        "id": 6,
                        "contenu": "La mise à jour régulière des systèmes corrige des vulnérabilités connues.",
                        "numero_page": 2,
                    },
                    {
                        "id": 7,
                        "contenu": "Les sauvegardes hors ligne réduisent l’impact d’une attaque par rançongiciel.",
                        "numero_page": 3,
                    },
                    {
                        "id": 8,
                        "contenu": "Le principe du moindre privilège consiste à n’accorder que les droits strictement nécessaires.",
                        "numero_page": 3,
                    },
                    {
                        "id": 9,
                        "contenu": "Le filtrage réseau permet de restreindre les flux entre zones de sécurité.",
                        "numero_page": 3,
                    },
                    {
                        "id": 10,
                        "contenu": "Un plan de réponse à incident définit les actions à mener en cas de compromission.",
                        "numero_page": 4,
                    },
                ],
            }
        }
    )
    configuration = recupere_configuration().jeopardy

    client_albert = ClientAlbertJeopardyReel(configuration)
    entrepot_questions = EntrepotQuestionGenereeMemoire()

    ServiceJepoardy(client_albert, entrepot_questions).jeopardyse(arguments.nom_collection, arguments.description_collection, document)
    questions = entrepot_questions.tous()

    print(f"Document traité : {document.nom_document}")
    print(f"Nombre de chunks : {len(document.chunks)}")
    print(f"Nombre de questions générées : {len(questions)}")

    for index, question in enumerate(questions[:20], start=1):
        print(
            f"{index}. [chunk={question.id_chunk} page={question.numero_page}] {question.contenu}"
        )


if __name__ == "__main__":
    main()
