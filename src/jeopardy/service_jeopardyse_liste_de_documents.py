from typing import cast

from configuration import recupere_configuration
from evenement.fabrique_bus_evenements import fabrique_bus_evenements
from infra.executeur_requete import ExecuteurDeRequete
from jeopardy.client_albert_jeopardy import ReponseDocumentOrigine
from jeopardy.client_albert_jeopardy_reel import ClientAlbertJeopardyReel
from jeopardy.questions import EntrepotQuestionGenereeMemoire
from jeopardy.service import ServiceJeopardyse, ListeDeDocuments, CollectionEntiere


class ServiceJeopardyseDocuments(ServiceJeopardyse):
    def recupere_les_documents(
        self, donnees: CollectionEntiere | ListeDeDocuments, taille_paquet_chunks=10
    ) -> tuple[list[ReponseDocumentOrigine], str]:
        liste_de_documents = cast(ListeDeDocuments, donnees)
        documents_par_noms = self._client_albert.recupere_documents_par_noms(
            liste_de_documents.id_collection_mqc, liste_de_documents.noms_documents
        )
        return documents_par_noms, liste_de_documents.id_collection_jeopardy


def fabrique_service_jeopardise_documents() -> ServiceJeopardyseDocuments:
    configuration_jeopardy = recupere_configuration().jeopardy
    return ServiceJeopardyseDocuments(
        ClientAlbertJeopardyReel(configuration_jeopardy, ExecuteurDeRequete()),
        EntrepotQuestionGenereeMemoire(),
        fabrique_bus_evenements(),
    )
