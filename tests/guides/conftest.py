from pathlib import Path
from typing import Callable
from unittest.mock import Mock
from requests import Session

import pytest

from guides.indexeur import ReponseDocument


@pytest.fixture
def fichier_pdf(tmp_path) -> Callable[[str], Path]:
    def _cree_fichier_pdf(nom: str) -> Path:
        le_fichier = (tmp_path / nom).with_suffix(".pdf")
        with open(le_fichier, "wb") as f:
            f.write(b"pdf content")
        return le_fichier

    return _cree_fichier_pdf


@pytest.fixture
def dossier_guide_anssi(tmp_path, fichier_pdf) -> Path:
    return fichier_pdf("test.pdf").parent


@pytest.fixture
def mock_post_session_creation_document() -> Callable[[Session, ReponseDocument], None]:
    def _mock(session: Session, reponse_attendue: ReponseDocument) -> None:
        mock_response = Mock()
        mock_response.json.return_value = reponse_attendue._asdict()
        session.post = Mock(return_value=mock_response)  # type: ignore[method-assign]

    return _mock


@pytest.fixture
def une_reponse_document() -> ReponseDocument:
    return ReponseDocument(
        id="doc123",
        name="test.pdf",
        collection_id="12345",
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z",
    )


@pytest.fixture
def une_reponse_document_parametree() -> Callable[[str, str], ReponseDocument]:
    def _une_reponse_document_parametree(
        id_document: str, nom_document: str
    ) -> ReponseDocument:
        return ReponseDocument(
            id=id_document,
            name=nom_document,
            collection_id="12345",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

    return _une_reponse_document_parametree
