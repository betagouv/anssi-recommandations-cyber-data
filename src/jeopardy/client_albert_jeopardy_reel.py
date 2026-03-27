from __future__ import annotations

import json
from typing import Any

from infra.executeur_requete import ExecuteurDeRequete
from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    ConfigurationJeopardy,
    ReponseCreationCollection,
    ReponseCreationDocument,
    RequeteCreationDocumentAlbert,
    RequeteAjoutChunksDansDocumentAlbert,
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
            "metadata": document.metadata,
            "disable_chunking": True,
        }

        self._executeur_de_requete.initialise_connexion_securisee(self._cle_api)
        reponse = self._executeur_de_requete.poste(url, payload, fichiers=None)
        corps = reponse.json()
        return ReponseCreationDocument(id=str(corps.get("id")))

    def ajoute_document(
        self, identifiant_collection: str, document: RequeteCreationDocumentAlbert
    ) -> None:
        url = (
            f"{self._configuration.base_url}/collections/"
            f"{identifiant_collection}/documents"
        )
        payload = {
            "name": document.name,
            "metadata": document.metadata,
        }
        self._executeur_de_requete.initialise_connexion_securisee(self._cle_api)
        self._executeur_de_requete.poste(url, payload, fichiers=None)

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
        corps = reponse.json()
        contenu_reponse = (
            corps.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        )
        json_reponse: dict[str, Any | None] = json.loads(contenu_reponse)
        payload_questions = json_reponse.get("questions")
        return payload_questions if payload_questions is not None else []

    def ajoute_chunks_dans_document(
        self,
        identifiant_collection: str,
        requete: RequeteAjoutChunksDansDocumentAlbert,
    ) -> None:
        url = (
            f"{self._configuration.base_url}/collections/"
            f"{identifiant_collection}/documents/{requete.id_document}/chunks"
        )
        payload = {
            "chunks": requete.chunks,
        }
        self._executeur_de_requete.initialise_connexion_securisee(self._cle_api)
        self._executeur_de_requete.poste(url, payload, fichiers=None)
