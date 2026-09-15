from abc import ABC, abstractmethod
from typing import Any, NamedTuple


class ReponseChunkAlbert(NamedTuple):
    id: str
    contenu: str
    metadonnees: dict[str, Any]


class ClientAlbertChunks(ABC):
    @abstractmethod
    def recupere_les_chunks_du_document(
        self, id_document: str
    ) -> list[ReponseChunkAlbert]:
        pass
