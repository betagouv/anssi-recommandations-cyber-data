import uuid
from pathlib import Path
from typing import cast

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
from configuration import MQC
from documents.docling.multi_processeur import Multiprocesseur
from evaluation.evaluateur_deepeval import EvaluateurDeepeval
from evaluation.evaluation_en_cours import (
    EntrepotEvaluationEnCoursMemoire,
    EvaluationEnCours,
)
from evaluation.mqc.collecte_reponses_mqc import (
    CollecteurDeReponses,
    fabrique_collecteur_de_reponses,
)
from evaluation.mqc.lanceur_deepeval import LanceurEvaluationDeepeval
from evaluation.mqc.remplisseur_reponses import ClientMQCHTTPAsync, ReponseQuestion
from evaluation.reformulation.evaluation import QuestionAEvaluer
from evaluation.service_evaluation import ServiceEvaluation, fabrique_service_evaluation
from evenement.bus import BusEvenement
from evenement.fabrique_bus_evenements import fabrique_bus_evenements
from infra.executeur_requete import fabrique_executeur_de_requete
from infra.memoire.ecrivain import EcrivainSortieDeTest
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
from jeopardy.service import CollectionEntiere, ListeDeDocuments
from jeopardy.service_jeopardyse_collection_entiere import (
    ServiceJeopardyseCollectionEntiere,
    fabrique_service_jeopardise_collection_entiere,
)
from jeopardy.service_jeopardyse_liste_de_documents import (
    ServiceJeopardyseDocuments,
    fabrique_service_jeopardise_documents,
)
from journalisation.evaluation import EntrepotEvaluationMemoire
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


class CollecteurDeReponsesDeTest(CollecteurDeReponses):
    def __init__(self):
        super().__init__(EcrivainSortieDeTest(""), ClientMQCHTTPAsyncDeTest(), 1)
        self.collecteur_de_reponse_appele = False

    async def collecte_reponses(self, chemin_csv: Path):
        self.collecteur_de_reponse_appele = True
        return None


class LanceurEvaluationDeepevalDeTest(LanceurEvaluationDeepeval):
    def __init__(self):
        super().__init__(EntrepotEvaluationMemoire(), EvaluateurDeepevalTest())

    def lance_l_evaluation(
        self, fichier_csv: Path, mapping_csv: Path
    ) -> int | str | None:
        return None


class ServiceEvaluationDeTest(ServiceEvaluation):
    def __init__(self):
        super().__init__(
            EntrepotEvaluationEnCoursMemoire(),
            LanceurEvaluationDeepevalDeTest(),
            AdaptateurJournalMemoire(),
            EntrepotEvaluationMemoire(),
        )
        self.evaluation_lancee = False
        self.chemin_fichier_evaluation = None
        self.chemin_fichier_mapping = None
        self.prompt_recu = None
        self.evaluation_reformulation_lancee = False
        self.questions_evaluees = []
        self._collecteur_de_reponse: CollecteurDeReponsesDeTest = None

    async def lance_evaluation(
        self,
        fichier_evaluation: Path,
        fichier_mapping: Path,
        collecteur_de_reponse: CollecteurDeReponses,
    ):
        self.evaluation_lancee = True
        self.chemin_fichier_evaluation = fichier_evaluation
        self.chemin_fichier_mapping = fichier_mapping
        self._collecteur_de_reponse = cast(
            CollecteurDeReponsesDeTest, collecteur_de_reponse
        )
        await collecteur_de_reponse.collecte_reponses(fichier_evaluation)
        return None

    @property
    def collecteur_de_reponse_appele(self):
        return self._collecteur_de_reponse.collecteur_de_reponse_appele

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

    def recupere_documents_par_noms(
        self, id_collection: str, noms_documents: list[str]
    ) -> list[ReponseDocumentOrigine]:
        return []


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
        donnees: CollectionEntiere | ListeDeDocuments,
        taille_paquet_chunks=10,
    ):
        collection_entiere = cast(CollectionEntiere, donnees)
        self.jeopardyse_appele = True
        self.identifiant_collection_a_jeopardyser = collection_entiere.id_collection
        self.nom_collection = collection_entiere.nom_collection
        self.description_collection = collection_entiere.description_collection


