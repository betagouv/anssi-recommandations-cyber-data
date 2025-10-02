from src.evalap.evalap_dataset_http import EvalapDatasetHttp
from src.evalap.evalap_base_http import EvalapBaseHTTP
import requests
from src.configuration import Evalap


class EvalapClient:
    def __init__(self, configuration_evalap: Evalap, session: requests.Session):
        self.dataset = EvalapDatasetHttp(configuration_evalap, session)
