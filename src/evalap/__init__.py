from evalap.evalap_dataset_http import EvalapDatasetHttp
from evalap.evalap_experience_http import EvalapExperienceHttp
import requests
from configuration import Configuration


class EvalapClient:
    def __init__(
        self,
        configuration: Configuration,
        session: requests.Session,
    ):
        self.dataset = EvalapDatasetHttp(configuration, session)
        self.experience = EvalapExperienceHttp(configuration, session)
