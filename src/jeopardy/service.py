from __future__ import annotations

from documents.docling.multi_processeur import Multiprocesseur
from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    RequeteCreationDocumentAlbert,
    RequeteAjoutChunksDansDocumentAlbert,
)
from jeopardy.collecteur import Document, CollecteurDeQuestions
from jeopardy.prompt_generation_question import PROMPT_SYSTEME_GENERATION_QUESTIONS_FR
from jeopardy.questions import EntrepotQuestionGeneree, QuestionGeneree
from itertools import islice
from typing import Generator


class ServiceJepoardy:
    def __init__(
        self,
        client_albert: ClientAlbertJeopardy,
        entrepot_questions: EntrepotQuestionGeneree,
        prompt: str = PROMPT_SYSTEME_GENERATION_QUESTIONS_FR,
        multi_processeur: Multiprocesseur = Multiprocesseur(),
    ):
        super().__init__()
        self._entrepot_questions = entrepot_questions
        self._client_albert = client_albert
        self._prompt = prompt
        self._multi_processeur = multi_processeur

    def jeopardyse(
        self, nom_collection: str, description_collection: str, document: Document
    ):
        # PARTIE 2
        # plutôt que passer le document, donner l’ID du document Albert pour qu’il aille le chercher
        # le mapper en document
        reponse_creation_collection = self._client_albert.cree_collection(
            f"Jeopardy : {nom_collection}", f"Jeopardy : {description_collection}"
        )
        print(f"ID de la collection créée : {reponse_creation_collection.id}")
        self._client_albert.ajoute_document(
            reponse_creation_collection.id, _en_document_albert(document)
        )
        collecteur = CollecteurDeQuestions(
            client_albert=self._client_albert,
            prompt=self._prompt,
            entrepot_questions_generees=self._entrepot_questions,
            multi_processeur=self._multi_processeur,
        )

        collecteur.collecte(
            document=document,
        )

        questions_generees = self._entrepot_questions.tous()

        def ajoute_un_paquet_de_questions(
            paquet_de_questions: list[QuestionGeneree],
        ) -> None:
            self._client_albert.ajoute_chunks_dans_document(
                identifiant_collection=reponse_creation_collection.id,
                requete=RequeteAjoutChunksDansDocumentAlbert(
                    id_document=document.id_document,
                    chunks=[
                        _en_chunk_albert(question_generee)
                        for question_generee in paquet_de_questions
                    ],
                ),
            )

        self._multi_processeur.execute(
            ajoute_un_paquet_de_questions,
            _decoupe_en_paquets_de_dix(questions_generees),
        )
        # PARTIE 1
        # pour toutes les questions générées, ajouter un chunk par question au document
        # toujours pareil en splittant la liste et en faisant du multi processeur
        # en ajoutant une nouvelle méthode ajoute_chunks_dans_document


def _en_document_albert(document: Document) -> RequeteCreationDocumentAlbert:
    return RequeteCreationDocumentAlbert(
        name=document.nom_document,
        metadata={
            "source": {
                "nom_document": document.nom_document,
                "id_document": document.id_document,
            }
        },
    )


def _en_chunk_albert(question_generee: QuestionGeneree) -> dict[str, object]:
    return {
        "contenu": question_generee.contenu,
        "metadata": {
            "source": {
                "id_document": question_generee.id_document,
                "id_chunk": question_generee.id_chunk,
                "numero_page": question_generee.numero_page,
                "contenu_origine": question_generee.contenu_origine,
            }
        },
    }


def _decoupe_en_paquets_de_dix(
    elements: list[QuestionGeneree],
) -> Generator[list[QuestionGeneree], None, None]:
    iterateur = iter(elements)

    while True:
        paquet = list(islice(iterateur, 10))
        if not paquet:
            break
        yield paquet
