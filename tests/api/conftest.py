import uuid
from pathlib import Path

import pytest
from deepeval.evaluate.types import EvaluationResult
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from fastapi import FastAPI
from typing_extensions import Callable, Dict, Optional

from adaptateurs.client_albert_reformulation_reel import (
    fabrique_client_albert_reformulation,
)
from adaptateurs.clients_albert import ClientAlbertReformulation
from adaptateurs.journal import (
    AdaptateurJournal,
    fabrique_adaptateur_journal,
    AdaptateurJournalMemoire,
)
from documents.docling.multi_processeur import Multiprocesseur
from evaluation.evaluateur_deepeval import EvaluateurDeepeval
from evaluation.evaluation_en_cours import (
    EntrepotEvaluationEnCoursMemoire,
    EvaluationEnCours,
)
from evaluation.reformulation.evaluation import QuestionAEvaluer
from evaluation.service_evaluation import ServiceEvaluation, fabrique_service_evaluation
from evenement.bus import BusEvenement
from evenement.fabrique_bus_evenements import fabrique_bus_evenements
from infra.executeur_requete import fabrique_executeur_de_requete
from infra.memoire.executeur_de_requete_memoire import (
    ExecuteurDeRequeteDeTest,
    ReponseAttendueOK,
    ReponseTexteEnSucces,
    TypeRequete,
)
from jeopardy.client_albert_jeopardy import (
    ClientAlbertJeopardy,
    ReponseCreationCollection,
    RequeteCreationDocumentAlbert,
    ReponseCreationDocument,
    RequeteAjoutChunksDansDocumentAlbert,
    ReponseDocumentsCollectionOrigine,
    ReponseDocumentOrigine,
)
from jeopardy.questions import EntrepotQuestionGenereeMemoire
from jeopardy.service_jeopardyse_collection_entiere import (
    ServiceJeopardyseCollectionEntiere,
    fabrique_service_jeopardise_collection_entiere,
)
from serveur import fabrique_serveur


class MultiProcesseurDeTest(Multiprocesseur):
    def __init__(self):
        self.a_ete_appele = False
        self.resultats = []

    def execute(self, func, iterable) -> list:
        self.a_ete_appele = True
        for chunk in iterable:
            self.resultats.append(func(chunk))
        return self.resultats


class EvaluateurDeepevalTest(EvaluateurDeepeval):
    def evaluate(
        self, test_cases: list[LLMTestCase], metrics: Optional[list[BaseMetric]] = None
    ) -> list[EvaluationResult]:
        return []


class ServiceEvaluationDeTest(ServiceEvaluation):
    def __init__(self):
        super().__init__(EntrepotEvaluationEnCoursMemoire())
        self.prompt_recu = None
        self.evaluation_reformulation_lancee = False
        self.questions_evaluees = []

    def lance_reformulation(
        self,
        client_albert: ClientAlbertReformulation,
        bus_evenement: BusEvenement,
        prompt: str,
        questions: list[QuestionAEvaluer],
        evaluateur: EvaluateurDeepeval = EvaluateurDeepevalTest(),
    ) -> EvaluationEnCours:
        self.evaluation_reformulation_lancee = True
        self.questions_evaluees = questions
        self.prompt_recu = prompt
        return EvaluationEnCours(uuid.uuid4(), len(questions))


class ClientAlbertJeopardyDeTest(ClientAlbertJeopardy):
    def __init__(self):
        super().__init__()
        self._identifiant_de_collection = "collection-test"
        self._identifiant_document = "document-de-test"
        self._reponses_questions_generees = ["question-de-test"]

    def cree_collection(
        self, nom_collection, description_collection
    ) -> ReponseCreationCollection:
        return ReponseCreationCollection(id=self._identifiant_de_collection)

    def cree_document(
        self, identifiant_collection: str, document: RequeteCreationDocumentAlbert
    ) -> ReponseCreationDocument:
        return ReponseCreationDocument(id=self._identifiant_document)

    def genere_questions(self, prompt: str, contenu: str) -> list[str]:
        return self._reponses_questions_generees

    def ajoute_chunks_dans_document(
        self,
        identifiant_collection: str,
        requete: RequeteAjoutChunksDansDocumentAlbert,
    ):
        pass

    def recupere_chunks_document(self, id_document: str) -> list[dict]:
        return []

    def recupere_documents_collection(
        self, identifiant_collection: str
    ) -> ReponseDocumentsCollectionOrigine:
        return ReponseDocumentsCollectionOrigine(
            id=identifiant_collection,
            documents=[
                ReponseDocumentOrigine(
                    id=self._identifiant_document,
                    nom=f"document-{self._identifiant_document}",
                    nombre_chunks=0,
                )
            ],
        )


class ServiceJeopardyseCollectionEntiereDeTest(ServiceJeopardyseCollectionEntiere):
    def __init__(self):
        super().__init__(
            ClientAlbertJeopardyDeTest(),
            EntrepotQuestionGenereeMemoire(),
            "Un prompt",
            MultiProcesseurDeTest(),
        )
        self.description_collection = None
        self.nom_collection = None
        self.identifiant_collection_a_jeopardyser = None
        self.jeopardyse_appele = False
        self.prompt_recu = None
        self.evaluation_reformulation_lancee = False
        self.questions_evaluees = []

    def jeopardyse(
        self,
        nom_collection: str,
        description_collection: str,
        id_collection: str,
        taille_paquet_chunks=10,
    ):
        self.jeopardyse_appele = True
        self.identifiant_collection_a_jeopardyser = id_collection
        self.nom_collection = nom_collection
        self.description_collection = description_collection


