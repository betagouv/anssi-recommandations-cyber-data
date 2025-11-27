import os
from pathlib import Path
from typing import Callable, Optional
from unittest.mock import Mock

import pytest

from configuration import (
    Evalap,
    Configuration,
    MQC,
    Albert,
    BaseDeDonnees,
)
from evalap import EvalapClient
from evalap.evalap_dataset_http import DatasetReponse
from evalap.evalap_experience_http import ExperienceReponse, ExperienceAvecResultats
from infra.memoire.ecrivain import EcrivainSortieDeTest
from infra.memoire.evalap import EvalapClientDeTest
from journalisation.experience import (
    EntrepotExperienceMemoire,
    Experience,
    EntrepotExperience,
)
from mqc.ecrivain_sortie import EcrivainSortie


@pytest.fixture
def une_experience() -> dict:
    return {
        "id": 42,
        "name": "Experience Test",
        "created_at": "2025-10-06T15:45:00Z",
        "experiment_status": "running_metrics",
        "experiment_set_id": 1,
        "num_try": 8,
        "num_success": 7,
        "num_observation_try": 40,
        "num_observation_success": 38,
        "num_metrics": 3,
        "readme": "Test readme",
        "judge_model": {"model": "albert"},
        "model": {"name": "albert-large"},
        "dataset": {"id": 10},
        "with_vision": False,
        "results": [
            {
                "created_at": "2025-10-09T14:48:35.428847",
                "experiment_id": 42,
                "id": 125,
                "metric_name": "judge_precision",
                "metric_status": "running",
                "num_success": 0,
                "num_try": 0,
                "observation_table": [
                    {
                        "id": 1001,
                        "created_at": "2025-10-09T14:48:35.428847",
                        "score": 0.8,
                        "observation": "test",
                        "num_line": 0,
                        "error_msg": None,
                        "execution_time": 5,
                    }
                ],
            }
        ],
    }


@pytest.fixture()
def configuration_evalap() -> Evalap:
    return Evalap(url="http://localhost:8000/v1", token_authentification="")


@pytest.fixture()
def configuration() -> Configuration:
    configuration_mqc = MQC(
        port=8002,
        hote="localhost",
        api_prefixe_route="",
        route_pose_question="pose_question",
        delai_attente_maximum=10.0,
    )
    evalap: Evalap = Evalap(
        url="http://localhost:8000",
        token_authentification="",
    )
    albert = Albert(url="https://albert.api.etalab.gouv.fr/v1", cle_api="fausse_cle")
    base_de_donnees = BaseDeDonnees(
        hote=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        utilisateur=os.getenv("DB_USER", "postgres"),
        mot_de_passe=os.getenv("DB_PASSWORD", "postgres"),
        nom="database",
    )
    return Configuration(
        mqc=configuration_mqc,
        evalap=evalap,
        albert=albert,
        base_de_donnees_journal=base_de_donnees,
        frequence_lecture=10.0,
    )


@pytest.fixture()
def cree_fichier_csv_avec_du_contenu(
    tmp_path: Path,
) -> Callable[[str, Optional[Path]], Path]:
    def _fichier_evaluation(contenu: str, chemin: Optional[Path] = None) -> Path:
        if chemin is not None:
            (tmp_path / chemin).mkdir(parents=True, exist_ok=True)
        fichier = tmp_path / "eval.csv"
        fichier.write_text(contenu, encoding="utf-8")
        return fichier

    return _fichier_evaluation


@pytest.fixture()
def reponse_avec_paragraphes() -> dict:
    return {
        "reponse": "Réponse test",
        "paragraphes": [
            {
                "score_similarite": 0.9,
                "numero_page": 5,
                "url": "https://test.com",
                "nom_document": "Doc test",
                "contenu": "Contenu test",
            }
        ],
        "question": "Q1?",
    }


@pytest.fixture
def reponse_a_l_ajout_d_un_dataset():
    return DatasetReponse(
        name="nom_dataset",
        readme="",
        default_metric="",
        columns_map={},
        id=1,
        created_at="2024-01-01",
        size=0,
        columns=[],
        parquet_size=0,
        parquet_columns=[],
    )


