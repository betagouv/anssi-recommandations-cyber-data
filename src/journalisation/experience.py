from typing import Union
import logging
import requests
from configuration import recupere_configuration
from evalap import EvalapExperienceHttp, EvalapClient


class Experience:
    id_experimentation: int | str
    metriques: list[dict]

    def __init__(self, id_experimentation: int | str, metriques: list[dict]):
        self.id_experimentation = id_experimentation
        self.metriques = metriques


class EntrepotExperience:
    def lit(self, id_experience: int | str) -> Union[Experience, None]:
        pass

    def persiste(self, experience: Experience) -> None:
        pass


class EntrepotExperienceMemoire(EntrepotExperience):
    experiences: list[Experience] = []

    def __init__(self) -> None:
        super().__init__()
        self.experiences: list[Experience] = []

    def persiste(self, experience: Experience) -> None:
        self.experiences.append(experience)

    def lit(self, id_experience: int | str) -> Experience | None:
        for experience in self.experiences:
            if experience.id_experimentation == id_experience:
                return experience
        return None


class EntrepotExperienceHttp(EntrepotExperience):
    def __init__(self, client_experience: EvalapExperienceHttp):
        super().__init__()
        self.client_experience = client_experience

    def lit(self, id_experience: int | str) -> Union[Experience, None]:
        experience = self.client_experience.lit(id_experience)

        if experience is None:
            logging.error(f"Impossible de récupérer l'expérience {id_experience}")
            return None

        metriques_collectees: dict[int, dict[str, Union[int, float]]] = {}
        for metrique in experience.results:
            for obs in metrique.observation_table:
                numero_ligne = obs.num_line
                if numero_ligne not in metriques_collectees:
                    metriques_collectees[numero_ligne] = {"numero_ligne": numero_ligne}
                if metrique.metric_name != "numero_ligne" and obs.score is not None:
                    metriques_collectees[numero_ligne][metrique.metric_name] = obs.score

        return Experience(
            id_experimentation=id_experience,
            metriques=list(metriques_collectees.values()),
        )


def fabrique_entrepot_experience() -> EntrepotExperience:
    configuration = recupere_configuration()
    if configuration.est_evaluation_deepeval:
        return EntrepotExperienceMemoire()
    session = requests.session()
    return EntrepotExperienceHttp(
        client_experience=EvalapClient(configuration, session=session).experience
    )
