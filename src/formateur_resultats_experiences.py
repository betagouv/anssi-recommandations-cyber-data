import pandas as pd
import time
import logging
from collections import defaultdict
from typing import Optional, Dict, Tuple, Any, DefaultDict
from src.evalap.evalap_experience_http import (
    ExperienceAvecResultats,
    EvalapExperienceHttp,
)


class FormateurResultatsExperiences:
    def __init__(self, client_experience: EvalapExperienceHttp):
        self.client_experience = client_experience

    @staticmethod
    def _experience_terminee(experience: ExperienceAvecResultats) -> bool:
        return all(
            metrique.metric_status != "running" for metrique in experience.results
        )

    def attend_fin_experience(
        self, experiment_id: int, delai_attente: int = 10, timeout_max: int = 1000
    ) -> Optional[ExperienceAvecResultats]:
        temps_ecoule = 0

        while temps_ecoule < timeout_max:
            experience = self.client_experience.lit(experiment_id)

            if experience is None:
                logging.error(f"Impossible de récupérer l'expérience {experiment_id}")
                return None

            if self._experience_terminee(experience):
                logging.info(f"Expérience {experiment_id} terminée")
                return experience

            logging.info(
                f"Expérience {experiment_id} en cours, attente {delai_attente}s..."
            )
            time.sleep(delai_attente)
            temps_ecoule += delai_attente

        logging.warning(f"Timeout atteint pour l'expérience {experiment_id}")
        return None

    @staticmethod
    def _ligne_depuis_observation_avec_contexte(args) -> dict:
        experience_id, experience_name, metrique, idx, observation = args
        return {
            "experiment_id": experience_id,
            "experiment_name": experience_name,
            "metric_name": metrique.metric_name,
            "metric_status": metrique.metric_status,
            "numero_ligne": idx,
            "score": observation.score,
            "observation": observation.observation,
        }

    def convertit_en_dataframe(
        self, experience: ExperienceAvecResultats
    ) -> pd.DataFrame:
        observations_avec_contexte = [
            (experience.id, experience.name, metrique, idx, observation)
            for metrique in experience.results
            for idx, observation in enumerate(metrique.observation_table)
        ]

        donnees = list(
            map(
                self._ligne_depuis_observation_avec_contexte, observations_avec_contexte
            )
        )
        return pd.DataFrame(donnees)

    def cree_dataframe_formate(
        self, experience: ExperienceAvecResultats
    ) -> pd.DataFrame:
        observations_dict = self._construit_dictionnaire_observations(experience)
        observations_df = pd.DataFrame(list(observations_dict.values()))
        return observations_df

    def _construit_dictionnaire_observations(
        self, experience: ExperienceAvecResultats
    ) -> Dict[Tuple[str, int], Dict[str, Any]]:
        nom_modele = f"Experience_{experience.id}"
        observations_dict: DefaultDict[Tuple[str, int], Dict[str, Any]] = defaultdict(
            lambda: {"model": nom_modele, "numero_ligne": 0}
        )

        for metrique in experience.results:
            for idx, obs in enumerate(metrique.observation_table):
                cle = (nom_modele, idx)
                observations_dict[cle]["numero_ligne"] = idx
                observations_dict[cle][metrique.metric_name] = obs.score

        return dict(observations_dict)
