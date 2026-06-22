from dataclasses import dataclass


@dataclass
class Collection:
    id: str
    nom: str
    description: str
    nombre_documents: int
    date_de_creation: str
    date_de_derniere_modification: str


class ServiceCollections:
    def les_collections(self) -> list[Collection]:
        return []


def fabrique_service_collections() -> ServiceCollections:
    return ServiceCollections()
