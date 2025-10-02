import requests
from typing import List, NamedTuple, Dict
from src.evalap.evalap_base_http import EvalapBaseHTTP


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


DATASET_REPONSE_VIDE = DatasetReponse(
    name="",
    readme="",
    default_metric="",
    columns_map={},
    id=-1,
    created_at="",
    size=0,
    columns=[],
    parquet_size=0,
    parquet_columns=[],
)


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
                else [DATASET_REPONSE_VIDE]
            )
        except (requests.Timeout, requests.RequestException):
            return [DATASET_REPONSE_VIDE]

    def ajoute(self, payload: DatasetPayload) -> DatasetReponse:
        try:
            donnees = self._post("/dataset", json=payload._asdict(), timeout=20)
            return DatasetReponse(**donnees)
        except (requests.Timeout, requests.RequestException):
            return DATASET_REPONSE_VIDE
