import os

import pytest
from configuration import (
    Evalap,
    Configuration,
    MQC,
    Albert,
    BaseDeDonnees,
)


@pytest.fixture
def une_experience() -> dict:
    return {
        "id": 42,
        "name": "Experience Test",
        "created_at": "2025-10-06T15:45:00Z",
        "experiment_status": "running_metrics",
        "experiment_set_id": 1,
        "num_try": 8,
        "num_success": 7,
        "num_observation_try": 40,
        "num_observation_success": 38,
        "num_metrics": 3,
        "readme": "Test readme",
        "judge_model": {"model": "albert"},
        "model": {"name": "albert-large"},
        "dataset": {"id": 10},
        "with_vision": False,
        "results": [
            {
                "created_at": "2025-10-09T14:48:35.428847",
                "experiment_id": 42,
                "id": 125,
                "metric_name": "judge_precision",
                "metric_status": "running",
                "num_success": 0,
                "num_try": 0,
                "observation_table": [
                    {
                        "id": 1001,
                        "created_at": "2025-10-09T14:48:35.428847",
                        "score": 0.8,
                        "observation": "test",
                        "num_line": 0,
                        "error_msg": None,
                        "execution_time": 5,
                    }
                ],
            }
        ],
    }


@pytest.fixture()
def configuration_evalap() -> Evalap:
    return Evalap(url="http://localhost:8000/v1", token_authentification="")


@pytest.fixture()
def configuration() -> Configuration:
    configuration_mqc = MQC(
        port=8002,
        hote="localhost",
        api_prefixe_route="",
        route_pose_question="pose_question",
        delai_attente_maximum=10.0,
    )
    evalap: Evalap = Evalap(
        url="http://localhost:8000",
        token_authentification="",
    )
    albert = Albert(url="https://albert.api.etalab.gouv.fr/v1", cle_api="fausse_cle")
    base_de_donnees = BaseDeDonnees(
        hote=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        utilisateur=os.getenv("DB_USER", "postgres"),
        mot_de_passe=os.getenv("DB_PASSWORD", "postgres"),
        nom="database",
    )
    return Configuration(
        mqc=configuration_mqc,
        evalap=evalap,
        albert=albert,
        base_de_donnees_journal=base_de_donnees,
    )
