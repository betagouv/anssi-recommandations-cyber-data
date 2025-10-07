from unittest.mock import Mock
from requests import Response
from src.evalap import EvalapClient
from src.evalap.evalap_dataset_http import (
    DatasetPayload,
    DatasetReponse,
)
from src.configuration import Evalap, Configuration, MQC, Albert
import pytest
import requests
import pandas as pd
from typing import Callable, cast
from src.evalap.evalap_base_http import EvalapBaseHTTP


@pytest.fixture()
def configuration_evalap() -> Evalap:
    return Evalap(url="http://localhost:8000/v1")


@pytest.fixture()
def configuration() -> Configuration:
    configuration_mqc = MQC(
        port=8002,
        hote="localhost",
        api_prefixe_route="",
        route_pose_question="pose_question",
    )
    evalap: Evalap = Evalap(
        url="http://localhost:8000",
    )
    albert = Albert(url="https://albert.api.etalab.gouv.fr/v1", cle_api="fausse_cle")
    return Configuration(mqc=configuration_mqc, evalap=evalap, albert=albert)


@pytest.fixture
def fabrique_reponse() -> Callable[[object, int], Response]:
    def _creer(contenu: object, statut: int = 200) -> Response:
        r = Mock(spec=Response)
        r.status_code = statut
        r.json.return_value = contenu
        r.raise_for_status = Mock()
        return r

    return _creer


@pytest.fixture
def donnees_dataset() -> DatasetReponse:
    return DatasetReponse(
        name="QA",
        readme="JEU QA",
        default_metric="judge_precision",
        columns_map={},
        id=10,
        created_at="2024-01-01",
        size=1,
        columns=[],
        parquet_size=42,
        parquet_columns=[""],
    )


def test_liste_datasets_retourne_la_liste_attendue(
    configuration: Configuration, fabrique_reponse: Mock
):
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

    client = EvalapClient(configuration, session=session)

    jeux = client.dataset.liste()

    assert jeux[0].id == 1
    assert jeux[0].name == "ds"
    session.get.assert_called_once_with(
        f"{configuration.evalap.url}/datasets", timeout=20
    )


def test_liste_datasets_timeout_retourne_liste_vide(
    configuration: Configuration,
):
    session = Mock()
    session.get.side_effect = requests.Timeout("timeout simulé")

    client = EvalapClient(configuration, session=session)
    resultat = client.dataset.liste()
    assert resultat == []


def test_liste_datasets_reponse_non_liste_retourne_liste_vide(
    configuration: Configuration, fabrique_reponse: Mock
):
    session = Mock()
    session.get.return_value = fabrique_reponse({"message": "erreur"})

    client = EvalapClient(configuration, session=session)
    resultat = client.dataset.liste()

    assert resultat == []


def test_ajoute_dataset_retourne_resultat_attendu(
    configuration: Configuration,
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

    df = pd.DataFrame([{"query": "Q", "output": "A", "output_true": "A"}])

    payload: DatasetPayload = DatasetPayload(
        name="QA",
        readme="JEU QA",
        default_metric="judge_precision",
        df=df.astype(object).where(pd.notnull(df), None).to_json(),
    )

    client = EvalapClient(configuration, session=session)
    resultat_ajoute_dataset = client.dataset.ajoute(payload)

    assert resultat_ajoute_dataset is not None
    assert resultat_ajoute_dataset.id == reponse_dict["id"]
    assert resultat_ajoute_dataset.name == reponse_dict["name"]
    session.post.assert_called_once()


def test_ajoute_dataset_timeout_retourne_modele_par_defaut(
    configuration: Configuration,
):
    session = Mock()
    session.post.side_effect = requests.Timeout("timeout simulé")

    df = pd.DataFrame([{"query": "Q", "output": "A", "output_true": "A"}])

    payload = DatasetPayload(
        name="QA",
        readme="JEU QA",
        default_metric="judge_precision",
        df=df.astype(object).where(pd.notnull(df), None).to_json(),
    )

    client = EvalapClient(configuration, session=session)
    resultat = client.dataset.ajoute(payload)

    assert resultat == None


def test_facade_propage_session_aux_datasets(
    donnees_dataset: DatasetReponse,
    fabrique_reponse: Mock,
    configuration: Configuration,
) -> None:
    session = Mock(spec=requests.Session)
    session.post.return_value = fabrique_reponse(donnees_dataset._asdict())

    client = EvalapClient(configuration, session=cast(requests.Session, session))

    assert client.dataset.session is session

    _ = client.dataset.ajoute(
        DatasetPayload(name="QA", readme="", default_metric="m", df="{}")
    )

    session.post.assert_called_once_with(
        "http://localhost:8000/dataset",
        json={"name": "QA", "readme": "", "default_metric": "m", "df": "{}"},
        timeout=20,
    )


def test_base_http_get_post_appellent_session(configuration: Configuration) -> None:
    def _ok(json_obj: object) -> Response:
        r = Mock(spec=Response)
        r.json.return_value = json_obj
        r.raise_for_status = Mock()
        return r

    s = Mock(spec=requests.Session)
    s.get.return_value = _ok({"ok": 1})
    s.post.return_value = _ok({"ok": 2})

    b = EvalapBaseHTTP(configuration, s)
    assert b._get("/ping", timeout=1) == {"ok": 1}
    assert b._post("/dataset", json={"x": 1}, timeout=2) == {"ok": 2}
    s.get.assert_called_once()
    s.post.assert_called_once()
