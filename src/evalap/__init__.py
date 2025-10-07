from src.evalap.evalap_dataset_http import EvalapDatasetHttp
from src.evalap.evalap_base_http import EvalapBaseHTTP
import requests
from src.configuration import Configuration


class EvalapClient:
    def __init__(
        self,
        configuration: Configuration,
        session: requests.Session,
    ):
        self.dataset = EvalapDatasetHttp(configuration, session)
