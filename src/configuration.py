import os
from typing_extensions import NamedTuple


class MQC(NamedTuple):
    port: int
    hote: str
    api_prefixe_route: str
    route_pose_question: str


class Evalap(NamedTuple):
    url: str


class Configuration(NamedTuple):
    mqc: MQC
    evalap: Evalap


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

    return Configuration(mqc=configuration_mqc, evalap=evalap)
