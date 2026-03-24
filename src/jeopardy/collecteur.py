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
    def __init__(self, client_albert: ClientAlbertJeopardy):
        super().__init__()
        self.client_albert = client_albert

    def collecte(self, documents: list[Document]):
        reponse_creation_collection = self.client_albert.cree_collection()
        for document in documents:
            self.client_albert.ajoute_document(
                reponse_creation_collection.id, _en_document_albert(document)
            )
            for chunk in document.chunks:
                self.client_albert.genere_question(chunk.contenu)


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
