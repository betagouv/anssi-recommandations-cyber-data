from typing import cast

from jeopardy.client_albert_jeopardy import ReponseDocumentOrigine
from jeopardy.service import ServiceJeopardyse, ListeDeDocuments, CollectionEntiere


class ServiceJeopardyseDocuments(ServiceJeopardyse):
    def recupere_les_documents(
        self, donnees: CollectionEntiere | ListeDeDocuments, taille_paquet_chunks=10
    ) -> tuple[list[ReponseDocumentOrigine], str]:
        liste_de_documents = cast(ListeDeDocuments, donnees)
        documents_par_noms = self._client_albert.recupere_documents_par_noms(
            liste_de_documents.id_collection, liste_de_documents.noms_documents
        )
        return documents_par_noms, liste_de_documents.id_collection
