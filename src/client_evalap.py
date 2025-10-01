from __future__ import annotations
import requests
from src.configuration import Evalap
from typing import NamedTuple, Dict, List


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


class ClientEvalap:
    def __init__(self, configuration_evalap: Evalap, session: requests.Session) -> None:
        self.evalap_url = configuration_evalap.url
        self.session: requests.Session = session

    def liste_datasets(self) -> List[DatasetReponse]:
        try:
            r: requests.Response = self.session.get(
                f"{self.evalap_url}/datasets", timeout=20
            )
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list):
                return [DatasetReponse(**d) for d in data]
            return []
        except (requests.Timeout, requests.RequestException):
            return []
