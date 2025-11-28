from typing import Optional, cast

import requests

from configuration import Configuration
from evalap import EvalapDatasetHttp, EvalapExperienceHttp, EvalapClient
from evalap.evalap_dataset_http import DatasetReponse, DatasetPayload
from evalap.evalap_experience_http import (
    ExperienceReponse,
    ExperienceAvecResultats,
    ExperiencePayload,
)


class EvalapDatasetDeTest(EvalapDatasetHttp):
    def __init__(self, configuration: Configuration, session: requests.Session):
        super().__init__(configuration, session)
        self.dataset_reponse: None | DatasetReponse = None

    def ajoute(self, payload: DatasetPayload) -> Optional[DatasetReponse]:
        return self.dataset_reponse


class EvalapExperienceDeTest(EvalapExperienceHttp):
    def __init__(self, configuration: Configuration, session: requests.Session):
        super().__init__(configuration, session)
        self.experience_reponse: None | ExperienceReponse = None
        self.experience_avec_resultats: None | ExperienceAvecResultats = None

    def cree(self, payload: ExperiencePayload) -> Optional[ExperienceReponse]:
        return self.experience_reponse

    def lit(self, experiment_id: int | str) -> Optional[ExperienceAvecResultats]:
        return self.experience_avec_resultats


class EvalapClientDeTest(EvalapClient):
    def __init__(self, configuration: Configuration, session: requests.Session):
        super().__init__(configuration, session)
        self.dataset = EvalapDatasetDeTest(configuration, session)
        self.experience = EvalapExperienceDeTest(configuration, session)

    def reponse_ajoute_dataset(self, dataset_reponse: DatasetReponse):
        cast(EvalapDatasetDeTest, self.dataset).dataset_reponse = dataset_reponse

    def reponse_cree_experience(self, experience_reponse: ExperienceReponse):
        cast(
            EvalapExperienceDeTest, self.experience
        ).experience_reponse = experience_reponse

    def reponse_lit_experience(self, experience_avec_resultats):
        cast(
            EvalapExperienceDeTest, self.experience
        ).experience_avec_resultats = experience_avec_resultats
