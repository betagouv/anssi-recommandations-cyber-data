from configuration import Configuration
from evaluation.mqc.evaluation import LanceurEvaluation
from evaluation.mqc.lanceur_deepeval import LanceurEvaluationDeepeval
from infra.evaluation.evaluateur_deepeval_multi_processus import (
    EvaluateurDeepevalMultiProcessus,
)
from journalisation.evaluation import EntrepotEvaluation


def fabrique_lanceur_evaluation(
    configuration: Configuration, entrepot_evaluation: EntrepotEvaluation
) -> LanceurEvaluation:
    return LanceurEvaluationDeepeval(
        entrepot_evaluation,
        EvaluateurDeepevalMultiProcessus(
            nb_processus=configuration.parametres_deepeval.nb_processus_en_parallele_pour_deepeval
        ),
    )
