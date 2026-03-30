from __future__ import annotations

from functools import partial
from itertools import islice
from typing import Generator

from documents.docling.multi_processeur import Multiprocesseur
from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    RequeteAjoutChunksDansDocumentAlbert,
    RequeteCreationDocumentAlbert,
)
from jeopardy.collecteur import ChunkSource, CollecteurDeQuestions, Document
from jeopardy.prompt_generation_question import PROMPT_SYSTEME_GENERATION_QUESTIONS_FR
from jeopardy.questions import EntrepotQuestionGeneree, QuestionGeneree


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
        self, nom_collection: str, description_collection: str, id_document: str
    ):
        reponse_creation_collection = self._client_albert.cree_collection(
            f"Jeopardy : {nom_collection}", f"Jeopardy : {description_collection}"
        )

        document_depuis_albert = self._recupere_et_mappe_document_depuis_albert(
            id_document
        )
        reponse_creation_document = self._client_albert.cree_document(
            reponse_creation_collection.id, _en_document_albert(document_depuis_albert)
        )

        collecteur = CollecteurDeQuestions(
            client_albert=self._client_albert,
            prompt=self._prompt,
            entrepot_questions_generees=self._entrepot_questions,
            multi_processeur=self._multi_processeur,
        )
        collecteur.collecte(document=document_depuis_albert)

        questions_generees = self._entrepot_questions.tous()

        self._multi_processeur.execute(
            partial(
                self._ajoute_chunks_dans_document,
                reponse_creation_collection.id,
                reponse_creation_document.id,
            ),
            _decoupe_en_paquets_de_dix(questions_generees),
        )

    def _ajoute_chunks_dans_document(
        self,
        identifiant_collection: str,
        identifiant_document: str,
        paquet_de_questions: list[QuestionGeneree],
    ) -> None:
        self._client_albert.ajoute_chunks_dans_document(
            identifiant_collection=identifiant_collection,
            requete=RequeteAjoutChunksDansDocumentAlbert(
                id_document=identifiant_document,
                chunks=[
                    _en_chunk_albert(question_generee)
                    for question_generee in paquet_de_questions
                ],
            ),
        )

    def _recupere_et_mappe_document_depuis_albert(self, id_document: str) -> Document:
        chunks_document = self._client_albert.recupere_chunks_document(id_document)
        if not chunks_document:
            raise ValueError(f"Aucun chunk trouve pour le document {id_document}.")

        return _mappe_vers_document(
            nom_document=f"document-{id_document}",
            id_document=id_document,
            chunks_document=chunks_document,
        )


def _en_document_albert(document: Document) -> RequeteCreationDocumentAlbert:
    return RequeteCreationDocumentAlbert(
        name=document.nom_document,
        metadata={
            "source_nom_document": document.nom_document,
            "source_id_document": document.id_document,
        },
    )


def _en_chunk_albert(question_generee: QuestionGeneree) -> dict[str, object]:
    return {
        "content": question_generee.contenu,
        "metadata": {
            "source_id_document": question_generee.id_document,
            "source_id_chunk": question_generee.id_chunk,
            "source_numero_page": question_generee.numero_page,
        },
    }


def _mappe_vers_document(
    nom_document: str, id_document: str, chunks_document: list[dict]
) -> Document:
    chunks = [_mappe_un_chunk(chunk) for chunk in chunks_document]
    return Document({nom_document: {"id": id_document, "chunks": chunks}})


def _mappe_un_chunk(chunk: dict) -> ChunkSource:
    metadata = chunk.get("metadata", {})
    source = metadata.get("source", {}) if isinstance(metadata, dict) else {}

    id_chunk = chunk.get("id", source.get("id_chunk", 0))
    contenu = chunk.get("contenu", chunk.get("content", ""))
    numero_page = source.get("numero_page", 1)

    return ChunkSource(
        {
            "id": int(id_chunk),
            "contenu": str(contenu),
            "numero_page": int(numero_page),
        }
    )


def _decoupe_en_paquets_de_dix(
    elements: list[QuestionGeneree],
) -> Generator[list[QuestionGeneree], None, None]:
    iterateur = iter(elements)

    while True:
        paquet = list(islice(iterateur, 10))
        if not paquet:
            break
        yield paquet
