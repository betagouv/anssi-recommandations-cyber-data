from adaptateurs.clients_albert import ClientAlbertCollections, ReponseCollection


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
