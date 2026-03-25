from typing import NamedTuple, Any

from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    RequeteCreationDocumentAlbert,
)


class Chunk(NamedTuple):
    contenu: str
    id: int
    numero_page: int


class Document:
    def __init__(self, data: dict[str, dict[str, Any]]):
        self.nom_document = list(data.keys())[0]
        self.id_document = data[self.nom_document]["id"]
        self.chunks: list[Chunk] = list(
            map(
                lambda c: Chunk(
                    contenu=c["contenu"], id=c["id"], numero_page=c["numero_page"]
                ),
                data[self.nom_document]["chunks"],
            )
        )


class CollecteurDeQuestions:
    def __init__(self, client_albert: ClientAlbertJeopardy, prompt: str):
        super().__init__()
        self.client_albert = client_albert
        self.prompt = prompt

    def collecte(
        self,
        nom_collection: str,
        description_collection: str,
        documents: list[Document],
    ):
        reponse_creation_collection = self.client_albert.cree_collection(
            f"Jeopardy : {nom_collection}", f"Jeopardy : {description_collection}"
        )
        for document in documents:
            self.client_albert.ajoute_document(
                reponse_creation_collection.id, _en_document_albert(document)
            )
            for chunk in document.chunks:
                self.client_albert.genere_question(self.prompt, chunk.contenu)


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
