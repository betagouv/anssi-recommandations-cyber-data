from pathlib import Path
from typing import Callable, Optional
import httpx
import pytest
from configuration import recupere_configuration, MQC


@pytest.fixture()
def fichier_evaluation(tmp_path: Path) -> Callable[[str, Optional[Path]], Path]:
    def _fichier_evaluation(contenu: str, chemin: Optional[Path] = None) -> Path:
        if chemin is not None:
            (tmp_path / chemin).mkdir(parents=True, exist_ok=True)
        fichier = tmp_path / "eval.csv"
        fichier.write_text(contenu, encoding="utf-8")
        return fichier

    return _fichier_evaluation


@pytest.fixture()
def configuration_mqc() -> MQC:
    return recupere_configuration().mqc


@pytest.fixture()
def reponse_creation_experience() -> Callable[[str, str], httpx.Response]:
    def _cree_reponse_mock(reponse: str, question: str) -> httpx.Response:
        return httpx.Response(
            200, json={"reponse": reponse, "paragraphes": [], "question": question}
        )

    return _cree_reponse_mock
