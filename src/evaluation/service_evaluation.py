import uuid

from adaptateurs.clients_albert import ClientAlbertReformulation
from evaluation.evaluateur_deepeval import EvaluateurDeepeval
from evaluation.evaluation_en_cours import (
    EntrepotEvaluationEnCours,
    EvaluationEnCours,
    EntrepotEvaluationEnCoursMemoire,
)
from evaluation.reformulation.evaluation import (
    QuestionAEvaluer,
    EvaluateurReformulation,
)
from evenement.bus import BusEvenement
from infra.evaluation.evaluateur_deepeval_multi_processus import (
    EvaluateurDeepevalMultiProcessus,
)


class ServiceEvaluation:
    def __init__(self, entrepot_evaluation: EntrepotEvaluationEnCours):
        super().__init__()
        self._entrepot_evaluation = entrepot_evaluation

    def lance_reformulation(
        self,
        client_albert: ClientAlbertReformulation,
        bus_evenement: BusEvenement,
        prompt: str,
        questions: list[QuestionAEvaluer],
        evaluateur: EvaluateurDeepeval = EvaluateurDeepevalMultiProcessus(),
    ):
        evaluation_en_cours = EvaluationEnCours(uuid.uuid4(), len(questions))
        self._entrepot_evaluation.persiste(evaluation_en_cours)
        EvaluateurReformulation(
            client_albert, prompt, evaluateur, bus_evenement
        ).evalue(questions=questions)
        return evaluation_en_cours


def fabrique_service_evaluation() -> ServiceEvaluation:
    return ServiceEvaluation(EntrepotEvaluationEnCoursMemoire())
