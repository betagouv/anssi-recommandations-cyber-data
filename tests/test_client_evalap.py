from unittest.mock import Mock
from requests import Response
from src.client_evalap import ClientEvalap, DATASET_REPONSE_VIDE
from src.configuration import Configuration, Mode, Evalap, MQC
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


def test_liste_datasets_timeout_retourne_modele_par_defaut(
    configuration_evalap: Evalap,
):
    session = Mock()
    session.get.side_effect = requests.Timeout("timeout simulé")

    client = ClientEvalap(configuration_evalap, session=session)
    result = client.liste_datasets()

    assert result == [DATASET_REPONSE_VIDE]
