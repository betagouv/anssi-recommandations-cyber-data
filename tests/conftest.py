import os
from pathlib import Path
from typing import Callable, Optional, Union

import pytest
from deepeval.evaluate.types import EvaluationResult, TestResult
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from deepeval.tracing.api import MetricData

from adaptateurs.clients_albert import (
    ReponseCollectionAlbert,
    ClientAlbertReformulation,
)
from configuration import (
    Configuration,
    MQC,
    MSC,
    Albert,
    BaseDeDonnees,
    IndexeurDocument,
    MQCData,
)
from configuration import ParametresEvaluation
from documents.indexeur.indexeur import (
    ReponseDocumentEnSucces,
    ReponseDocumentEnErreur,
    ReponseChunkEnSucces,
    ReponseChunkEnErreur,
)
from evaluation.evaluateur_deepeval import EvaluateurDeepeval
from evenement.bus import BusEvenement, Evenement
from infra.ecrivain_sortie import EcrivainSortie
from infra.memoire.ecrivain import EcrivainSortieDeTest
from infra.memoire.executeur_de_requete_memoire import (
    ExecuteurDeRequeteDeTest,
    ReponseAttendueOK,
    ReponseAttendueKO,
    ReponseCreationCollectionOK,
    ReponseRecuperationCollectionOK,
    ReponseRecuperationCollectionKO,
    ReponseAttendue,
    ReponseTexteEnSucces,
    TypeRequete,
    ReponseTexteEnErreur,
)
from journalisation.evaluation import (
    EntrepotEvaluation,
    EntrepotEvaluationMemoire,
    Evaluation,
)


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
        mqc_data=MQCData(max_requetes_par_minute=10, hote="mqc.local", port=5672),
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
def resultat_evaluation() -> EntrepotEvaluation:
    entrepot_evaluation = EntrepotEvaluationMemoire()
    entrepot_evaluation.persiste(
        Evaluation(
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
    return entrepot_evaluation


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
def evaluateur_de_test_simple() -> EvaluateurDeepevalTest:
    return EvaluateurDeepevalTest()


@pytest.fixture
def un_executeur_de_requete() -> Callable[
    [list[ReponseAttendue]], ExecuteurDeRequeteDeTest
]:
    def _un_executeur_de_requete(
        reponse_attendue: list[ReponseAttendue],
    ) -> ExecuteurDeRequeteDeTest:
        return ExecuteurDeRequeteDeTest(reponse_attendue)

    return _un_executeur_de_requete


@pytest.fixture
def une_reponse_attendue_OK() -> Callable[
    [
        ReponseDocumentEnSucces | ReponseChunkEnSucces | ReponseTexteEnSucces,
        TypeRequete,
    ],
    ReponseAttendueOK,
]:
    def _une_reponse_OK(
        reponse_ok: ReponseDocumentEnSucces
        | ReponseChunkEnSucces
        | ReponseTexteEnSucces,
        type_requete: TypeRequete = TypeRequete.POST,
    ) -> ReponseAttendueOK:
        return ReponseAttendueOK(reponse_ok, type_requete)

    return _une_reponse_OK


@pytest.fixture
def une_reponse_attendue_KO() -> Callable[
    [
        ReponseDocumentEnErreur | ReponseChunkEnErreur | ReponseTexteEnErreur,
        Optional[str],
        TypeRequete,
    ],
    ReponseAttendueKO,
]:
    def _une_reponse_document(
        reponse_document: ReponseDocumentEnErreur
        | ReponseChunkEnErreur
        | ReponseTexteEnErreur,
        leve_une_erreur: Optional[str] = None,
        type_requete: TypeRequete = TypeRequete.POST,
    ) -> ReponseAttendueKO:
        return ReponseAttendueKO(reponse_document, leve_une_erreur, type_requete)

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


class ClientAlbertReformulationDeTest(ClientAlbertReformulation):
    def __init__(self, reformulations: list[dict[str, str]]):
        super().__init__()
        self._reformulations = reformulations
        self.prompt_fourni = ""

    def reformule_la_question(self, prompt: str, question) -> str:
        self.prompt_fourni = prompt
        return list(filter(lambda q: q["question"] == question, self._reformulations))[
            0
        ]["question_reformulee"]


class ConstructeurClientAlbertReformulation:
    def __init__(self):
        super().__init__()
        self.reformulations = []

    def construis(self) -> ClientAlbertReformulationDeTest:
        return ClientAlbertReformulationDeTest(self.reformulations)

    def retourne_la_reformulation_pour_la_question(
        self, question_reformulee: str, question: str
    ):
        self.reformulations.append(
            {"question": question, "question_reformulee": question_reformulee}
        )
        return self


@pytest.fixture
def un_client_albert_de_reformulation() -> Callable[
    [], ConstructeurClientAlbertReformulation
]:
    def _un_client_albert() -> ConstructeurClientAlbertReformulation:
        return ConstructeurClientAlbertReformulation()

    return _un_client_albert


class BusEvenementDeTest(BusEvenement):
    def __init__(self):
        super().__init__([])
        self.evenements = []

    def publie(self, evenement: Evenement):
        self.evenements.append(evenement)
        super().publie(evenement)


@pytest.fixture
def un_bus_d_evenement() -> BusEvenementDeTest:
    return BusEvenementDeTest()
