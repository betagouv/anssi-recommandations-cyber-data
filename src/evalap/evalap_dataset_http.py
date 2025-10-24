import requests
from typing import List, NamedTuple, Dict, Optional

from .evalap_base_http import EvalapBaseHTTP


class DatasetReponse(NamedTuple):
    name: str
    readme: str
    default_metric: str
    columns_map: Dict[str, str]
    id: int
    created_at: str
    size: int
    columns: List[str]
    parquet_size: int
    parquet_columns: List[str]


class DatasetPayload(NamedTuple):
    name: str
    readme: str
    default_metric: str
    df: str


class EvalapDatasetHttp(EvalapBaseHTTP):
    def liste(self) -> List[DatasetReponse]:
        try:
            donnees = self._get("/datasets", timeout=20)
            return (
                [DatasetReponse(**d) for d in donnees]
                if isinstance(donnees, list)
                else []
            )
        except (requests.Timeout, requests.RequestException):
            return []

    def ajoute(self, payload: DatasetPayload) -> Optional[DatasetReponse]:
        try:
            donnees = self._post("/dataset", json=payload._asdict(), timeout=20)
            return DatasetReponse(**donnees)
        except requests.HTTPError as e:
            if e.response.status_code == 409:
                datasets_existants = [
                    dataset.name
                    for dataset in self.liste()
                    if dataset.name == payload.name
                ]
                if datasets_existants:
                    raise ValueError(f"Dataset avec ce nom existe déjà: {payload.name}")
            raise
        except (requests.Timeout, requests.RequestException):
            return None
