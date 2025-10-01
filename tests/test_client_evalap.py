from unittest.mock import Mock
from requests import Response
from src.client_evalap import ClientEvalap, DatasetPayload
from src.configuration import Configuration, Evalap, MQC
import pytest
import requests
import pandas as pd


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


def test_ajoute_dataset_retourne_resultat_attendu(
    configuration_evalap: Evalap,
):
    session = Mock()
    reponse_dict = {
        "id": 10,
        "name": "QA",
        "readme": "JEU QA",
        "default_metric": "judge_precision",
        "size": 1,
        "created_at": "2024-01-01",
        "parquet_size": 42,
        "parquet_columns": [""],
        "columns_map": {},
        "columns": [],
    }
    reponse_mockee = Mock(spec=Response)
    reponse_mockee.status_code = 200
    reponse_mockee.json.return_value = reponse_dict
    reponse_mockee.raise_for_status = Mock()
    session.post.return_value = reponse_mockee

    client = ClientEvalap(configuration_evalap, session=session)
    df = pd.DataFrame([{"query": "Q", "output": "A", "output_true": "A"}])

    payload: DatasetPayload = DatasetPayload(
        name="QA",
        readme="JEU QA",
        default_metric="judge_precision",
        df=df.astype(object).where(pd.notnull(df), None).to_json(),
    )
    resultat_ajoute_dataset = client.ajoute_dataset(payload)

    assert resultat_ajoute_dataset is not None
    assert resultat_ajoute_dataset.id == reponse_dict["id"]
    assert resultat_ajoute_dataset.name == reponse_dict["name"]
    session.post.assert_called_once()


def test_ajoute_dataset_timeout_retourne_modele_par_defaut(configuration_evalap):
    session = Mock()
    session.post.side_effect = requests.Timeout("timeout simulé")

    client = ClientEvalap(configuration_evalap, session=session)
    df = pd.DataFrame([{"query": "Q", "output": "A", "output_true": "A"}])

    payload = DatasetPayload(
        name="QA",
        readme="JEU QA",
        default_metric="judge_precision",
        df=df.astype(object).where(pd.notnull(df), None).to_json(),
    )

    resultat = client.ajoute_dataset(payload)

    assert resultat == None
