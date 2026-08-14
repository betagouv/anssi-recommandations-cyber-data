import json
import logging
import traceback
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import Generator
from urllib.parse import unquote

from documents.docling.chunker_docling import TypeFichier, ChunkerDocling
from documents.docling.document import Document
from documents.docling.chunker_docling_mqc import ChunkerDoclingMQC
from documents.docling.multi_processeur import Multiprocesseur
from documents.html.document_html import BlocPageReponse
from documents.indexeur.indexeur import (
    DocumentAIndexer,
    Indexeur,
    ReponseDocument,
    ReponseDocumentEnErreur,
    ReponseDocumentEnSucces,
    ReponseDocumentMaitriseEnSucces,
    ReponseDocumentIndexePartiellement,
)
from documents.page import BlocPage
from infra.executeur_requete import ExecuteurDeRequete
from infra.interval import AdaptateurInterval
from infra.logger import log

for name in (
    "docling",
    "docling.pipeline",
    "docling.document_converter",
    "docling.chunking",
):
    logging.getLogger(name).setLevel(logging.CRITICAL)


def _trouve_une_metadata_trop_longue(metadata: object, emplacement: str) -> str | None:
    if not isinstance(metadata, dict):
        return None
    for nom, valeur in metadata.items():
        if isinstance(valeur, str) and len(valeur) > 255:
            return (
                f"La métadonnée {nom} {emplacement} dépasse la longueur maximale "
                "de 255 caractères"
            )
    return None


def _prepare_les_payloads(
    document: Document,
    les_blocs_non_vides: list[BlocPage],
) -> tuple[list[dict[str, object]], dict[str, object], str | None]:
    payloads_chunks: list[dict[str, object]] = [
        {"content": bloc.texte, "metadata": document.metadata(bloc)}
        for bloc in les_blocs_non_vides
    ]
    for numero_chunk, chunk in enumerate(payloads_chunks):
        erreur_metadata = _trouve_une_metadata_trop_longue(
            chunk["metadata"], f"du chunk {numero_chunk}"
        )
        if erreur_metadata is not None:
            return [], {}, erreur_metadata

    metadata_document = {
        "source_url": document.url,
        "nom_document": unquote(document.nom_document),
    }
    erreur_metadata = _trouve_une_metadata_trop_longue(
        metadata_document, "du document"
    )
    return payloads_chunks, metadata_document, erreur_metadata


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
            log(
                __name__,
                f"[Liste {documents.numero_liste_en_cours}][{indice + 1} de {len(documents.documents)}] - Découpage du document {document.url}",
            )
            reponse_documents.extend(
                self.__ajoute_document(document, documents.id_collection)
            )
            if indice + 1 == len(documents.documents):
                log(__name__, f"[Liste {documents.numero_liste_en_cours}] - FINI")
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

            payloads_chunks, metadata_document, erreur_metadata = _prepare_les_payloads(
                document, les_blocs_non_vides
            )
            if erreur_metadata is not None:
                reponses.append(
                    ReponseDocumentEnErreur(
                        detail=erreur_metadata,
                        document_en_erreur=nom_du_document,
                    )
                )
                return reponses
            if not payloads_chunks:
                return reponses

            self.executeur_de_requete.initialise_connexion_securisee(self.clef_api)

            payload = {
                "collection_id": int(id_collection),
                "name": unquote(nom_du_document),
                "metadata": json.dumps(metadata_document),
                "disable_chunking": True,
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

            mapping = {
                bloc.id_reponse: bloc.reponse
                for bloc in les_blocs_non_vides
                if isinstance(bloc, BlocPageReponse) and bloc.id_reponse
            }
            resultat_indexation: ReponseDocument
            if document.erreurs_pages:
                resultat_indexation = ReponseDocumentIndexePartiellement(
                    id=resultat["id"],
                    nom=resultat.get("name", nom_du_document),
                    id_collection=resultat.get("collection_id", str(id_collection)),
                    date_creation=resultat.get("created_at", ""),
                    date_mise_a_jour=resultat.get("updated_at", ""),
                    pages_non_indexees=tuple(
                        erreur.numero_page for erreur in document.erreurs_pages
                    ),
                    erreurs=tuple(erreur.detail for erreur in document.erreurs_pages),
                )
            elif mapping:
                resultat_indexation = ReponseDocumentMaitriseEnSucces(
                    id=resultat["id"],
                    name=resultat.get("name", nom_du_document),
                    collection_id=resultat.get("collection_id", str(id_collection)),
                    created_at=resultat.get("created_at", ""),
                    updated_at=resultat.get("updated_at", ""),
                    mapping=mapping,
                    chemin_source=str(document_a_indexer.chemin),
                )
            else:
                resultat_indexation = ReponseDocumentEnSucces(
                    id=resultat["id"],
                    name=resultat.get("name", nom_du_document),
                    collection_id=resultat.get("collection_id", str(id_collection)),
                    created_at=resultat.get("created_at", ""),
                    updated_at=resultat.get("updated_at", ""),
                )

            for debut in range(0, len(payloads_chunks), 64):
                payload_chunks = {"chunks": payloads_chunks[debut : debut + 64]}
                reponse_chunk = self.executeur_de_requete.poste(
                    f"{self.url}/documents/{resultat['id']}/chunks",
                    payload_chunks,
                    None,
                )

                AdaptateurInterval.pause()

                resultat_chunk = reponse_chunk.json()
                if reponse_chunk.status_code != 201:
                    resultat_indexation = ReponseDocumentEnErreur(
                        detail=str(resultat_chunk),
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
