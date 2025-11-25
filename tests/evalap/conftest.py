import pytest
from evalap.evalap_dataset_http import DatasetReponse
from evalap.evalap_experience_http import ExperienceReponse, ExperienceAvecResultats


@pytest.fixture
def reponse_a_l_ajout_d_un_dataset():
    return DatasetReponse(
        name="nom_dataset",
        readme="",
        default_metric="",
        columns_map={},
        id=1,
        created_at="2024-01-01",
        size=0,
        columns=[],
        parquet_size=0,
        parquet_columns=[],
    )


@pytest.fixture
def reponse_a_la_creation_d_une_experience():
    return ExperienceReponse(
        id=1,
        name="nom_experience",
        created_at="2024-01-01",
        experiment_status="created",
        experiment_set_id=None,
        num_try=0,
        num_success=0,
        num_observation_try=0,
        num_observation_success=0,
        num_metrics=0,
        readme=None,
        judge_model="",
        model={},
        dataset={"id": 1, "name": "test"},
        with_vision=False,
    )


@pytest.fixture
def reponse_a_la_lecture_d_une_experience():
    return ExperienceAvecResultats(
        id=1,
        name="Experience Test",
        created_at="2024-01-01",
        experiment_status="completed",
        experiment_set_id=None,
        num_try=1,
        num_success=1,
        num_observation_try=1,
        num_observation_success=1,
        num_metrics=1,
        readme=None,
        judge_model={},
        model={},
        dataset={"id": 1, "name": "test"},
        with_vision=False,
        results=[],
    )
