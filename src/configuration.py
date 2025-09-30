import os
from typing_extensions import NamedTuple
from enum import StrEnum, auto

# `mypy` ne comprend pas les classes imbriquées dans des `NamedTuple` (alors que c'est du `Python` valide...);
# _c.f._ https://github.com/python/mypy/issues/15775 .
# mypy: disable-error-code="misc, attr-defined, name-defined"


class Mode(StrEnum):
    DEVELOPPEMENT = auto()
    TEST = auto()
    PRODUCTION = auto()


class MQC(NamedTuple):
    port: int
    hote: str
    prefix_api: str
    route_pose_question: str


class Configuration(NamedTuple):
    mqc: MQC
    mode: Mode


def recupere_configuration() -> Configuration:
    configuration_mqc = MQC(
        port=int(os.getenv("MQC_PORT", "8002")),
        hote=os.getenv("MQC_HOTE", "localhost"),
        prefix_api=os.getenv("MQC_PREFIX_API", ""),
        route_pose_question=os.getenv("MQC_ROUTE_POSE_QUESTION", "pose_question"),
    )
    mode: Mode = Mode(os.getenv("MODE", "production"))

    return Configuration(mqc=configuration_mqc, mode=mode)
