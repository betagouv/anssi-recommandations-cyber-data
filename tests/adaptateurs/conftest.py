from typing import Any, Callable

import pytest
from requests import Response

from infra.executeur_requete import ExecuteurDeRequete


class ReponseAlbertDeTest(Response):
    def __init__(self, corps: dict[str, Any]):
        super().__init__()
        self._corps = corps

    def json(self, **kwargs: Any) -> dict[str, Any]:
        return self._corps


class ExecuteurAlbertMemoire(ExecuteurDeRequete):
    def __init__(self):
        super().__init__()
        self._pages_de_chunks: list[list[dict[str, Any]]] = []
        self._nombre_de_chunks = 0
        self.requetes_recues: list[tuple[str, dict[str, int] | None]] = []
        self.requetes_de_chunks_recues: list[tuple[str, dict[str, int] | None]] = []

    def avec_les_pages_de_chunks(
        self, pages: list[list[dict[str, Any]]]
    ) -> "ExecuteurAlbertMemoire":
        self._pages_de_chunks = pages
        return self

    def avec_le_nombre_de_chunks(
        self, nombre_de_chunks: int
    ) -> "ExecuteurAlbertMemoire":
        self._nombre_de_chunks = nombre_de_chunks
        return self

    def initialise_connexion_securisee(self, clef_api: str):
        pass

    def recupere(
        self, url: str, parametres: dict[str, int] | None = None
    ) -> ReponseAlbertDeTest:
        self.requetes_recues.append((url, parametres))
        if url.endswith("/chunks"):
            self.requetes_de_chunks_recues.append((url, parametres))
            page = self._pages_de_chunks.pop(0) if self._pages_de_chunks else []
            return ReponseAlbertDeTest({"data": page})
        return ReponseAlbertDeTest({"chunks": self._nombre_de_chunks})


@pytest.fixture
def un_executeur_albert_memoire() -> Callable[[], ExecuteurAlbertMemoire]:
    def _un_executeur_albert_memoire() -> ExecuteurAlbertMemoire:
        return ExecuteurAlbertMemoire()

    return _un_executeur_albert_memoire
