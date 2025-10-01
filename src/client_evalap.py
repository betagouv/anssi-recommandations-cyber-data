from __future__ import annotations
from typing import List
import requests
from src.configuration import Evalap
from src.evalap_modele import DatasetReponse, DATASET_REPONSE_VIDE


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
            return [DATASET_REPONSE_VIDE]
        except (requests.Timeout, requests.RequestException):
            return [DATASET_REPONSE_VIDE]