@pytest.fixture
def reponse_a_la_creation_d_une_experience():
    return ExperienceReponse(
        id=1,
        name="nom_experience",
        created_at="2024-01-01",
        experiment_status="created",
        experiment_set_id=None,
        num_try=0,
        num_success=0,
        num_observation_try=0,
        num_observation_success=0,
        num_metrics=0,
        readme=None,
        judge_model="",
        model={},
        dataset={"id": 1, "name": "test"},
        with_vision=False,
    )


@pytest.fixture
def reponse_a_la_lecture_d_une_experience():
    return ExperienceAvecResultats(
        id=1,
        name="Experience Test",
        created_at="2024-01-01",
        experiment_status="completed",
        experiment_set_id=None,
        num_try=1,
        num_success=1,
        num_observation_try=1,
        num_observation_success=1,
        num_metrics=1,
        readme=None,
        judge_model={},
        model={},
        dataset={"id": 1, "name": "test"},
        with_vision=False,
        results=[],
    )


@pytest.fixture
def une_experience_evalap(
    reponse_a_l_ajout_d_un_dataset,
    reponse_a_la_creation_d_une_experience,
    reponse_a_la_lecture_d_une_experience,
):
    def _une_experience_evalap(configuration) -> EvalapClient:
        session = Mock()
        client = EvalapClientDeTest(configuration, session=session)
        client.reponse_ajoute_dataset(reponse_a_l_ajout_d_un_dataset)
        client.reponse_cree_experience(reponse_a_la_creation_d_une_experience)
        client.reponse_lit_experience(reponse_a_la_lecture_d_une_experience)
        return client

    return _une_experience_evalap


@pytest.fixture
def resultat_collecte_mqc(tmp_path: Path):
    def _resultat_collecte_mqc() -> tuple[EcrivainSortieDeTest, Path]:
        sortie = tmp_path.joinpath("sortie")
        en_tete = "REF Guide,REF Question,Question type,Tags,REF Réponse,Réponse envisagée,Numéro page (lecteur),Localisation paragraphe,Réponse Bot,Note réponse (/10),Commentaire Note,Contexte,Noms Documents,Numéros Page\n"
        premiere_ligne = "GAUT,GAUT.Q.1,Qu'est-ce que l'authentification ?,Usuelle,GAUT.R.1,réponse envisagée,10,en bas,réponse mqc,nan,Bonne réponse,test,[],[]"
        contenu_fichier_csv_resultat_collecte = en_tete + premiere_ligne
        ecrivain_sortie_de_test = EcrivainSortieDeTest(
            contenu_fichier_csv_resultat_collecte, Path("/tmp"), sortie
        )
        return ecrivain_sortie_de_test, sortie

    return _resultat_collecte_mqc


@pytest.fixture
def resultat_collecte_mqc_avec_deux_resultats() -> EcrivainSortie:
    en_tete = "REF Guide,REF Question,Question type,Tags,REF Réponse,Réponse envisagée,Numéro page (lecteur),Localisation paragraphe,Réponse Bot,Note réponse (/10),Commentaire Note,Contexte,Noms Documents,Numéros Page\n"
    premiere_ligne = "GAUT,GAUT.Q.1,Qu'est-ce que l'authentification ?,Usuelle,GAUT.R.1,réponse envisagée,10,en bas,réponse mqc,nan,Bonne réponse,test,[],[]\n"
    seconde_ligne = "GAUT,GAUT.Q.1,Qu'elle est la bonne longueur d'un mot de passe?,Usuelle,GAUT.R.1,réponse envisagée,10,en bas,réponse mqc,nan,Excellente réponse,test,[],[]"

    contenu_complet = en_tete + premiere_ligne + seconde_ligne
    ecrivain_sortie_de_test = EcrivainSortieDeTest(contenu_complet)
    ecrivain_sortie_de_test.ecris_contenu()

    return ecrivain_sortie_de_test


@pytest.fixture
def resultat_experience() -> EntrepotExperience:
    entrepot_experience = EntrepotExperienceMemoire()
    entrepot_experience.persiste(
        Experience(
            id_experimentation=1,
            metriques=[
                {
                    "numero_ligne": 0,
                    "score_numero_page_en_contexte_4": 0.4,
                    "bon_nom_document_en_contexte_2": 0,
                }
            ],
        )
    )
    return entrepot_experience
