from unittest.mock import Mock

import pytest

from evalap.evalap_experience_http import (
    ExperienceAvecResultats,
    MetriqueResultat,
    ObservationResultat,
)
from evalap.verificateur_experience_terminee import (
    VerificateurExperienceTerminee,
    ExperienceInconnue,
)


@pytest.fixture
def client_experience_mock():
    return Mock()


@pytest.fixture
def experience_terminee():
    return ExperienceAvecResultats(
        id=42,
        name="Test",
        created_at="2025-01-01T00:00:00Z",
        experiment_status="finished",
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
                metric_status="finished",
                num_success=0,
                num_try=1,
                observation_table=[],
            )
        ],
    )


@pytest.fixture
def experience_en_cours(experience_terminee):
    return ExperienceAvecResultats(
        **{
            **experience_terminee._asdict(),
            "experiment_status": "running",
            "results": [
                MetriqueResultat(
                    **{
                        **experience_terminee.results[0]._asdict(),
                        "metric_status": "running",
                    }
                )
            ],
        }
    )


@pytest.fixture
def experience_avec_plusieurs_metriques_terminees(experience_terminee):
    experience_avec_resultats = ExperienceAvecResultats(
        **{
            **experience_terminee._asdict(),
            "results": [
                MetriqueResultat(
                    **{
                        **experience_terminee.results[0]._asdict(),
                        "observation_table": [
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
                    }
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
        }
    )
    return experience_avec_resultats


def test_verifie_que_toutes_les_metriques_sont_finies(
    client_experience_mock, experience_avec_plusieurs_metriques_terminees
):
    client_experience_mock.lit.return_value = (
        experience_avec_plusieurs_metriques_terminees
    )
    verificateur = VerificateurExperienceTerminee(client_experience_mock)

    assert (
        verificateur.verifie(experience_avec_plusieurs_metriques_terminees.id) is None
    )


def test_verificateur_leve_une_erreur_en_cas_de_timeout(
    client_experience_mock, experience_en_cours
):
    client_experience_mock.lit.return_value = experience_en_cours
    verificateur = VerificateurExperienceTerminee(client_experience_mock)

    with pytest.raises(TimeoutError):
        verificateur.verifie(42, frequence_lecture=0.01, timeout_max=0.05)

    assert client_experience_mock.lit.call_count == 5


def test_verificateur_leve_une_erreur_si_experience_inconnue(client_experience_mock):
    client_experience_mock.lit.return_value = None
    verificateur = VerificateurExperienceTerminee(client_experience_mock)

    with pytest.raises(ExperienceInconnue):
        verificateur.verifie(42, frequence_lecture=0.01, timeout_max=0.05)
