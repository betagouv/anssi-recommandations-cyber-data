from configuration import Configuration
from evaluation.deepeval.evaluation import LanceurEvaluation
from evaluation.deepeval.lanceur_deepeval import LanceurEvaluationDeepeval
from infra.evaluateur.deep_eval.evaluateur_deepeval_multi_processus import (
    EvaluateurDeepevalMultiProcessus,
)
from journalisation.experience import EntrepotExperience


def fabrique_lanceur_evaluation(
    configuration: Configuration, entrepot_experience: EntrepotExperience
) -> LanceurEvaluation:
    return LanceurEvaluationDeepeval(
        entrepot_experience,
        EvaluateurDeepevalMultiProcessus(
            nb_processus=configuration.parametres_deepeval.nb_processus_en_parallele_pour_deepeval
        ),
    )
