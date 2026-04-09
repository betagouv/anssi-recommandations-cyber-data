from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import islice
from typing import Generator

from documents.docling.multi_processeur import Multiprocesseur
from evenement.bus import BusEvenement
from infra.interval import Interval
from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    RequeteAjoutChunksDansDocumentAlbert,
    RequeteCreationDocumentAlbert,
    ReponseDocumentOrigine,
)
from jeopardy.collecteur import ChunkSource, CollecteurDeQuestions, Document
from jeopardy.evenements import (
    CorpsEvenementJeopardyChunkAjouteEnErreur,
    EvenementJeopardyChunkAjouteEnErreur,
    EvenementQuestionsGenerees,
    CorpsEvenementQuestionsGenerees,
    EvenementJeopardyChunksAjoutes,
    CorpsEvenementJeopardyChunksAjoutes,
    EvenementJeopardyGenereEnErreur,
    CorpsEvenementJeopardyGenereEnErreur,
)
from jeopardy.prompt_generation_question import PROMPT_SYSTEME_GENERATION_QUESTIONS_FR
from jeopardy.questions import (
    EntrepotQuestionGeneree,
    QuestionGeneree,
)


@dataclass
class CollectionEntiere:
    id_collection: str
    nom_collection: str
    description_collection: str


@dataclass
class ListeDeDocuments:
    id_collection: str
    noms_documents: list[str]


class ServiceJeopardyse(ABC):
    def __init__(
        self,
        client_albert: ClientAlbertJeopardy,
        entrepot_questions: EntrepotQuestionGeneree,
        bus_evenement: BusEvenement,
        prompt: str = PROMPT_SYSTEME_GENERATION_QUESTIONS_FR,
        multi_processeur: Multiprocesseur = Multiprocesseur(7),
    ):
        super().__init__()
        self._entrepot_questions = entrepot_questions
        self._client_albert = client_albert
        self._prompt = prompt
        self._bus_evenement = bus_evenement
        self._multi_processeur = multi_processeur
        self._logger = logging.getLogger(__name__)

    def jeopardyse(
        self,
        donnees: CollectionEntiere | ListeDeDocuments,
        taille_paquet_chunks: int = 10,
    ):
        documents, id_collection_jeopardy = self.recupere_les_documents(
            donnees, taille_paquet_chunks
        )
        self._jeopardyse_les_documents(
            self._mappe_les_documents(documents), id_collection_jeopardy
        )

    @abstractmethod
    def recupere_les_documents(
        self, donnees: CollectionEntiere | ListeDeDocuments, taille_paquet_chunks=10
    ) -> tuple[list[ReponseDocumentOrigine], str]:
        pass

    def _ajoute_chunks_dans_document(
        self,
        identifiant_collection: str,
        identifiant_document: str,
        questions_generees: list[QuestionGeneree],
    ) -> None:
        try:
            paquets = _decoupe_en_paquets(questions_generees, 64)
            for paquet in paquets:
                self._client_albert.ajoute_chunks_dans_document(
                    identifiant_collection=identifiant_collection,
                    requete=RequeteAjoutChunksDansDocumentAlbert(
                        id_document=identifiant_document,
                        chunks=[
                            _en_chunk_albert(question_generee)
                            for question_generee in paquet
                        ],
                    ),
                )
                Interval.pause()
        except Exception as e:
            message_erreur = f"Erreur lors de l'ajout du chunk au document {identifiant_document} : {e}"
            self._bus_evenement.publie(
                EvenementJeopardyChunkAjouteEnErreur(
                    corps=CorpsEvenementJeopardyChunkAjouteEnErreur(
                        erreur=message_erreur
                    )
                )
            )
            return

    def _jeopardyse_un_document(
        self, document_depuis_albert: Document, id_collection_jeopardy
    ):
        date_debut = time.time()
        reponse_creation_document = self._client_albert.cree_document(
            id_collection_jeopardy,
            _en_document_albert(document_depuis_albert),
        )

        collecteur = CollecteurDeQuestions(
            client_albert=self._client_albert,
            prompt=self._prompt,
            entrepot_questions_generees=self._entrepot_questions,
            bus_evenement=self._bus_evenement,
            multi_processeur=self._multi_processeur,
        )
        collecteur.collecte(document=document_depuis_albert)

        questions_generees = list(
            self._entrepot_questions.par_id_document(document_depuis_albert.id_document)
        )

        date_fin = time.time()
        temps = date_fin - date_debut
        self._bus_evenement.publie(
            EvenementQuestionsGenerees(
                corps=CorpsEvenementQuestionsGenerees(
                    questions_generees=questions_generees,
                    id_document_origine=document_depuis_albert.id_document,
                    nombre_chunks_origine=len(document_depuis_albert.chunks),
                    id_collection_jeopardy=id_collection_jeopardy,
                    id_document_jeopardy=reponse_creation_document.id,
                    temps_traitement=int(temps),
                )
            )
        )
        date_debut = time.time()
        self._ajoute_chunks_dans_document(
            id_collection_jeopardy,
            reponse_creation_document.id,
            questions_generees,
        )
        date_fin = time.time()
        self._bus_evenement.publie(
            EvenementJeopardyChunksAjoutes(
                corps=CorpsEvenementJeopardyChunksAjoutes(
                    chunks=questions_generees, temps=int(date_fin - date_debut)
                )
            )
        )

    def _mappe_un_document(
        self, document_collection: ReponseDocumentOrigine, id_document: str
    ) -> Document:
        chunks_document = self._client_albert.recupere_chunks_document(id_document)

        document = _mappe_vers_document(
            nom_document=document_collection.nom,
            id_document=id_document,
            chunks_document=chunks_document,
        )
        return document

    def _mappe_les_documents(
        self, documents_recuperes: list[ReponseDocumentOrigine]
    ) -> list[Document]:
        documents: list[Document] = []

        for document_collection in documents_recuperes:
            try:
                id_document = document_collection.id
                documents.append(
                    self._mappe_un_document(document_collection, id_document)
                )
            except Exception:
                # Rajouter du feedback pour dire qu’un document manque
                continue

        return documents

    def _jeopardyse_les_documents(
        self, documents_depuis_albert: list[Document], id_collection_jeopardy: str
    ):
        for document_depuis_albert in documents_depuis_albert:
            try:
                self._jeopardyse_un_document(
                    document_depuis_albert, id_collection_jeopardy
                )
            except Exception as e:
                message_erreur = f"Erreur lors de la collecte du document {document_depuis_albert.id_document}: {e}"
                self._bus_evenement.publie(
                    EvenementJeopardyGenereEnErreur(
                        corps=CorpsEvenementJeopardyGenereEnErreur(
                            erreur=message_erreur
                        )
                    )
                )
                continue


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
            "source_numero_page": question_generee.page,
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
    numero_page = metadata.get("page", 1)

    return ChunkSource(
        {
            "id": int(id_chunk),
            "contenu": str(contenu),
            "page": int(numero_page),
        }
    )


def _decoupe_en_paquets(
    elements: list[QuestionGeneree], taille_paquet
) -> Generator[list[QuestionGeneree], None, None]:
    iterateur = iter(elements)

    while True:
        paquet = list(islice(iterateur, taille_paquet))
        if not paquet:
            break
        yield paquet
