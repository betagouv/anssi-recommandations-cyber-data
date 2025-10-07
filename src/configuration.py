import os
from typing_extensions import NamedTuple


class MQC(NamedTuple):
    port: int
    hote: str
    api_prefixe_route: str
    route_pose_question: str


class Evalap(NamedTuple):
    url: str


class Albert(NamedTuple):
    url: str
    cle_api: str


class Configuration(NamedTuple):
    mqc: MQC
    evalap: Evalap
    albert: Albert


def recupere_configuration() -> Configuration:
    configuration_mqc = MQC(
        port=int(os.getenv("MQC_PORT", "8002")),
        hote=os.getenv("MQC_HOTE", "localhost"),
        api_prefixe_route=os.getenv("MQC_API_PREFIXE_ROUTE", ""),
        route_pose_question=os.getenv("MQC_ROUTE_POSE_QUESTION", "pose_question"),
    )

    evalap: Evalap = Evalap(
        url=os.getenv("EVALAP_URL", "http://localhost:8000/v1"),
    )

    albert: Albert = Albert(
        url=os.getenv("ALBERT_URL", "https://albert.api.etalab.gouv.fr/v1"),
        cle_api=os.getenv("ALBERT_CLE_API", "cle_api"),
    )

    return Configuration(mqc=configuration_mqc, evalap=evalap, albert=albert)
