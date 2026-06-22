from adaptateurs.clients_albert import (
    ClientAlbertCollections,
    ReponseCollection,
    ReponseDocuments,
    ReponseDocumentCollection,
)


class ClientAlbertCollectionsReel(ClientAlbertCollections):
    def recupere_collections_mqc(self) -> list[ReponseCollection]:
        reponse_collection_indexee = self.executeur_de_requete.recupere(
            f"{self.url}/collections/{self.collections_mqc.id_collection_indexee}"
        )
        reponse_collection_jeopardy = self.executeur_de_requete.recupere(
            f"{self.url}/collections/{self.collections_mqc.id_collection_jeopardy}"
        )
        collection_indexee = self._en_reponse_collection(
            reponse_collection_indexee.json()
        )
        collection_jeopardy = self._en_reponse_collection(
            reponse_collection_jeopardy.json()
        )
        return [collection_indexee, collection_jeopardy]

    def recupere_documents_collection(
        self, offset_indexation: int, offset_jeopardy: int
    ) -> ReponseDocuments:
        def liste_documents_dans_collection(collection_id: str, offset: int):
            resultats = []

            for offset in range(0, offset, 100):
                params = {
                    "collection_id": collection_id,
                    "limit": 100,
                    "offset": offset,
                }
                response = self.executeur_de_requete.recupere(
                    f"{self.url}/documents", params
                )
                les_documents = response.json()["data"]
                resultats.extend(
                    list(
                        map(
                            lambda doc: ReponseDocumentCollection(
                                id=doc["id"],
                                name=doc["name"],
                                created=doc["created"],
                                chunks=doc["chunks"],
                            ),
                            les_documents,
                        )
                    )
                )
            return resultats

        documents_indexes = liste_documents_dans_collection(
            self.collections_mqc.id_collection_indexee, offset_indexation
        )
        documents_jeopardy = liste_documents_dans_collection(
            self.collections_mqc.id_collection_jeopardy, offset_jeopardy
        )
        return ReponseDocuments(indexee=documents_indexes, jeopardy=documents_jeopardy)

    def _en_reponse_collection(self, donnees_collection_indexee) -> ReponseCollection:
        return ReponseCollection(
            id=donnees_collection_indexee["id"],
            name=donnees_collection_indexee["name"],
            description=donnees_collection_indexee["description"],
            visibility=donnees_collection_indexee["visibility"],
            documents=donnees_collection_indexee["documents"],
            created=donnees_collection_indexee["created"],
            updated=donnees_collection_indexee["updated"],
        )
