from __future__ import annotations

import json
from typing import Any, Callable

from infra.executeur_requete import ExecuteurDeRequete
from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    ConfigurationJeopardy,
    ReponseCreationCollection,
    ReponseCreationDocument,
    RequeteCreationDocumentAlbert,
    RequeteAjoutChunksDansDocumentAlbert,
    ReponseDocumentOrigine,
    ReponseDocumentsCollectionOrigine,
)


class ClientAlbertJeopardyReel(ClientAlbertJeopardy):
    def __init__(
        self,
        configuration: ConfigurationJeopardy,
        executeur_de_requete=ExecuteurDeRequete(),
    ):
        super().__init__()
        self._configuration = configuration
        self._cle_api = configuration.cle_api
        self._executeur_de_requete = executeur_de_requete

    def cree_collection(
        self, nom_collection: str, description_collection: str
    ) -> ReponseCreationCollection:
        url = f"{self._configuration.base_url}/collections"
        payload = {
            "name": nom_collection,
            "description": description_collection,
        }

        self._executeur_de_requete.initialise_connexion_securisee(self._cle_api)
        reponse = self._executeur_de_requete.poste(url, payload, fichiers=None)
        reponse.raise_for_status()

        corps = reponse.json()
        identifiant = corps.get("id")
        return ReponseCreationCollection(id=identifiant)

    def cree_document(
        self, identifiant_collection: str, document: RequeteCreationDocumentAlbert
    ) -> ReponseCreationDocument:
        url = f"{self._configuration.base_url}/documents"
        payload = {
            "collection_id": int(identifiant_collection),
            "name": document.name,
            "metadata": json.dumps(document.metadata),
            "disable_chunking": True,
        }

        self._executeur_de_requete.initialise_connexion_securisee(self._cle_api)
        reponse = self._executeur_de_requete.poste(url, payload, fichiers={})
        reponse.raise_for_status()
        corps = reponse.json()
        return ReponseCreationDocument(id=str(corps.get("id")))

    def genere_questions(self, prompt: str, contenu: str) -> list[str]:
        url = f"{self._configuration.base_url}/chat/completions"
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Paragraphe :\n{contenu}"},
        ]
        payload = {
            "model": self._configuration.modele_generation,
            "messages": messages,
            "stream": False,
            "n": 1,
        }
        self._executeur_de_requete.initialise_connexion_securisee(self._cle_api)
        reponse = self._executeur_de_requete.poste(url, payload, fichiers=None)
        reponse.raise_for_status()
        corps = reponse.json()
        contenu_reponse = (
            corps.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        )
        try:
            json_reponse: dict[str, Any | None] = json.loads(contenu_reponse)
        except json.JSONDecodeError:
            return []
        payload_questions = json_reponse.get("questions")
        return payload_questions if payload_questions is not None else []

    def ajoute_chunks_dans_document(
        self,
        identifiant_collection: str,
        requete: RequeteAjoutChunksDansDocumentAlbert,
    ) -> None:
        url = f"{self._configuration.base_url}/documents/{requete.id_document}/chunks"
        payload = {
            "chunks": requete.chunks,
        }
        self._executeur_de_requete.initialise_connexion_securisee(self._cle_api)
        reponse = self._executeur_de_requete.poste(url, payload, fichiers=None)
        reponse.raise_for_status()

    def recupere_documents_collection(
        self, id_collection: str
    ) -> ReponseDocumentsCollectionOrigine:
        self._executeur_de_requete.initialise_connexion_securisee(self._cle_api)

        def mappe_document(document: dict) -> ReponseDocumentOrigine:
            return ReponseDocumentOrigine(
                id=str(document["id"]),
                nom=str(document.get("name", "")),
                nombre_chunks=int(document.get("chunk_count", 0)),
            )

        documents = self._recupere_reponse_albert(
            offset=0,
            url=f"{self._configuration.base_url}/documents?collection_id={int(id_collection)}&limit=100",
            mappe=mappe_document,
        )
        return ReponseDocumentsCollectionOrigine(
            id=id_collection,
            documents=documents,
        )

    def _recupere_reponse_albert(
        self, offset: int, url: str, mappe: Callable[[dict], Any]
    ) -> list:
        reponse = self._executeur_de_requete.recupere(
            (f"{url}&offset={offset}")
        )
        reponse.raise_for_status()
        corps = reponse.json()
        donnees: list[dict] = []
        if isinstance(corps, dict):
            data = corps.get("data", [])
            if isinstance(data, list):
                donnees = data
        elif isinstance(corps, list):
            donnees = corps
        documents = [mappe(document) for document in donnees]
        if len(donnees) < 100:
            return documents
        return documents + self._recupere_reponse_albert(offset + 100, url, mappe)

    def recupere_chunks_document(self, id_document: str) -> list[dict]:
        self._executeur_de_requete.initialise_connexion_securisee(self._cle_api)
        tous_les_chunks = self._recupere_reponse_albert(
            offset=0,
            url=f"{self._configuration.base_url}/documents/{id_document}/chunks?limit=100",
            mappe=lambda chunks: chunks,
        )
        return tous_les_chunks
