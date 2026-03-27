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
        self._identifiant_collection_en_cours: str | None = None
        self._id_document_en_cours: str | None = None

    def jeopardyse(
        self, nom_collection: str, description_collection: str, document: Document
    ):
        # PARTIE 2
        # plutôt que passer le document, donner l’ID du document Albert pour qu’il aille le chercher
        # le mapper en document
        reponse_creation_collection = self._client_albert.cree_collection(
            f"Jeopardy : {nom_collection}", f"Jeopardy : {description_collection}"
        )
        reponse_creation_document = self._client_albert.cree_document(
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

        self._identifiant_collection_en_cours = reponse_creation_collection.id
        self._id_document_en_cours = reponse_creation_document.id

        self._multi_processeur.execute(
            self._ajoute_chunks_dans_document,
            _decoupe_en_paquets_de_dix(questions_generees),
        )

    def _ajoute_chunks_dans_document(
        self, paquet_de_questions: list[QuestionGeneree]
    ) -> None:
        if (
            self._identifiant_collection_en_cours is None
            or self._id_document_en_cours is None
        ):
            raise ValueError("Le contexte d'ajout des questions n'est pas initialisé.")

        self._client_albert.ajoute_chunks_dans_document(
            identifiant_collection=self._identifiant_collection_en_cours,
            requete=RequeteAjoutChunksDansDocumentAlbert(
                id_document=self._id_document_en_cours,
                chunks=[
                    _en_chunk_albert(question_generee)
                    for question_generee in paquet_de_questions
                ],
            ),
        )


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
