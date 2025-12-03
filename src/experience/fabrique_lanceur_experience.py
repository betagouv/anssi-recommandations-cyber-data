from configuration import Configuration
from evaluation.lanceur_deepeval import LanceurExperienceDeepeval
from experience.experience import (
    LanceurExperience,
)
from infra.evaluateur.deep_eval.evaluateur_deepeval_multi_processus import (
    EvaluateurDeepevalMultiProcessus,
)
from journalisation.experience import EntrepotExperience


def fabrique_lanceur_experience(
    configuration: Configuration, entrepot_experience: EntrepotExperience
) -> LanceurExperience:
    return LanceurExperienceDeepeval(
        entrepot_experience,
        EvaluateurDeepevalMultiProcessus(
            nb_processus=configuration.parametres_deepeval.nb_processus_en_parallele_pour_deepeval
        ),
    )
