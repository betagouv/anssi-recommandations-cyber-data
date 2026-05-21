from adaptateurs.clients_albert import (
    ClientAlbertIndexation,
    ReponseCollection,
    PayloadCollection,
)
from documents.indexeur.indexeur import DocumentAIndexer, ReponseDocument
from infra.logger import log


class ClientAlbertIndexationReel(ClientAlbertIndexation):
    def cree_collection(self, nom: str, description: str) -> ReponseCollection:
        payload = PayloadCollection(name=nom, description=description)
        response = self.executeur_de_requete.poste(
            f"{self.url}/collections", payload._asdict(), None
        )
        if response.status_code != 201:
            print(f"Erreur {response.status_code}: {response.text}")
            raise Exception(f"Erreur création collection: {response.status_code}")
        result = response.json()
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
        documents: list[DocumentAIndexer],
    ) -> list[ReponseDocument]:
        id_collection = self.id_collection
        return self.indexeur.ajoute_documents(documents, id_collection)

    def document_existe(self, nom_document: str, id_collection: str) -> str | None:
        payload_document = {"name": nom_document, "collection_id": id_collection}
        reponse = self.executeur_de_requete.recupere(
            f"{self.url}/documents", payload_document
        )
        if reponse.status_code != 200:
            log(
                __name__,
                f"Erreur {reponse.status_code}: {reponse.text}, pour le document : {nom_document}",
            )
            raise Exception(
                f"Erreur lors de la récupération du document : {reponse.status_code}"
            )
        result = reponse.json()
        return result.get("data")[0]["id"] if len(result.get("data")) > 0 else None

    def supprime_document(self, id_document: str):
        reponse = self.executeur_de_requete.supprime(
            f"{self.url}/documents/{id_document}"
        )
        if reponse.status_code != 204:
            raise Exception(
                f"Erreur lors de la suppression du document : {id_document}, {reponse.json()}"
            )

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
