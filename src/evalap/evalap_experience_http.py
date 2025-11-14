import requests
import logging
from typing import NamedTuple, Optional, Dict, Union
from configuration import Configuration
from evalap.evalap_base_http import EvalapBaseHTTP


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
    id: int
    created_at: str
    score: Optional[float]
    observation: Optional[str]
    num_line: int
    error_msg: Optional[str]
    execution_time: Optional[int]


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
    def __init__(self, configuration: Configuration, session: requests.Session) -> None:
        super().__init__(configuration, session)

    def cree(self, payload: ExperiencePayload) -> Optional[ExperienceReponse]:
        try:
            donnees = self._post("/experiment", json=payload._asdict(), timeout=20)
            return ExperienceReponse(**donnees)
        except requests.Timeout as e:
            logging.error(f"Timeout lors de la création de l'expérience: {e}")
            return None
        except requests.RequestException as e:
            logging.error(f"Erreur de requête lors de la création de l'expérience: {e}")
            if hasattr(e, "response") and e.response is not None:
                logging.error(f"Code de statut: {e.response.status_code}")
                logging.error(f"Réponse du serveur: {e.response.text}")
        return None

    @staticmethod
    def _observation_depuis(donnees_obs: Dict) -> ObservationResultat:
        return ObservationResultat(
            id=donnees_obs["id"],
            created_at=donnees_obs["created_at"],
            score=donnees_obs.get("score"),
            observation=donnees_obs.get("observation"),
            num_line=donnees_obs["num_line"],
            error_msg=donnees_obs.get("error_msg"),
            execution_time=donnees_obs.get("execution_time"),
        )

    @staticmethod
    def _metrique_depuis(donnees_resultat: Dict) -> MetriqueResultat:
        observations = list(
            map(
                EvalapExperienceHttp._observation_depuis,
                donnees_resultat.get("observation_table", []),
            )
        )
        return MetriqueResultat(
            created_at=donnees_resultat["created_at"],
            experiment_id=donnees_resultat["experiment_id"],
            id=donnees_resultat["id"],
            metric_name=donnees_resultat["metric_name"],
            metric_status=donnees_resultat["metric_status"],
            num_success=donnees_resultat["num_success"],
            num_try=donnees_resultat["num_try"],
            observation_table=observations,
        )

    def lit(self, experiment_id: int) -> Optional[ExperienceAvecResultats]:
        try:
            donnees = self._get(
                f"/experiment/{experiment_id}?with_results=true", timeout=20
            )

            resultats = list(map(self._metrique_depuis, donnees.get("results", [])))

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
        except requests.Timeout as e:
            logging.error(
                f"Timeout lors de la lecture de l'expérience {experiment_id}: {e}"
            )
            return None
        except requests.RequestException as e:
            logging.error(
                f"Erreur de requête lors de la lecture de l'expérience {experiment_id}: {e}"
            )
            return None
