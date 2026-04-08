from __future__ import annotations

from configuration import recupere_configuration
from evenement.fabrique_bus_evenements import fabrique_bus_evenements
from infra.executeur_requete import ExecuteurDeRequete
from jeopardy.client_albert_jeopardy import ReponseDocumentOrigine
from jeopardy.client_albert_jeopardy_reel import ClientAlbertJeopardyReel
from jeopardy.questions import EntrepotQuestionGenereeMemoire
from jeopardy.service import ServiceJeopardyse


class ServiceJeopardyseCollectionEntiere(ServiceJeopardyse):
    def recupere_les_documents(
        self,
        nom_collection: str,
        description_collection: str,
        id_collection: str,
        taille_paquet_chunks=10,
    ) -> tuple[list[ReponseDocumentOrigine], str]:
        reponse_creation_collection = self._client_albert.cree_collection(
            f"Jeopardy : {nom_collection}",
            f"Jeopardy : {description_collection}",
        )
        id_collection_jeopardy = reponse_creation_collection.id
        self._logger.info(f"Collection créée avec succès : {id_collection_jeopardy}")

        reponse_documents_collection = (
            self._client_albert.recupere_documents_collection(id_collection)
        )
        return reponse_documents_collection.documents, id_collection_jeopardy


def fabrique_service_jeopardise_collection_entiere() -> (
    ServiceJeopardyseCollectionEntiere
):
    configuration_jeopardy = recupere_configuration().jeopardy
    return ServiceJeopardyseCollectionEntiere(
        ClientAlbertJeopardyReel(configuration_jeopardy, ExecuteurDeRequete()),
        EntrepotQuestionGenereeMemoire(),
        fabrique_bus_evenements(),
    )
