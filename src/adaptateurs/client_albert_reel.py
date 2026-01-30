from adaptateurs.client_albert import ClientAlbert, PayloadCollection, ReponseCollection
from guides.indexeur import DocumentPDF, ReponseDocument


class ClientAlbertReel(ClientAlbert):
    def cree_collection(self, nom: str, description: str) -> ReponseCollection:
        payload = PayloadCollection(name=nom, description=description)
        response = self.executeur_de_requete.poste(
            f"{self.url}/collections", payload._asdict(), None
        )
        if response.status_code != 201:
            print(f"Erreur {response.status_code}: {response.text}")
            raise Exception(f"Erreur création collection: {response.status_code}")
        result = response.json()
        print(f"Réponse API: {result}")
        self.id_collection = result["id"]
        return ReponseCollection(
            id=result["id"],
            name=result.get("name", nom),
            description=result.get("description", description),
            visibility=result.get("visibility", "private"),
            documents=result.get("documents", 0),
            created_at=result.get("created_at", ""),
            updated_at=result.get("updated_at", ""),
        )

    def ajoute_documents(
        self,
        documents: list[DocumentPDF],
    ) -> list[ReponseDocument]:
        id_collection = self.id_collection
        return self.indexeur.ajoute_documents(documents, id_collection)

    def _collection_existe(self, id_collection: str) -> bool:
        response = self.executeur_de_requete.recupere(
            f"{self.url}/collections/{id_collection}"
        )
        return response.status_code == 200

    def attribue_collection(self, id_collection: str) -> bool:
        if not self._collection_existe(id_collection):
            return False
        self.id_collection = id_collection
        return True
