import requests

from configuration import Configuration
from evalap import EvalapClient
from evaluation.lanceur_deepeval import LanceurExperienceDeepeval
from experience.experience import (
    LanceurExperience,
    LanceurExperienceEvalap,
    LanceurExperienceMemoire,
)
from infra.evaluateur.deep_eval.evaluateur_deepeval_multi_processus import (
    EvaluateurDeepevalMultiProcessus,
)
from journalisation.experience import EntrepotExperience


def fabrique_lanceur_experience(
    configuration: Configuration, entrepot_experience: EntrepotExperience
) -> LanceurExperience:
    if configuration.est_evaluation_deepeval:
        return LanceurExperienceDeepeval(
            entrepot_experience,
            EvaluateurDeepevalMultiProcessus(
                nb_processus=configuration.parametres_deepeval.nb_processus_en_parallele_pour_deepeval
            ),
        )
    if configuration.mqc is not None:
        session = requests.session()
        client_evalap = EvalapClient(configuration, session)
        return LanceurExperienceEvalap(client_evalap, configuration)
    return LanceurExperienceMemoire()
