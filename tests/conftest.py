import os
import pytest
from configuration import (
    Evalap,
    Configuration,
    MQC,
    Albert,
    BaseDeDonnees,
    recupere_configuration,
)


@pytest.fixture()
def configuration_evalap() -> Evalap:
    return Evalap(url="http://localhost:8000/v1", token_authentification="")


@pytest.fixture()
def configuration_mqc() -> MQC:
    return recupere_configuration().mqc


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
