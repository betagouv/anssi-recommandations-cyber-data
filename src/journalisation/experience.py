from typing import Union


class Experience:
    id_experimentation: int
    metriques: list[dict]

    def __init__(self, id_experimentation: int, metriques: list[dict]):
        self.id_experimentation = id_experimentation
        self.metriques = metriques


class EntrepotExperience:
    def lit(self, id_experience) -> Union[Experience, None]:
        pass


class EntrepotExperienceMemoire(EntrepotExperience):
    experiences: list[Experience] = []

    def __init__(self):
        super().__init__()
        self.experiences: list[Experience] = []

    def persiste(self, experience: Experience):
        self.experiences.append(experience)

    def lit(self, id_experience) -> Experience | None:
        for experience in self.experiences:
            if experience.id_experimentation == id_experience:
                return experience
        return None