class ServiceJeopardyseDocumentsDeTest(ServiceJeopardyseDocuments):
    def __init__(self):
        super().__init__(
            ClientAlbertJeopardyDeTest(),
            EntrepotQuestionGenereeMemoire(),
            None,
            "Un prompt",
            MultiProcesseurDeTest(),
        )
        self.jeopardyse_documents_appele = False
        self.identifiant_collection_jeopardy = None
        self.noms_documents_a_jeopardyser = []
        self.identifiant_collection_a_jeopardyser = None

    def jeopardyse(
        self,
        donnees: CollectionEntiere | ListeDeDocuments,
        taille_paquet_chunks: int = 10,
    ):
        liste_de_documents = cast(ListeDeDocuments, donnees)
        self.jeopardyse_documents_appele = True
        self.identifiant_collection_jeopardy = liste_de_documents.id_collection_jeopardy
        self.noms_documents_a_jeopardyser = liste_de_documents.noms_documents
        self.identifiant_collection_a_jeopardyser = liste_de_documents.id_collection_mqc


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

    def avec_un_service_jeopardy_de_collection_entiere(
        self, service_jeopardy: ServiceJeopardyseCollectionEntiereDeTest
    ):
        self._dependances[fabrique_service_jeopardise_collection_entiere] = (
            lambda: service_jeopardy
        )
        return self

    def avec_un_service_jeopardy_de_documents(
        self, service_jeopardy_de_documents: ServiceJeopardyseDocumentsDeTest
    ):
        self._dependances[fabrique_service_jeopardise_documents] = (
            lambda: service_jeopardy_de_documents
        )
        return self

    def avec_un_collecteur_de_reponses(
        self, collecteur_de_reponses: CollecteurDeReponsesDeTest
    ):
        self._dependances[fabrique_collecteur_de_reponses] = (
            lambda: collecteur_de_reponses
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
def un_service_jeopardy_de_collection_entiere() -> Callable[
    [], ServiceJeopardyseCollectionEntiereDeTest
]:
    def _un_service_jeopardy():
        return ServiceJeopardyseCollectionEntiereDeTest()

    return _un_service_jeopardy


@pytest.fixture()
def un_service_jeopardy_de_documents() -> Callable[
    [], ServiceJeopardyseDocumentsDeTest
]:
    def _un_service_jeopardy():
        return ServiceJeopardyseDocumentsDeTest()

    return _un_service_jeopardy


@pytest.fixture()
def un_serveur_de_test_complet(
    pages_statiques,
    un_client_albert_de_reformulation,
    un_bus_d_evenement,
    un_service_evaluation,
    un_service_jeopardy_de_collection_entiere,
    un_service_jeopardy_de_documents,
) -> Callable[
    [Optional[ExecuteurDeRequeteDeTest] | None],
    tuple[
        FastAPI,
        AdaptateurJournalMemoire,
        BusEvenement,
        ServiceEvaluationDeTest,
        ServiceJeopardyseCollectionEntiereDeTest,
        ServiceJeopardyseDocumentsDeTest,
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
        service_jeopardy_de_collection_entiere = (
            un_service_jeopardy_de_collection_entiere()
        )
        serveur.avec_un_service_jeopardy_de_collection_entiere(
            service_jeopardy_de_collection_entiere
        )
        service_jeopardy_de_documents = un_service_jeopardy_de_documents()
        serveur.avec_un_service_jeopardy_de_documents(service_jeopardy_de_documents)
        executeur_de_requete = (
            ExecuteurDeRequeteDeTest(
                [ReponseAttendueOK(ReponseTexteEnSucces(texte="OK"), TypeRequete.GET)]
            )
            if executeur_de_requete_de_test is None
            else executeur_de_requete_de_test
        )
        serveur.avec_un_executeur_de_requete(executeur_de_requete)
        collecteur_de_reponses = CollecteurDeReponsesDeTest()
        serveur.avec_un_collecteur_de_reponses(collecteur_de_reponses)
        return (
            serveur.construis(),
            adaptateur_journal,
            bus_evenement,
            service_evaluation,
            service_jeopardy_de_collection_entiere,
            service_jeopardy_de_documents,
        )

    return _un_serveur_de_test_complet
