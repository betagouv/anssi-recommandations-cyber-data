from pathlib import Path
from typing import Optional, Union

import pytest
from deepeval.evaluate.types import EvaluationResult, TestResult
from deepeval.metrics import (
    BaseMetric,
)
from deepeval.test_case import LLMTestCase
from deepeval.tracing.api import MetricData

from configuration import MQC
from evaluation.evaluateur_deepeval import EvaluateurDeepeval
from evaluation.mqc.collecte_reponses_mqc import CollecteurDeReponses
from evaluation.mqc.lanceur_deepeval import LanceurEvaluationDeepeval
from evaluation.mqc.remplisseur_reponses import ClientMQCHTTPAsync, ReponseQuestion
from infra.memoire.ecrivain import EcrivainSortieDeTest
from journalisation.evaluation import EntrepotEvaluationMemoire


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
    cas_de_test_executes: list[LLMTestCase] = []
    metriques_deepeval_soumises: list[BaseMetric] = []
    metriques_personnalisees_soumises: list[BaseMetric] = []

    def __init__(self):
        super().__init__()
        self.metriques_personnalisees_soumises = []
        self.nombre_metriques_soumise = 0
        self.metriques_deepeval_soumises = []
        self.cas_de_test_executes = []

    def evaluate(
        self, test_cases: list[LLMTestCase], metrics: Optional[list[BaseMetric]] = None
    ) -> list[EvaluationResult]:
        self.cas_de_test_executes.extend(test_cases)
        if metrics is not None:
            self.metriques_deepeval_soumises.extend(metrics[0:3])
            self.metriques_personnalisees_soumises.extend(metrics[3:])
            self.nombre_metriques_soumise = len(self.metriques_deepeval_soumises) + len(
                self.metriques_personnalisees_soumises
            )

        metriques = self._construis_metriques_de_test()

        results = []
        for test_case in test_cases:
            results.append(
                TestResult(
                    metrics_data=metriques,
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

    def _construis_metriques_de_test(self) -> list[MetricData]:
        scores_par_nom = {
            "bon_nom_document_en_contexte_2": 1,
            "bon_numéro_page_en_contexte_2": 0,
            "score_numéro_page_en_contexte_2": 0.7,
            "hallucination": 0.6,
        }

        metriques = []

        for metrique in self.metriques_personnalisees_soumises:
            nom = metrique.__name__.lower().replace(" ", "_")
            score = scores_par_nom.get(nom, 1)
            metriques.append(
                ConstructeurMetricData.construis(nom=metrique.__name__, score=score)
            )

        for metrique in self.metriques_deepeval_soumises:
            nom = metrique.__name__.lower().replace(" ", "_")
            score = scores_par_nom.get(nom, 0.6)
            metriques.append(
                ConstructeurMetricData.construis(nom=metrique.__name__, score=score)
            )

        return metriques


@pytest.fixture
def evaluateur_de_test_avec_metriques() -> EvaluateurDeepevalTest:
    return EvaluateurDeepevalTest()


class ClientMQCHTTPAsyncDeTest(ClientMQCHTTPAsync):
    def __init__(self):
        super().__init__(
            MQC(
                port=1,
                hote="ici.local",
                api_prefixe_route="/prefixe",
                route_pose_question="/question",
                delai_attente_maximum=1,
            )
        )
        self.reponses_recues = []

    async def pose_question(self, question: str) -> ReponseQuestion:
        return ReponseQuestion(
            reponse="La réponse", paragraphes=[], question="La question"
        )


class CollecteurDeReponsesDeTest(CollecteurDeReponses):
    en_tete = "REF Guide,REF Question,Question type,Tags,REF Réponse,Réponse envisagée,Numéro page (lecteur),Localisation paragraphe,Réponse Bot,Note réponse (/10),Commentaire Note,Contexte,Noms Documents,Numéros Page\n"
    premiere_ligne = "GAUT,GAUT.Q.1,Qu'est-ce que l'authentification ?,Usuelle,GAUT.R.1,réponse envisagée,10,en bas,réponse mqc,nan,Bonne réponse,test,[],[]"

    def __init__(self):
        super().__init__(
            EcrivainSortieDeTest(self.en_tete + self.premiere_ligne),
            ClientMQCHTTPAsyncDeTest(),
            1,
        )
        self.collecteur_de_reponse_appele = False

    async def collecte_reponses(self, chemin_csv: Path):
        self.collecteur_de_reponse_appele = True
        return None

    @property
    def fichier_de_reponses(self) -> Path:
        return self._ecrivain_sortie.fichier_de_reponses


@pytest.fixture
def un_collecteur_de_reponse():
    return CollecteurDeReponsesDeTest()


class LanceurEvaluationDeepevalDeTest(LanceurEvaluationDeepeval):
    def __init__(self):
        super().__init__(EntrepotEvaluationMemoire(), EvaluateurDeepevalTest())

    def lance_l_evaluation(
        self, fichier_csv: Path, mapping_csv: Path
    ) -> int | str | None:
        return None


@pytest.fixture
def un_lanceur_deepeval():
    return LanceurEvaluationDeepevalDeTest()
