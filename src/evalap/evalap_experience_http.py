import requests
from typing import NamedTuple, Optional, Dict, Union
from src.evalap.evalap_base_http import EvalapBaseHTTP


class ExperienceReponse(NamedTuple):
    id: int
    name: str
    created_at: str
    experiment_status: str
    experiment_set_id: Optional[int]
    num_try: int
    num_success: int
    num_observation_try: int
    num_observation_success: int
    num_metrics: int
    readme: Optional[str]
    judge_model: Dict[str, Union[str, int, bool, None]]
    model: Dict[str, Union[str, int, bool, None]]
    dataset: Dict[str, Union[str, int, list[str], None]]
    with_vision: bool


class ExperiencePayload(NamedTuple):
    name: str
    metrics: list[str]
    dataset: str
    model: Dict[str, Union[str, list[str]]] | None
    judge_model: Dict[str, str]


class EvalapExperienceHttp(EvalapBaseHTTP):
    def cree(self, payload: ExperiencePayload) -> Optional[ExperienceReponse]:
        try:
            donnees = self._post("/experiment", json=payload._asdict(), timeout=20)
            return ExperienceReponse(**donnees)
        except (requests.Timeout, requests.RequestException):
            return None
