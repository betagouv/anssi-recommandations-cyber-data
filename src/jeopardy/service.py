from __future__ import annotations

from itertools import islice
from typing import Generator

from configuration import recupere_configuration
from documents.docling.multi_processeur import Multiprocesseur
from evenement.bus import BusEvenement
from evenement.fabrique_bus_evenements import fabrique_bus_evenements
from infra.executeur_requete import ExecuteurDeRequete
from infra.interval import Interval
from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    RequeteAjoutChunksDansDocumentAlbert,
    RequeteCreationDocumentAlbert,
)
from jeopardy.client_albert_jeopardy_reel import ClientAlbertJeopardyReel
from jeopardy.collecteur import ChunkSource, CollecteurDeQuestions, Document
from jeopardy.prompt_generation_question import PROMPT_SYSTEME_GENERATION_QUESTIONS_FR
from jeopardy.questions import (
    EntrepotQuestionGeneree,
    QuestionGeneree,
    EntrepotQuestionGenereeMemoire,
)


class ServiceJeopardy:
    def __init__(
        self,
        client_albert: ClientAlbertJeopardy,
        entrepot_questions: EntrepotQuestionGeneree,
        bus_evenement: BusEvenement,
        prompt: str = PROMPT_SYSTEME_GENERATION_QUESTIONS_FR,
        multi_processeur: Multiprocesseur = Multiprocesseur(),
    ):
        super().__init__()
        self._entrepot_questions = entrepot_questions
        self._client_albert = client_albert
        self._prompt = prompt
        self._bus_evenement = bus_evenement
        self._multi_processeur = multi_processeur

    def jeopardyse(
        self,
        nom_collection: str,
        description_collection: str,
        id_collection: str,
        taille_paquet_chunks=10,
    ):
        reponse_creation_collection = self._client_albert.cree_collection(
            f"Jeopardy : {nom_collection}", f"Jeopardy : {description_collection}"
        )

        documents_depuis_albert = self._recupere_et_mappe_collection_depuis_albert(
            id_collection
        )

        for document_depuis_albert in documents_depuis_albert:
            try:
                reponse_creation_document = self._client_albert.cree_document(
                    reponse_creation_collection.id,
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

                questions_generees = list(self._entrepot_questions.tous())

                self._ajoute_chunks_dans_document(
                    reponse_creation_collection.id,
                    reponse_creation_document.id,
                    questions_generees,
                )
            except Exception as e:
                print(
                    f"Erreur lors de la collecte du document {document_depuis_albert.id_document}: {e}"
                )
                # TODO: ajouter du feedback
                continue

    def _ajoute_chunks_dans_document(
        self,
        identifiant_collection: str,
        identifiant_document: str,
        questions_generees: list[QuestionGeneree],
    ) -> None:
        try:
            paquets = _decoupe_en_paquets(questions_generees, 64)
            for paquet in paquets:
                print(f"Envoi de {len(paquet)} chunks")
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
        except Exception:
            # TODO: Ajouter du feedback
            return

    def _recupere_et_mappe_collection_depuis_albert(
        self, id_collection: str
    ) -> list[Document]:
        reponse_documents_collection = (
            self._client_albert.recupere_documents_collection(id_collection)
        )
        documents: list[Document] = []

        for document_collection in reponse_documents_collection.documents:
            try:
                id_document = document_collection.id
                chunks_document = self._client_albert.recupere_chunks_document(
                    id_document
                )

                documents.append(
                    _mappe_vers_document(
                        nom_document=document_collection.nom,
                        id_document=id_document,
                        chunks_document=chunks_document,
                    )
                )
            except Exception:
                # Rajouter du feedback pour dire qu’un document manque
                continue

        return documents


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


def fabrique_service_jeopardy() -> ServiceJeopardy:
    configuration_jeopardy = recupere_configuration().jeopardy
    return ServiceJeopardy(
        ClientAlbertJeopardyReel(configuration_jeopardy, ExecuteurDeRequete()),
        EntrepotQuestionGenereeMemoire(),
        fabrique_bus_evenements(),
    )
