from unittest.mock import Mock
from requests import Response
from src.client_evalap import ClientEvalap
from src.configuration import Evalap
import pytest
import requests


@pytest.fixture()
def configuration_evalap() -> Evalap:
    return Evalap(url="http://localhost:8000/v1")


def fabrique_reponse(objet_json, status=200):
    r = Mock(spec=Response)
    r.code_status = status
    r.json.return_value = objet_json
    r.raise_for_status = Mock()
    return r


def test_liste_datasets_retourne_la_liste_attendue(configuration_evalap: Evalap):
    session = Mock()
    session.get.return_value = fabrique_reponse(
        [
            {
                "id": 1,
                "name": "ds",
                "readme": "test",
                "default_metric": "judge_precision",
                "columns_map": {},
                "created_at": "2024-01-01",
                "size": 0,
                "columns": [],
                "parquet_size": 0,
                "parquet_columns": [],
            }
        ]
    )

    client = ClientEvalap(configuration_evalap, session=session)
    jeux = client.liste_datasets()

    assert jeux[0].id == 1
    assert jeux[0].name == "ds"
    session.get.assert_called_once_with(
        f"{configuration_evalap.url}/datasets", timeout=20
    )


def test_liste_datasets_timeout_retourne_liste_vide(
    configuration_evalap: Evalap,
):
    session = Mock()
    session.get.side_effect = requests.Timeout("timeout simulé")

    client = ClientEvalap(configuration_evalap, session=session)
    resultat = client.liste_datasets()

    assert resultat == []


def test_liste_datasets_reponse_non_liste_retourne_liste_vide(
    configuration_evalap: Evalap,
):
    session = Mock()
    session.get.return_value = fabrique_reponse({"message": "erreur"})

    client = ClientEvalap(configuration_evalap, session=session)
    resultat = client.liste_datasets()

    assert resultat == []
