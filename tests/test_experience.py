import typing
from unittest.mock import Mock
from requests import Response
from configuration import Configuration
from evalap import EvalapClient
from journalisation.experience import EntrepotExperienceHttp, Experience
from test_client_evalap import DONNEES_JSON


def test_peut_lire_une_experience(
    configuration: Configuration,
):
    session = Mock()

    donnees_json: dict = DONNEES_JSON
    donnees_json["results"].append(
        {
            "created_at": "2025-10-09T14:48:35.428847",
            "experiment_id": 42,
            "id": 125,
            "metric_name": "autre_metrique",
            "metric_status": "running",
            "num_success": 0,
            "num_try": 0,
            "observation_table": [
                {
                    "id": 1002,
                    "created_at": "2025-10-09T14:48:35.428847",
                    "score": 0.4,
                    "observation": "test",
                    "num_line": 0,
                    "error_msg": None,
                    "execution_time": 5,
                }
            ],
        },
    )

    reponse_mockee = Mock(spec=Response)
    reponse_mockee.status_code = 200
    reponse_mockee.json.return_value = donnees_json
    reponse_mockee.raise_for_status = Mock()
    session.get.return_value = reponse_mockee

    client = EvalapClient(configuration, session=session)

    experience_http = EntrepotExperienceHttp(client.experience)
    experience_lue = typing.cast(Experience, experience_http.lit(42))
    assert experience_lue.id_experimentation == 42
    assert experience_lue.metriques == [
        {
            "numero_ligne": 0,
            "judge_precision": 0.8,
            "autre_metrique": 0.4,
        }
    ]
