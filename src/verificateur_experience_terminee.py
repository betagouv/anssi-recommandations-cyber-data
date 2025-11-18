import time
import logging
from typing import Dict, Tuple, Union, Iterator
from evalap.evalap_experience_http import (
    ExperienceAvecResultats,
    EvalapExperienceHttp,
)

ResultatMetrique = list[Dict[str, Union[int, float, None]]]
GenerateurMetriques = Iterator[Tuple[str, ResultatMetrique]]


class VerificateurExperienceTerminee:
    def __init__(self, client_experience: EvalapExperienceHttp):
        self.client_experience = client_experience

    @staticmethod
    def _experience_terminee(experience: ExperienceAvecResultats) -> bool:
        return all(
            metrique.metric_status != "running" for metrique in experience.results
        )

    def verifie(
        self, experiment_id: int, delai_attente: float = 10.0, timeout_max: int = 1000
    ) -> bool:
        temps_ecoule = 0.0

        while temps_ecoule < timeout_max:
            experience = self.client_experience.lit(experiment_id)

            if experience is None:
                logging.error(f"Impossible de récupérer l'expérience {experiment_id}")
                return False

            if self._experience_terminee(experience):
                logging.info(f"Expérience {experiment_id} terminée")
                return True

            logging.info(
                f"Expérience {experiment_id} en cours, attente {delai_attente}s..."
            )
            time.sleep(delai_attente)
            temps_ecoule += delai_attente

        logging.warning(f"Timeout atteint pour l'expérience {experiment_id}")
        return False