class ConstructeurServeur:
    def __init__(
        self,
        max_requetes_par_minute: int = 600,
    ):
        self._max_requetes_par_minute = max_requetes_par_minute
        self._dependances: Dict[Callable, Callable] = {}
        self.pages_statiques: Path = Path()

    def avec_adaptateur_journal(self, adaptateur_journal: AdaptateurJournal):
        self._dependances[fabrique_adaptateur_journal] = lambda: adaptateur_journal
        return self

    def avec_pages_statiques(self, pages_statiques):
        self.pages_statiques = pages_statiques
        return self

    def avec_un_client_albert_reformulation(
        self, client_albert_reformulation: ClientAlbertReformulation
    ):
        self._dependances[fabrique_client_albert_reformulation] = (
            lambda: client_albert_reformulation
        )
        return self

    def avec_un_bus_d_evenement(self, bus_evenement: BusEvenement):
        self._dependances[fabrique_bus_evenements] = lambda: bus_evenement
        return self

    def avec_un_service_evaluation(self, service_evaluation: ServiceEvaluationDeTest):
        self._dependances[fabrique_service_evaluation] = lambda: service_evaluation
        return self

    def avec_un_executeur_de_requete(
        self, executeur_de_requete: ExecuteurDeRequeteDeTest
    ):
        self._dependances[fabrique_executeur_de_requete] = lambda: executeur_de_requete
        return self

    def construis(self):
        self._serveur = fabrique_serveur(
            self._max_requetes_par_minute,
            f"{self.pages_statiques}/ui/dist/",
        )
        for clef, dependance in self._dependances.items():
            self._serveur.dependency_overrides[clef] = dependance
        return self._serveur

    def avec_un_service_jeopardy(
        self, service_jeopardy: ServiceJeopardyseCollectionEntiereDeTest
    ):
        self._dependances[fabrique_service_jeopardise_collection_entiere] = (
            lambda: service_jeopardy
        )
        return self


@pytest.fixture(autouse=True)
def pages_statiques(tmp_path) -> Path:
    def crees_la_page_statique(page: Path):
        page.write_text(
            "<html><body>%%NONCE_A_INJECTER%%</body></html>",
            encoding="utf-8",
        )

    root = tmp_path
    (root / "ui" / "dist" / "assets").mkdir(parents=True, exist_ok=True)
    (root / "ui" / "dist" / "fonts").mkdir(parents=True, exist_ok=True)
    (root / "ui" / "dist" / "icons").mkdir(parents=True, exist_ok=True)
    (root / "ui" / "dist" / "images").mkdir(parents=True, exist_ok=True)

    crees_la_page_statique(root / "ui" / "dist" / "index.html")
    return root


@pytest.fixture()
def un_service_evaluation() -> Callable[[], ServiceEvaluationDeTest]:
    def _un_service_evaluation():
        return ServiceEvaluationDeTest()

    return _un_service_evaluation


@pytest.fixture()
def un_service_jeopardy() -> Callable[[], ServiceJeopardyseCollectionEntiereDeTest]:
    def _un_service_jeopardy():
        return ServiceJeopardyseCollectionEntiereDeTest()

    return _un_service_jeopardy


@pytest.fixture()
def un_serveur_de_test_complet(
    pages_statiques,
    un_client_albert_de_reformulation,
    un_bus_d_evenement,
    un_service_evaluation,
    un_service_jeopardy,
) -> Callable[
    [Optional[ExecuteurDeRequeteDeTest] | None],
    tuple[
        FastAPI,
        AdaptateurJournalMemoire,
        BusEvenement,
        ServiceEvaluationDeTest,
        ServiceJeopardyseCollectionEntiereDeTest,
    ],
]:
    def _un_serveur_de_test_complet(
        executeur_de_requete_de_test: Optional[ExecuteurDeRequeteDeTest] | None = None,
    ):
        adaptateur_journal = AdaptateurJournalMemoire()
        serveur = ConstructeurServeur(
            max_requetes_par_minute=100,  # type: ignore[arg-type]
        ).avec_pages_statiques(pages_statiques)
        serveur = serveur.avec_adaptateur_journal(adaptateur_journal)
        client_albert = un_client_albert_de_reformulation().construis()
        bus_evenement = un_bus_d_evenement
        serveur.avec_un_client_albert_reformulation(client_albert)
        serveur.avec_un_bus_d_evenement(bus_evenement)
        service_evaluation = un_service_evaluation()
        serveur.avec_un_service_evaluation(service_evaluation)
        service_jeopardy = un_service_jeopardy()
        serveur.avec_un_service_jeopardy(service_jeopardy)
        executeur_de_requete = (
            ExecuteurDeRequeteDeTest(
                [ReponseAttendueOK(ReponseTexteEnSucces(texte="OK"), TypeRequete.GET)]
            )
            if executeur_de_requete_de_test is None
            else executeur_de_requete_de_test
        )
        serveur.avec_un_executeur_de_requete(executeur_de_requete)
        return (
            serveur.construis(),
            adaptateur_journal,
            bus_evenement,
            service_evaluation,
            service_jeopardy,
        )

    return _un_serveur_de_test_complet
