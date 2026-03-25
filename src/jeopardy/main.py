from __future__ import annotations

import argparse

from configuration import recupere_configuration
from documents.docling.multi_processeur import Multiprocesseur
from jeopardy.client_albert_jeopardy_reel import ClientAlbertJeopardyReel
from jeopardy.collecteur import CollecteurDeQuestions, Document
from jeopardy.questions import EntrepotQuestionGenereeMemoire

PROMPT_SYSTEME_GENERATION_QUESTIONS_FR = """
Tu es un composant de génération de questions de type Jeopardy pour un système RAG en cybersécurité (ANSSI).

Mission :
À partir d’un paragraphe, générer un nombre DYNAMIQUE de questions de type Jeopardy réalistes permettant de retrouver ce paragraphe via recherche sémantique.
Le nombre de questions ne doit pas être fixé à l’avance : il doit être proportionnel au nombre de thématiques, de mécanismes, de recommandations, de risques, de limites et d’éléments distincts réellement présents dans le paragraphe.

Règles de sortie (obligatoires) :
- Retourner UNIQUEMENT un JSON STRICT sur UNE seule ligne, sans texte avant/après, sans Markdown, sans ```fences```.
- Une seule clé autorisée : "questions".
- Format exact : {"questions":["...","..."]}

Règle de cardinalité dynamique :
- Générer suffisamment de questions pour couvrir les thématiques réellement présentes dans le paragraphe, sans sous-générer ni sur-générer.
- Plus le paragraphe couvre d’idées distinctes, de notions techniques, de mécanismes, de recommandations ANSSI, de risques, de limites ou de relations de cause à effet, plus le nombre de questions doit augmenter.
- À l’inverse, si le paragraphe est simple, focalisé et mono-thématique, produire peu de questions.
- Ne jamais ajouter de questions artificielles uniquement pour augmenter le volume.
- Ne générer qu’une question lorsqu’un élément est mineur, redondant ou insuffisamment informatif.
- Générer plusieurs questions distinctes lorsqu’un même paragraphe contient plusieurs axes réellement indépendants et utiles pour la recherche sémantique.
- La liste finale doit être dimensionnée pour maximiser la couverture informationnelle utile, avec le minimum de redondance.

Définition du format Jeopardy :
- Chaque élément de "questions" doit être formulé comme un indice de type Jeopardy, c’est-à-dire une question dont la réponse attendue est un concept, un mécanisme, une recommandation, une menace, une pratique ou une entité explicitement présente dans le paragraphe.
- La formulation doit rester naturelle pour un usage de recherche sémantique.
- Chaque question doit se terminer par "?".
- Les questions doivent être autoportantes et compréhensibles sans contexte externe.

Contraintes de contenu :
1) Langue : français.
2) Chaque élément de "questions" est une UNIQUE phrase interrogative et se termine par "?".
3) Répondabilité : chaque question doit être répondable uniquement à partir du paragraphe.
4) Autoportance : aucune question ne doit dépendre d’un contexte externe.
5) Un seul axe par question.
6) Non-duplication : pas de doublons.

Optimisation retrieval :
11) Les questions doivent être concises, précises et riches en signal lexical.
12) Conserver les termes techniques du paragraphe.
13) Ne conserver que les éléments discriminants utiles à la recherche.

Mise en avant des recommandations ANSSI :
16) Si le paragraphe contient une mention de recommandation "R" suivie d’un ou plusieurs chiffres :
- Générer au moins UNE question dédiée par recommandation détectée.
- La question doit citer explicitement la recommandation.

Nettoyage obligatoire :
17) Interdire et supprimer dans les questions :
- toute référence bibliographique ou note ;
- tout astérisque ;
- "cf.", "voir", "référence", "guide", "article", ou toute mention de source externe.
""".strip()


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

    collecteur = CollecteurDeQuestions(
        client_albert=client_albert,
        prompt=PROMPT_SYSTEME_GENERATION_QUESTIONS_FR,
        entrepot_questions_generees=entrepot_questions,
        multi_processeur=Multiprocesseur(),
    )

    collecteur.collecte(
        nom_collection=arguments.nom_collection,
        description_collection=arguments.description_collection,
        document=document,
    )

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
