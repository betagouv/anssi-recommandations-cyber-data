from math import ceil
from typing import Any

from adaptateurs.client_albert_chunks import ClientAlbertChunks, ReponseChunkAlbert
from documents.contexte_documentaire import separe_le_contenu_indexe
from infra.executeur_requete import ExecuteurDeRequete

LIMITE_CHUNKS_PAR_PAGE = 100


class ClientAlbertChunksReel(ClientAlbertChunks):
    def __init__(
        self,
        url: str,
        cle_api: str,
        executeur_de_requete: ExecuteurDeRequete = ExecuteurDeRequete(),
    ):
        self.url = url
        self.executeur_de_requete = executeur_de_requete
        self.executeur_de_requete.initialise_connexion_securisee(cle_api)

    def recupere_les_chunks_du_document(
        self, id_document: str
    ) -> list[ReponseChunkAlbert]:
        reponse_document = self.executeur_de_requete.recupere(
            f"{self.url}/documents/{id_document}"
        )
        nombre_de_chunks: int = reponse_document.json()["chunks"]
        nombre_de_pages = ceil(nombre_de_chunks / LIMITE_CHUNKS_PAR_PAGE)
        resultat: list[ReponseChunkAlbert] = []
        for numero_page in range(nombre_de_pages):
            offset = numero_page * LIMITE_CHUNKS_PAR_PAGE
            reponse = self.executeur_de_requete.recupere(
                f"{self.url}/documents/{id_document}/chunks",
                {"limit": LIMITE_CHUNKS_PAR_PAGE, "offset": offset},
            )
            chunks: list[dict[str, Any]] = reponse.json()["data"]
            resultat.extend(
                _mappe_un_chunk(chunk)
                for chunk in chunks
            )
        return resultat


def _mappe_un_chunk(chunk: dict[str, Any]) -> ReponseChunkAlbert:
    contenu, contexte_documentaire = separe_le_contenu_indexe(
        str(chunk.get("content", ""))
    )
    return ReponseChunkAlbert(
        id=str(chunk["id"]),
        contenu=contenu,
        metadonnees=chunk.get("metadata", {}),
        contexte_documentaire=contexte_documentaire,
    )
