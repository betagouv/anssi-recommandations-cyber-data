import json
import logging
import traceback
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import Generator

from documents.docling.chunker_docling import TypeFichier, ChunkerDocling
from documents.docling.chunker_docling_mqc import ChunkerDoclingMQC
from documents.docling.multi_processeur import Multiprocesseur
from documents.indexeur.indexeur import (
    DocumentAIndexer,
    Indexeur,
    ReponseDocument,
    ReponseDocumentEnErreur,
    ReponseDocumentEnSucces,
)
from documents.page import BlocPage, Page
from infra.executeur_requete import ExecuteurDeRequete

for name in (
    "docling",
    "docling.pipeline",
    "docling.document_converter",
    "docling.chunking",
):
    logging.getLogger(name).setLevel(logging.CRITICAL)


@dataclass
class DocumentsAAjouter:
    documents: list[DocumentAIndexer]
    id_collection: str = ""
    numero_liste_en_cours: int = 0


CONTENT_TYPE: dict[TypeFichier, str] = {
    TypeFichier.TEXTE: "text/plain",
    TypeFichier.PDF: "application/pdf",
}


class IndexeurDocling(Indexeur):
    def __init__(
        self,
        url: str,
        clef_api: str,
        chunker: ChunkerDocling = ChunkerDoclingMQC(),
        executeur_de_requete: ExecuteurDeRequete = ExecuteurDeRequete(),
        multi_processeur: Multiprocesseur = Multiprocesseur(),
    ):
        super().__init__()
        self.multi_processeur = multi_processeur
        self.executeur_de_requete = executeur_de_requete
        self.chunker = chunker
        self.url = url
        self.clef_api = clef_api

    def ajoute_documents(
        self, documents: list[DocumentAIndexer], id_collection: str
    ) -> list[ReponseDocument]:
        reponse_documents = []

        def decoupe_la_liste_de_documents(
            iterable: list[DocumentAIndexer],
        ) -> Generator[DocumentsAAjouter]:
            it = iter(iterable)
            i = 0
            while True:
                sous_ensemble = list(islice(it, 10))
                if not sous_ensemble:
                    break
                yield DocumentsAAjouter(
                    documents=sous_ensemble,
                    id_collection=id_collection,
                    numero_liste_en_cours=i,
                )
                i = i + 1

        documents_crees: list[list[ReponseDocument]] = self.multi_processeur.execute(
            self._ajoute_les_documents, decoupe_la_liste_de_documents(documents)
        )
        reponse_documents.extend(
            [x for sous_liste in documents_crees for x in sous_liste]
        )
        return reponse_documents

    def _ajoute_les_documents(
        self, documents: DocumentsAAjouter
    ) -> list[ReponseDocument]:
        reponse_documents = []
        for indice, document in enumerate(documents.documents):
            print(
                f"[Liste {documents.numero_liste_en_cours}][{indice + 1} de {len(documents.documents)}] - Découpage du document {document.url}"
            )
            reponse_documents.extend(
                self.__ajoute_document(document, documents.id_collection)
            )
            if indice + 1 == len(documents.documents):
                print(f"[Liste {documents.numero_liste_en_cours}] - FINI")
        return reponse_documents

    def __ajoute_document(
        self, document_a_indexer: DocumentAIndexer, id_collection: str
    ) -> list[ReponseDocument]:
        nom_du_document = Path(document_a_indexer.chemin).name
        reponses: list[ReponseDocument] = []
        try:
            document = self.chunker.applique(document_a_indexer)

            les_blocs_non_vides = [
                bloc
                for page in document.pages.values()
                for bloc in page.blocs
                if len(bloc.texte) > 1
            ]
            if not les_blocs_non_vides:
                return reponses

            self.executeur_de_requete.initialise(self.clef_api)

            payload = {
                "collection_id": int(id_collection),
                "name": nom_du_document,
                "metadata": json.dumps(
                    {"source_url": document.url, "nom_document": document.nom_document}
                ),
                "chunker": "NoSplitter",
            }
            reponse_document = self.executeur_de_requete.poste(
                f"{self.url}/documents", payload, {}
            )

            resultat = reponse_document.json()

            if reponse_document.status_code != 201:
                reponses.append(
                    ReponseDocumentEnErreur(
                        detail=resultat.get("detail", "Une erreur est survenue"),
                        document_en_erreur=nom_du_document,
                    )
                )
                return reponses

            resultat_indexation: ReponseDocumentEnSucces | ReponseDocumentEnErreur = (
                ReponseDocumentEnSucces(
                    id=resultat["id"],
                    name=resultat.get("name", nom_du_document),
                    collection_id=resultat.get("collection_id", str(id_collection)),
                    created_at=resultat.get("created_at", ""),
                    updated_at=resultat.get("updated_at", ""),
                )
            )

            def _en_payload(page: Page, bloc: BlocPage) -> dict:
                return {"content": bloc.texte, "metadata": document.metadata(page)}

            for page in document.pages.values():
                tous_les_blocs = list(
                    filter(lambda bloc: len(bloc.texte) > 1, page.blocs)
                )
                payload_chunks = {
                    "chunks": list(
                        map(lambda bloc: _en_payload(page, bloc), tous_les_blocs)
                    )
                }
                reponse_chunk = self.executeur_de_requete.poste(
                    f"{self.url}/documents/{resultat['id']}/chunks",
                    payload_chunks,
                    None,
                )

                resultat_chunk = reponse_chunk.json()
                if reponse_chunk.status_code != 201:
                    resultat_indexation = ReponseDocumentEnErreur(
                        detail=resultat_chunk.get("detail")[0].msg,
                        document_en_erreur=nom_du_document,
                    )
                    break

            reponses.append(resultat_indexation)

        except Exception:
            tb = traceback.format_exc()
            reponses.append(
                ReponseDocumentEnErreur(detail=tb, document_en_erreur=nom_du_document)
            )
        return reponses
