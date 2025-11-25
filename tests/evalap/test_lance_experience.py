from pathlib import Path
from typing import Optional
from unittest.mock import Mock

import requests
from typing import cast
from configuration import Configuration
from evalap import EvalapClient, EvalapDatasetHttp, EvalapExperienceHttp
from evalap.evalap_dataset_http import DatasetPayload, DatasetReponse
from evalap.evalap_experience_http import (
    ExperiencePayload,
    ExperienceReponse,
    ExperienceAvecResultats,
)
from evalap.lance_experience import lance_experience


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

    def lit(self, experiment_id: int) -> Optional[ExperienceAvecResultats]:
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


def test_lance_experience(
    configuration,
    cree_fichier_csv_avec_du_contenu,
    tmp_path: Path,
    reponse_a_l_ajout_d_un_dataset,
    reponse_a_la_creation_d_une_experience,
    reponse_a_la_lecture_d_une_experience,
):
    session = Mock()
    client = EvalapClientDeTest(configuration, session=session)
    client.reponse_ajoute_dataset(reponse_a_l_ajout_d_un_dataset)
    client.reponse_cree_experience(reponse_a_la_creation_d_une_experience)
    client.reponse_lit_experience(reponse_a_la_lecture_d_une_experience)
    fichier_csv = cree_fichier_csv_avec_du_contenu(
        "REF Guide,REF Question,Que stion type,Tags,REF Réponse,Réponse envisagée,Numéro page (lecteur),Localisation paragraphe,Réponse Bot,Note réponse (/10),Commentaire Note,Contexte,Noms Documents,Numéros Page\nGAUT,GAUT.Q.1,Qu'est-ce que l'authentification ?,Usuelle,GAUT.R.1,réponse envisagée,10,en bas,réponse mqc,nan,Bonne réponse,test,[],[]",
        tmp_path,
    )

    experience_id_cree = lance_experience(
        client, configuration, 1, "nom_experience", fichier_csv
    )

    assert experience_id_cree == 1
