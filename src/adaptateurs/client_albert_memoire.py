from adaptateurs.client_albert import ClientAlbert, ReponseCollection
from guides.indexeur import Indexeur, DocumentPDF, ReponseDocument


class ClientAlbertMemoire(ClientAlbert):
    def __init__(self, url: str, cle_api: str, indexeur: Indexeur):
        super().__init__(url, cle_api, indexeur)
        self.collections_existantes: set[str] = set()
        self.documents_par_collection: dict[str, list[DocumentPDF]] = {}

    def cree_collection(self, nom: str, description: str) -> ReponseCollection:
        collection_id = f"mem-{len(self.collections_existantes)}"
        self.collections_existantes.add(collection_id)
        self.id_collection = collection_id
        return ReponseCollection(
            id=collection_id,
            name=nom,
            description=description,
            visibility="private",
            documents=0,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

    def ajoute_documents(
        self,
        documents: list[DocumentPDF],
    ) -> list[ReponseDocument]:
        if self.id_collection:
            if self.id_collection not in self.documents_par_collection:
                self.documents_par_collection[self.id_collection] = []
            self.documents_par_collection[self.id_collection].extend(documents)
        return []

    def _collection_existe(self, id_collection: str) -> bool:
        return id_collection in self.collections_existantes

    def attribue_collection(self, id_collection: str) -> bool:
        if not self._collection_existe(id_collection):
            return False
        self.id_collection = id_collection
        return True
