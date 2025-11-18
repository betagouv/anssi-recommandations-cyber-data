from unittest.mock import Mock

import pytest

from evalap.evalap_experience_http import (
    ExperienceAvecResultats,
    MetriqueResultat,
    ObservationResultat,
)
from verificateur_experience_terminee import VerificateurExperienceTerminee


@pytest.fixture
def client_experience_mock():
    return Mock()


@pytest.fixture
def experience_terminee():
    return ExperienceAvecResultats(
        id=42,
        name="Test Experience",
        created_at="2025-01-01T00:00:00Z",
        experiment_status="finished",
        experiment_set_id=1,
        num_try=2,
        num_success=2,
        num_observation_try=2,
        num_observation_success=2,
        num_metrics=1,
        readme="Test",
        judge_model={"name": "albert"},
        model={"name": "test"},
        dataset={"id": 1},
        with_vision=False,
        results=[
            MetriqueResultat(
                created_at="2025-01-01T00:00:00Z",
                experiment_id=42,
                id=1,
                metric_name="judge_precision",
                metric_status="finished",
                num_success=2,
                num_try=2,
                observation_table=[
                    ObservationResultat(
                        id=1001,
                        created_at="2025-01-01T00:00:00Z",
                        score=0.8,
                        observation="test1",
                        num_line=0,
                        error_msg=None,
                        execution_time=5,
                    ),
                    ObservationResultat(
                        id=1002,
                        created_at="2025-01-01T00:00:00Z",
                        score=0.9,
                        observation="test2",
                        num_line=1,
                        error_msg=None,
                        execution_time=3,
                    ),
                ],
            ),
            MetriqueResultat(
                created_at="2025-01-01T00:00:00Z",
                experiment_id=42,
                id=2,
                metric_name="hallucination",
                metric_status="finished",
                num_success=2,
                num_try=2,
                observation_table=[
                    ObservationResultat(
                        id=1003,
                        created_at="2025-01-01T00:00:00Z",
                        score=0.7,
                        observation="test3",
                        num_line=0,
                        error_msg=None,
                        execution_time=2,
                    ),
                    ObservationResultat(
                        id=1004,
                        created_at="2025-01-01T00:00:00Z",
                        score=0.6,
                        observation="test4",
                        num_line=1,
                        error_msg=None,
                        execution_time=4,
                    ),
                ],
            ),
        ],
    )


def test_experience_terminee_retourne_vrai_si_toutes_metriques_finies(
    client_experience_mock, experience_terminee
):
    formateur = VerificateurExperienceTerminee(client_experience_mock)

    assert formateur._experience_terminee(experience_terminee) is True


def test_experience_terminee_retourne_faux_si_au_moins_une_metrique_en_cours(
    client_experience_mock, experience_terminee
):
    experience_en_cours = experience_terminee._replace(
        results=[experience_terminee.results[0]._replace(metric_status="running")]
    )

    formateur = VerificateurExperienceTerminee(client_experience_mock)

    assert formateur._experience_terminee(experience_en_cours) is False


def test_experience_terminee_retourne_faux_si_deux_metriques_en_cours(
    client_experience_mock, experience_terminee
):
    results_en_cours = [
        experience_terminee.results[0]._replace(metric_status="running"),
        experience_terminee.results[1]._replace(metric_status="running"),
    ]
    experience_en_cours = experience_terminee._replace(results=results_en_cours)

    formateur = VerificateurExperienceTerminee(client_experience_mock)

    assert formateur._experience_terminee(experience_en_cours) is False

def test_surveille_experience_flux_gere_timeout(client_experience_mock):
    experience_en_cours = ExperienceAvecResultats(
        id=42,
        name="Test",
        created_at="2025-01-01T00:00:00Z",
        experiment_status="running",
        experiment_set_id=1,
        num_try=1,
        num_success=0,
        num_observation_try=1,
        num_observation_success=0,
        num_metrics=1,
        readme="Test",
        judge_model={"name": "albert"},
        model={"name": "test"},
        dataset={"id": 1},
        with_vision=False,
        results=[
            MetriqueResultat(
                created_at="2025-01-01T00:00:00Z",
                experiment_id=42,
                id=1,
                metric_name="judge_precision",
                metric_status="running",
                num_success=0,
                num_try=1,
                observation_table=[],
            )
        ],
    )

    client_experience_mock.lit.return_value = experience_en_cours
    formateur = VerificateurExperienceTerminee(client_experience_mock)

    resultats = formateur.verifie(42, delai_attente=0.01, timeout_max=0.05)

    assert not resultats
