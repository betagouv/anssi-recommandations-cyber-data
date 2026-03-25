from dataclasses import dataclass
from itertools import islice
from typing import NamedTuple, TypedDict, Generator

from documents.docling.multi_processeur import Multiprocesseur
from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    RequeteCreationDocumentAlbert,
)
from jeopardy.questions import EntrepotQuestionGeneree, QuestionGeneree


class ChunkSource(TypedDict):
    id: int
    contenu: str
    numero_page: int


class Chunk(NamedTuple):
    contenu: str
    id: int
    numero_page: int


class Document:
    def __init__(self, data: dict[str, dict[str, str | list[ChunkSource]]]):
        self.nom_document = list(data.keys())[0]
        document_data = data[self.nom_document]
        id_document = document_data["id"]
        if isinstance(id_document, str):
            self.id_document: str = id_document
        chunks = document_data["chunks"]
        if isinstance(chunks, list):
            self.chunks: list[Chunk] = list(
                map(
                    lambda c: Chunk(
                        contenu=c["contenu"], id=c["id"], numero_page=c["numero_page"]
                    ),
                    chunks,
                )
            )


@dataclass
class ChunksAAjouter:
    chunks: list[Chunk]
    id_document: str


class CollecteurDeQuestions:
    def __init__(
        self,
        client_albert: ClientAlbertJeopardy,
        prompt: str,
        entrepot_questions_generees: EntrepotQuestionGeneree,
        multi_processeur: Multiprocesseur = Multiprocesseur(),
    ):
        super().__init__()
        self.client_albert = client_albert
        self.prompt = prompt
        self.entrepot_questions_generees = entrepot_questions_generees
        self.multi_processeur = multi_processeur

    def collecte(
        self,
        nom_collection: str,
        description_collection: str,
        document: Document,
    ):
        reponse_creation_collection = self.client_albert.cree_collection(
            f"Jeopardy : {nom_collection}", f"Jeopardy : {description_collection}"
        )
        print(f"ID de la collection créée : {reponse_creation_collection.id}")
        self.client_albert.ajoute_document(
            reponse_creation_collection.id, _en_document_albert(document)
        )

        def decoupe_la_liste_de_documents(
            iterable: list[Chunk],
        ) -> Generator[ChunksAAjouter, None, None]:
            it = iter(iterable)
            i = 0
            while True:
                sous_ensemble = list(islice(it, 10))
                if not sous_ensemble:
                    break
                yield ChunksAAjouter(
                    chunks=sous_ensemble, id_document=document.id_document
                )
                i = i + 1

        resultats = self.multi_processeur.execute(
            self._genere_questions,
            decoupe_la_liste_de_documents(document.chunks),
        )

        for questions_generees in resultats:
            for question_generee in questions_generees:
                self.entrepot_questions_generees.persiste(question_generee)

        # on fait une liste de 45K chunks
        # on slice la liste par paquets de 10
        # on invoque le multi-process
        # on se retrouve avec 225K questions
        # Explode des questions
        # On persiste toutes les questions (en mémoire)
        # Appeler Albert pour ajouter les questions au document (N questions * N chunks * N documents)

    def _genere_questions(
        self, chunks_a_ajouter: ChunksAAjouter
    ) -> list[QuestionGeneree]:
        questions_generees = []

        for chunk in chunks_a_ajouter.chunks:
            liste_questions = self.client_albert.genere_questions(
                self.prompt, chunk.contenu
            )
            for question in liste_questions:
                questions_generees.append(
                    QuestionGeneree(
                        contenu=question,
                        contenu_origine=chunk.contenu,
                        id_document=chunks_a_ajouter.id_document,
                        id_chunk=chunk.id,
                        numero_page=chunk.numero_page,
                    )
                )

        return questions_generees


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
