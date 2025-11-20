from typing import Callable
import httpx
import pytest
from configuration import recupere_configuration, MQC


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
