from dataclasses import dataclass
from datetime import datetime, timezone
from typing import NamedTuple

from adaptateurs.client_albert_collections_reel import ClientAlbertCollectionsReel
from adaptateurs.clients_albert import ClientAlbertCollections
from configuration import recupere_configuration


@dataclass
class Collection:
    id: str
    nom: str
    description: str
    nombre_documents: int
    date_de_creation: str
    date_de_derniere_modification: str


class InformationsDeCollections(NamedTuple):
    indexee: Collection
    jeopardy: Collection


class OffsetsCollections(NamedTuple):
    indexee: int
    jeopardy: int


class Document(NamedTuple):
    id: str
    nom: str
    date_de_creation: str
    chunks: int


class InformationsDeDocuments(NamedTuple):
    indexee: list[Document]
    jeopardy: list[Document]


class ServiceCollections:
    def __init__(self, client_albert: ClientAlbertCollections):
        super().__init__()
        self.client_albert = client_albert

    def les_collections(self) -> InformationsDeCollections:
        def en_date(date: str) -> str:
            return (
                datetime.fromtimestamp(int(date)).astimezone(timezone.utc).isoformat()
            )

        les_collections = self.client_albert.recupere_collections_mqc()
        collection_indexee = Collection(
            id=les_collections[0].id,
            nom=les_collections[0].name,
            description=les_collections[0].description,
            nombre_documents=les_collections[0].documents,
            date_de_creation=en_date(les_collections[0].created),
            date_de_derniere_modification=en_date(les_collections[0].updated),
        )
        collection_jeopardy = Collection(
            id=les_collections[1].id,
            nom=les_collections[1].name,
            description=les_collections[1].description,
            nombre_documents=les_collections[1].documents,
            date_de_creation=en_date(les_collections[1].created),
            date_de_derniere_modification=en_date(les_collections[1].updated),
        )
        return InformationsDeCollections(
            indexee=collection_indexee, jeopardy=collection_jeopardy
        )

    def les_documents(self, offsets: OffsetsCollections) -> InformationsDeDocuments:
        return InformationsDeDocuments(indexee=[], jeopardy=[])


def fabrique_service_collections() -> ServiceCollections:
    la_configuration = recupere_configuration()
    client = ClientAlbertCollectionsReel(
        la_configuration.albert.url,
        la_configuration.albert.cle_api,
        la_configuration.collections_MQC,
    )
    return ServiceCollections(client)
