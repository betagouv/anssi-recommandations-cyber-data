from typing import Union


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


def fabrique_entrepot_experience() -> EntrepotExperience:
    return EntrepotExperienceMemoire()
