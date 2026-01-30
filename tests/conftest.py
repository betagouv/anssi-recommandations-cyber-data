import os
from pathlib import Path
from typing import Callable, Optional, Union
from unittest.mock import Mock

import pytest
from deepeval.evaluate.types import EvaluationResult, TestResult
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from deepeval.tracing.api import MetricData
from requests import Response

from adaptateurs.client_albert import ReponseCollectionAlbert
from configuration import (
    Configuration,
    MQC,
    MSC,
    Albert,
    BaseDeDonnees,
    IndexeurDocument,
)
from configuration import ParametresEvaluation
from evaluation.lanceur_deepeval import EvaluateurDeepeval
from guides.executeur_requete import ExecuteurDeRequete
from guides.indexeur import (
    ReponseDocument,
    ReponseDocumentEnSucces,
    ReponseDocumentEnErreur,
)
from infra.memoire.ecrivain import EcrivainSortieDeTest
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
                "metric_name": "hallucination",
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
def configuration() -> Configuration:
    configuration_mqc = MQC(
        port=8002,
        hote="localhost",
        api_prefixe_route="",
        route_pose_question="pose_question",
        delai_attente_maximum=10.0,
    )

    albert = Albert(
        url="https://albert.api.etalab.gouv.fr/v1",
        cle_api="fausse_cle",
        indexeur=IndexeurDocument.INDEXEUR_ALBERT,
        modele="albert-de-test",
    )
    base_de_donnees = BaseDeDonnees(
        hote=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        utilisateur=os.getenv("DB_USER", "postgres"),
        mot_de_passe=os.getenv("DB_PASSWORD", "postgres"),
        nom="database",
    )
    parametres_deepeval = ParametresEvaluation(
        taille_de_lot_collecte_mqc=10, nb_processus_en_parallele_pour_deepeval=4
    )
    return Configuration(
        mqc=configuration_mqc,
        albert=albert,
        base_de_donnees_journal=base_de_donnees,
        parametres_deepeval=parametres_deepeval,
        msc=MSC(url="http://msc.local", chemin_guides="/guides"),
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


class ConstructeurMetricData:
    @staticmethod
    def construis(nom: str, score: Union[float, int]) -> MetricData:
        return MetricData(
            name=nom,
            score=score,
            evaluationCost=0,
            success=True,
            threshold=0.5,
            strictMode=False,
            evaluationModel="gpt-4.1",
            verboseLogs=None,
        )


class EvaluateurDeepevalTest(EvaluateurDeepeval):
    def __init__(self):
        super().__init__()

    def evaluate(
        self, test_cases: list[LLMTestCase], metrics: Optional[list[BaseMetric]] = None
    ) -> list[EvaluationResult]:
        results = []
        for test_case in test_cases:
            results.append(
                TestResult(
                    metrics_data=[
                        ConstructeurMetricData.construis(
                            nom="Une métrique",
                            score=1,
                        ),
                    ],
                    name="",
                    success=True,
                    conversational=False,
                    additional_metadata=test_case.additional_metadata,
                )
            )
        return [
            EvaluationResult(
                test_results=results, confident_link=None, test_run_id=None
            )
        ]


@pytest.fixture
def evaluateur_de_test() -> EvaluateurDeepevalTest:
    return EvaluateurDeepevalTest()


class ReponseAttendueAbstraite:
    def __init__(self, reponse: ReponseDocument):
        super().__init__()
        self.reponse_document = reponse


class ReponseAttendueOK(ReponseAttendueAbstraite):
    def __init__(self, reponse: ReponseDocumentEnSucces):
        super().__init__(reponse)

    @property
    def status_code(self) -> int:
        return 201

    @property
    def reponse(self) -> dict:
        return self.reponse_document._asdict()


class ReponseAttendueKO(ReponseAttendueAbstraite):
    def __init__(
        self, reponse: ReponseDocumentEnErreur, leve_une_erreur: str | None = None
    ):
        super().__init__(reponse)
        self.leve_une_erreur = leve_une_erreur

    @property
    def status_code(self) -> int:
        return 400

    @property
    def reponse(self) -> dict:
        if self.leve_une_erreur is not None:
            raise RuntimeError(self.leve_une_erreur)
        return self.reponse_document._asdict()


class ReponseCreationCollectionOK:
    def __init__(self, reponse: ReponseCollectionAlbert):
        super().__init__()
        self.reponse_collection = reponse

    @property
    def status_code(self) -> int:
        return 201

    @property
    def reponse(self) -> dict:
        return self.reponse_collection._asdict()


class ReponseRecuperationCollectionOK:
    def __init__(self, reponse: ReponseCollectionAlbert):
        super().__init__()
        self.reponse_collection = reponse

    @property
    def status_code(self) -> int:
        return 200

    @property
    def reponse(self) -> dict:
        return self.reponse_collection._asdict()


class ReponseRecuperationCollectionKO:
    def __init__(self):
        super().__init__()

    @property
    def status_code(self) -> int:
        return 404

    @property
    def reponse(self) -> dict:
        return {"message": "La collection n’existe pas"}


ReponseAttendue = Union[
    ReponseAttendueOK,
    ReponseAttendueKO,
    ReponseCreationCollectionOK,
    ReponseRecuperationCollectionOK,
    ReponseRecuperationCollectionKO,
]


class ExecuteurDeRequeteDeTest(ExecuteurDeRequete):
    def __init__(self, reponse_attendue: list[ReponseAttendue]):
        super().__init__()
        self.reponse_attendue = reponse_attendue
        self.payload_recu: None | dict = None
        self.fichiers_recus: None | dict = None
        self.index_courant = 0

    def initialise(self, clef_api: str):
        pass

    def poste(self, url: str, payload: dict, fichiers: Optional[dict]) -> Response:
        reponse = Mock()
        reponse.status_code = self.reponse_attendue[self.index_courant].status_code
        reponse.json.return_value = self.reponse_attendue[self.index_courant].reponse
        self.fichiers_recus = fichiers
        self.payload_recu = payload
        self.index_courant += 1
        return reponse

    def recupere(self, url):
        reponse = Mock()
        reponse.status_code = self.reponse_attendue[self.index_courant].status_code
        reponse.json.return_value = self.reponse_attendue[self.index_courant].reponse
        self.index_courant += 1
        return reponse


@pytest.fixture
def un_executeur_de_requete() -> Callable[[list[ReponseAttendue]], ExecuteurDeRequete]:
    def _un_executeur_de_requete(
        reponse_attendue: list[ReponseAttendue],
    ) -> ExecuteurDeRequete:
        return ExecuteurDeRequeteDeTest(reponse_attendue)

    return _un_executeur_de_requete


@pytest.fixture
def une_reponse_attendue_OK() -> Callable[[ReponseDocumentEnSucces], ReponseAttendueOK]:
    def _une_reponse_document(
        reponse_document: ReponseDocumentEnSucces,
    ) -> ReponseAttendueOK:
        return ReponseAttendueOK(reponse_document)

    return _une_reponse_document


@pytest.fixture
def une_reponse_attendue_KO() -> Callable[[ReponseDocumentEnErreur], ReponseAttendueKO]:
    def _une_reponse_document(
        reponse_document: ReponseDocumentEnErreur,
    ) -> ReponseAttendueKO:
        return ReponseAttendueKO(reponse_document)

    return _une_reponse_document


@pytest.fixture
def une_reponse_de_creation_de_collection_OK() -> Callable[
    [ReponseCollectionAlbert], ReponseCreationCollectionOK
]:
    def _une_reponse_de_creation_de_collection(
        reponse_collection: ReponseCollectionAlbert,
    ) -> ReponseCreationCollectionOK:
        return ReponseCreationCollectionOK(reponse_collection)

    return _une_reponse_de_creation_de_collection


@pytest.fixture
def une_reponse_de_recuperation_de_collection_OK() -> Callable[
    [ReponseCollectionAlbert], ReponseRecuperationCollectionOK
]:
    def _une_reponse_de_recuperation_de_collection(
        reponse_collection: ReponseCollectionAlbert,
    ) -> ReponseRecuperationCollectionOK:
        return ReponseRecuperationCollectionOK(reponse_collection)

    return _une_reponse_de_recuperation_de_collection


@pytest.fixture
def une_reponse_de_recuperation_de_collection_KO() -> ReponseRecuperationCollectionKO:
    return ReponseRecuperationCollectionKO()
