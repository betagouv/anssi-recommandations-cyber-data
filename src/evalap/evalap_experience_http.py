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


class ObservationResultat(NamedTuple):
    score: Optional[float]
    observation: Optional[str]


class MetriqueResultat(NamedTuple):
    created_at: str
    experiment_id: int
    id: int
    metric_name: str
    metric_status: str
    num_success: int
    num_try: int
    observation_table: list[ObservationResultat]


class ExperienceAvecResultats(NamedTuple):
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
    judge_model: Optional[Dict[str, Union[str, int, bool, None]]]
    model: Optional[Dict[str, Union[str, int, bool, None]]]
    dataset: Dict[str, Union[str, int, list[str], None]]
    with_vision: bool
    results: list[MetriqueResultat]


class EvalapExperienceHttp(EvalapBaseHTTP):
    def cree(self, payload: ExperiencePayload) -> Optional[ExperienceReponse]:
        try:
            donnees = self._post("/experiment", json=payload._asdict(), timeout=20)
            return ExperienceReponse(**donnees)
        except (requests.Timeout, requests.RequestException):
            return None

    @staticmethod
    def _formate_resultats(donnees_resultats: list[Dict]) -> list[MetriqueResultat]:
        resultats = []
        for resultat in donnees_resultats:
            observations = [
                ObservationResultat(
                    score=obs.get("score"), observation=obs.get("observation")
                )
                for obs in resultat.get("observation_table", [])
            ]
            resultats.append(
                MetriqueResultat(
                    created_at=resultat["created_at"],
                    experiment_id=resultat["experiment_id"],
                    id=resultat["id"],
                    metric_name=resultat["metric_name"],
                    metric_status=resultat["metric_status"],
                    num_success=resultat["num_success"],
                    num_try=resultat["num_try"],
                    observation_table=observations,
                )
            )
        return resultats

    def lit(self, experiment_id: int) -> Optional[ExperienceAvecResultats]:
        try:
            donnees = self._get(
                f"/experiment/{experiment_id}?with_results=true", timeout=20
            )

            resultats = self._formate_resultats(donnees.get("results", []))

            return ExperienceAvecResultats(
                id=donnees["id"],
                name=donnees["name"],
                created_at=donnees["created_at"],
                experiment_status=donnees["experiment_status"],
                experiment_set_id=donnees.get("experiment_set_id"),
                num_try=donnees["num_try"],
                num_success=donnees["num_success"],
                num_observation_try=donnees["num_observation_try"],
                num_observation_success=donnees["num_observation_success"],
                num_metrics=donnees["num_metrics"],
                readme=donnees.get("readme"),
                judge_model=donnees.get("judge_model"),
                model=donnees.get("model"),
                dataset=donnees["dataset"],
                with_vision=donnees.get("with_vision", False),
                results=resultats,
            )
        except (requests.Timeout, requests.RequestException):
            return None
