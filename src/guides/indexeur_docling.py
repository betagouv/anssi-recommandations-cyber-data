import json
import logging
from dataclasses import dataclass
from itertools import islice
from pathlib import Path
from typing import Generator

from guides.chunker_docling import ChunkerDocling, TypeFichier
from guides.chunker_docling_hierarchique import ChunkerDoclingHierarchique
from guides.executeur_requete import ExecuteurDeRequete
from guides.indexeur import (
    Indexeur,
    DocumentPDF,
    ReponseDocument,
    ReponseDocumentEnSucces,
    ReponseDocumentEnErreur,
)
from guides.multi_processeur import Multiprocesseur

for name in (
    "docling",
    "docling.pipeline",
    "docling.document_converter",
    "docling.chunking",
):
    logging.getLogger(name).setLevel(logging.CRITICAL)


@dataclass
class DocumentsAAjouter:
    documents: list[DocumentPDF]
    id_collection: str | None = None
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
        chunker: ChunkerDocling = ChunkerDoclingHierarchique(),
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
        self, documents: list[DocumentPDF], id_collection: str | None
    ) -> list[ReponseDocument]:
        reponse_documents = []

        def decoupe_la_liste_de_documents(
            iterable: list[DocumentPDF],
        ) -> Generator[DocumentsAAjouter]:
            it = iter(iterable)
            i = 0
            while True:
                sous_ensemble = list(islice(it, 15))
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
                f"[Liste {documents.numero_liste_en_cours}][{indice + 1} de {len(documents.documents)}] - Découpage du document {document.url_pdf}"
            )
            reponse_documents.extend(
                self.__ajoute_document(document, documents.id_collection)
            )
            if indice + 1 == len(documents.documents):
                print(f"[Liste {documents.numero_liste_en_cours}] - FINI")
        return reponse_documents

    def __ajoute_document(
        self, document: DocumentPDF, id_collection: str | None
    ) -> list[ReponseDocument]:
        nom_du_document = Path(document.chemin_pdf).name
        reponses: list[ReponseDocument] = []
        try:
            guide = self.chunker.applique(document)

            self.executeur_de_requete.initialise(self.clef_api)

            for page in guide.pages.values():
                numero_page = page.numero_page

                for bloc in page.blocs:
                    contenu_paragraphe_txt = bloc.texte
                    if len(contenu_paragraphe_txt) > 1:
                        fichiers = {
                            "file": (
                                f"{self.chunker.nom_fichier}",
                                contenu_paragraphe_txt.encode("utf-8"),
                                CONTENT_TYPE[self.chunker.type_fichier],
                            )
                        }
                        payload = {
                            "collection": str(id_collection),
                            "metadata": json.dumps(
                                {
                                    "source_url": document.url_pdf,
                                    "page": numero_page,
                                    "nom_document": guide.nom_document,
                                }
                            ),
                            "chunker": "NoSplitter",
                        }
                        response = self.executeur_de_requete.poste(
                            f"{self.url}/documents", payload, fichiers
                        )
                        try:
                            result = response.json()
                        except json.JSONDecodeError:
                            print(
                                f"Erreur de décodage JSON. Status: {response.status_code}"
                            )
                            print(f"Contenu reçu: {response.text[:200]}")
                            raise
                        if response.status_code != 201:
                            reponses.append(
                                ReponseDocumentEnErreur(
                                    detail=result.get(
                                        "detail", "Une erreur est survenue"
                                    ),
                                    document_en_erreur=nom_du_document,
                                )
                            )
                        else:
                            reponses.append(
                                ReponseDocumentEnSucces(
                                    id=result["id"],
                                    name=result.get("name", nom_du_document),
                                    collection_id=result.get(
                                        "collection_id", str(id_collection)
                                    ),
                                    created_at=result.get("created_at", ""),
                                    updated_at=result.get("updated_at", ""),
                                )
                            )
        except Exception as e:
            reponses.append(
                ReponseDocumentEnErreur(
                    detail=str(e), document_en_erreur=nom_du_document
                )
            )
        return reponses
