from pathlib import Path
from typing import Callable

import pytest


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
