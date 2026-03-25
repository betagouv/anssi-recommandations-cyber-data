from typing import NamedTuple, TypedDict

from jeopardy.questions import EntrepotQuestionGeneree, QuestionGeneree
from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    RequeteCreationDocumentAlbert,
)


class ChunkSource(TypedDict):
    id: str
    contenu: str
    numero_page: int


class Chunk(NamedTuple):
    contenu: str
    id: str
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


class CollecteurDeQuestions:
    def __init__(
        self,
        client_albert: ClientAlbertJeopardy,
        prompt: str,
        entrepot_questions_generees: EntrepotQuestionGeneree,
    ):
        super().__init__()
        self.client_albert = client_albert
        self.prompt = prompt
        self.entrepot_questions_generees = entrepot_questions_generees

    def collecte(
        self,
        nom_collection: str,
        description_collection: str,
        document: Document,
    ):
        reponse_creation_collection = self.client_albert.cree_collection(
            f"Jeopardy : {nom_collection}", f"Jeopardy : {description_collection}"
        )
        self.client_albert.ajoute_document(
            reponse_creation_collection.id, _en_document_albert(document)
        )
        # on fait une liste de 45K chunks
        # on slice la liste par paquets de 10
        # on invoque le multi-process
        # on se retrouve avec 225K questions
        for chunk in (
            document.chunks
        ):  # Entre quelques chunks et plusieurs milliers de chunks par document
            questions = self.client_albert.genere_questions(self.prompt, chunk.contenu)
            for question in questions:
                self.entrepot_questions_generees.persiste(
                    QuestionGeneree(
                        contenu=question,
                        contenu_origine=chunk.contenu,
                        id_document=document.id_document,
                        id_chunk=chunk.id,
                        numero_page=chunk.numero_page,
                    )
                )

            # Explode des questions
            # On persiste toutes les questions (en mémoire)
        # Appeler Albert pour ajouter les questions au document (N questions * N chunks * N documents)


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
