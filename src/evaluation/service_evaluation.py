import uuid
from pathlib import Path

from adaptateurs.clients_albert import ClientAlbertReformulation
from adaptateurs.journal import AdaptateurJournal, fabrique_adaptateur_journal
from evaluation.evaluateur_deepeval import EvaluateurDeepeval
from evaluation.evaluation_en_cours import (
    EntrepotEvaluationEnCours,
    EvaluationEnCours,
    EntrepotEvaluationEnCoursMemoire,
)
from evaluation.mqc.collecte_reponses_mqc import CollecteurDeReponses
from evaluation.mqc.evaluation import LanceurEvaluation
from evaluation.mqc.fabrique_lanceur_evaluation import fabrique_lanceur_evaluation
from evaluation.reformulation.evaluation import (
    QuestionAEvaluer,
    EvaluateurReformulation,
)
from evenement.bus import BusEvenement
from infra.evaluation.evaluateur_deepeval_multi_processus import (
    EvaluateurDeepevalMultiProcessus,
)
from journalisation.consignateur_evaluation import consigne_evaluation
from journalisation.evaluation import EntrepotEvaluation, fabrique_entrepot_evaluation


class ServiceEvaluation:
    def __init__(
        self,
        entrepot_evaluation_en_cours: EntrepotEvaluationEnCours,
        lanceur_deepeval: LanceurEvaluation,
        adaptateur_journal: AdaptateurJournal,
        entrepot_evaluation: EntrepotEvaluation,
    ):
        super().__init__()
        self._entrepot_evaluation_en_cours = entrepot_evaluation_en_cours
        self._lanceur_deepeval = lanceur_deepeval
        self._adaptateur_journal = adaptateur_journal
        self._entrepot_evaluation = entrepot_evaluation

    async def lance_evaluation(
        self,
        fichier_evaluation: Path,
        fichier_mapping: Path,
        collecteur_de_reponse: CollecteurDeReponses,
    ):
        await collecteur_de_reponse.collecte_reponses(fichier_evaluation)
        fichier_csv = collecteur_de_reponse.fichier_de_reponses
        if fichier_csv is not None:
            id_evaluation = self._lanceur_deepeval.lance_l_evaluation(
                fichier_csv, fichier_mapping
            )
            if id_evaluation is not None:
                consigne_evaluation(
                    id_evaluation,
                    self._entrepot_evaluation,
                    self._adaptateur_journal,
                    fichier_csv,  # TODO passer l’entrepot dans le constructeur
                )
            return id_evaluation

    def lance_reformulation(
        self,
        client_albert: ClientAlbertReformulation,
        bus_evenement: BusEvenement,
        prompt: str,
        questions: list[QuestionAEvaluer],
        evaluateur: EvaluateurDeepeval = EvaluateurDeepevalMultiProcessus(),
    ):
        evaluation_en_cours = EvaluationEnCours(uuid.uuid4(), len(questions))
        self._entrepot_evaluation_en_cours.persiste(evaluation_en_cours)
        EvaluateurReformulation(
            client_albert, prompt, evaluateur, bus_evenement
        ).evalue(questions=questions)
        return evaluation_en_cours


def fabrique_service_evaluation() -> ServiceEvaluation:
    entrepot_evaluation = fabrique_entrepot_evaluation()
    lanceur_deepeval = fabrique_lanceur_evaluation(entrepot_evaluation)
    adaptateur_journal = fabrique_adaptateur_journal()
    return ServiceEvaluation(
        EntrepotEvaluationEnCoursMemoire(),
        lanceur_deepeval,
        adaptateur_journal,
        entrepot_evaluation,
    )
