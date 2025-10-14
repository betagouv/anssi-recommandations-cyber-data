import pytest
from unittest.mock import Mock, patch
import pandas as pd
from formateur_resultats_experiences import (
    FormateurResultatsExperiences,
)
from remplisseur_reponses import EcrivainResultatsFlux
from evalap.evalap_experience_http import (
    ExperienceAvecResultats,
    MetriqueResultat,
    ObservationResultat,
)


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
    formateur = FormateurResultatsExperiences(client_experience_mock)

    assert formateur._experience_terminee(experience_terminee) is True


def test_experience_terminee_retourne_faux_si_au_moins_une_metrique_en_cours(
    client_experience_mock, experience_terminee
):
    experience_en_cours = experience_terminee._replace(
        results=[experience_terminee.results[0]._replace(metric_status="running")]
    )

    formateur = FormateurResultatsExperiences(client_experience_mock)

    assert formateur._experience_terminee(experience_en_cours) is False


def test_experience_terminee_retourne_faux_si_deux_metriques_en_cours(
    client_experience_mock, experience_terminee
):
    results_en_cours = [
        experience_terminee.results[0]._replace(metric_status="running"),
        experience_terminee.results[1]._replace(metric_status="running"),
    ]
    experience_en_cours = experience_terminee._replace(results=results_en_cours)

    formateur = FormateurResultatsExperiences(client_experience_mock)

    assert formateur._experience_terminee(experience_en_cours) is False


def test_convertit_en_dataframe_structure_correcte(
    client_experience_mock, experience_terminee
):
    formateur = FormateurResultatsExperiences(client_experience_mock)

    df = formateur.convertit_en_dataframe(experience_terminee)

    assert len(df) == 4
    assert list(df.columns) == [
        "experiment_id",
        "experiment_name",
        "metric_name",
        "metric_status",
        "numero_ligne",
        "score",
        "observation",
    ]
    assert df.iloc[0]["score"] == 0.8
    assert df.iloc[1]["score"] == 0.9


def test_surveille_experience_flux_retourne_metriques_terminees_une_par_une(
    client_experience_mock, experience_terminee
):
    experience_partielle = experience_terminee._replace(
        results=[
            experience_terminee.results[0],
            experience_terminee.results[1]._replace(metric_status="running"),
        ]
    )

    client_experience_mock.lit.side_effect = [experience_partielle, experience_terminee]

    formateur = FormateurResultatsExperiences(client_experience_mock)

    generateur_de_resultats = formateur.surveille_experience_flux(
        42, delai_attente=0.01, timeout_max=1
    )

    premier_resultat = next(generateur_de_resultats)
    assert premier_resultat[0] == "judge_precision"
    assert len(premier_resultat[1]) == 2

    deuxieme_resultat = next(generateur_de_resultats)
    assert deuxieme_resultat[0] == "hallucination"
    assert len(deuxieme_resultat[1]) == 2


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
    formateur = FormateurResultatsExperiences(client_experience_mock)

    resultats = list(
        formateur.surveille_experience_flux(42, delai_attente=0.01, timeout_max=0.05)
    )

    assert len(resultats) == 0


@pytest.mark.parametrize(
    "fichier_existant,mock_read_csv_config",
    [
        (False, FileNotFoundError()),
        (True, pd.DataFrame({"judge_precision": [0.8, 0.9]}, index=[0, 1])),
    ],
)
def test_ecrivain_resultats_flux_sauvegarde_toujours(
    fichier_existant, mock_read_csv_config
):
    def generateur_resultats():
        yield (
            "judge_precision",
            [{"numero_ligne": 0, "score": 0.8}, {"numero_ligne": 1, "score": 0.9}],
        )

    ecrivain = EcrivainResultatsFlux("/fake/path", "test_experience")

    with patch("pandas.DataFrame.to_csv") as mock_to_csv:
        with patch("pandas.read_csv") as mock_read_csv:
            if fichier_existant:
                mock_read_csv.return_value = mock_read_csv_config
            else:
                mock_read_csv.side_effect = mock_read_csv_config

            ecrivain.ecrit_resultats_flux(generateur_resultats(), 123)

            mock_to_csv.assert_called_once()
