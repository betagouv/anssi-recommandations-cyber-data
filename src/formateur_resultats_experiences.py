import pandas as pd
import time
import logging
from collections import defaultdict
from typing import Dict, Tuple, Any, DefaultDict, Iterator, List, Union
from datetime import datetime
from pathlib import Path
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

    def surveille_experience_flux(
        self, experiment_id: int, delai_attente: float = 10.0, timeout_max: int = 1000
    ) -> Iterator[Tuple[str, List[Dict[str, Union[int, float, None]]]]]:
        temps_ecoule = 0.0
        metriques_terminees = set()

        while temps_ecoule < timeout_max:
            experience = self.client_experience.lit(experiment_id)

            if experience is None:
                logging.error(f"Impossible de récupérer l'expérience {experiment_id}")
                return

            for metrique in experience.results:
                if (
                    metrique.metric_status != "running"
                    and metrique.metric_name not in metriques_terminees
                ):
                    metriques_terminees.add(metrique.metric_name)
                    observations = [
                        {"numero_ligne": obs.num_line, "score": obs.score}
                        for obs in metrique.observation_table
                    ]
                    yield metrique.metric_name, observations

            if self._experience_terminee(experience):
                logging.info(f"Expérience {experiment_id} terminée")
                return

            logging.info(
                f"Expérience {experiment_id} en cours, attente {delai_attente}s..."
            )
            time.sleep(delai_attente)
            temps_ecoule += delai_attente

        logging.warning(f"Timeout atteint pour l'expérience {experiment_id}")

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


class EcrivainResultatsFlux:
    def __init__(self, racine_dossier, prefixe_nom: str):
        self.racine_dossier = racine_dossier
        self.prefixe_nom = prefixe_nom

    def ecrit_resultats_flux(
        self,
        generateur_resultats: Iterator[
            Tuple[str, List[Dict[str, Union[int, float, None]]]]
        ],
        experience_id: int,
    ):
        nom_colonnes = "Id Dataset,Numéro ligne,Nom métrique,Score"
        horodatage = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nom_fichier = f"{self.prefixe_nom}_{experience_id}_{horodatage}.csv"
        chemin_fichier = Path(self.racine_dossier) / nom_fichier

        with open(chemin_fichier, "w", newline="", encoding="utf-8") as fichier:
            fichier.write(f"Métrique terminée à {datetime.now()}\n")
            fichier.write(f"{nom_colonnes}\n")

        for nom_metrique, observations in generateur_resultats:
            logging.info(f"Métrique {nom_metrique} terminée, écriture en cours...")
            with open(chemin_fichier, "a", newline="", encoding="utf-8") as fichier:
                for obs in observations:
                    ligne = f"Experience_{experience_id},{obs['numero_ligne']},{nom_metrique},{obs['score']}\n"
                    fichier.write(ligne)
            logging.info(f"Métrique {nom_metrique} écrite dans {chemin_fichier}")

        return chemin_fichier
