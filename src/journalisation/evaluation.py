from typing import Union


class Evaluation:
    id_experimentation: int | str
    metriques: list[dict]

    def __init__(self, id_experimentation: int | str, metriques: list[dict]):
        self.id_experimentation = id_experimentation
        self.metriques = metriques


class EntrepotEvaluation:
    def lit(self, id_evaluation: int | str) -> Union[Evaluation, None]:
        pass

    def persiste(self, evaluation: Evaluation) -> None:
        pass


class EntrepotEvaluationMemoire(EntrepotEvaluation):
    evaluations: list[Evaluation] = []

    def __init__(self) -> None:
        super().__init__()
        self.evaluations: list[Evaluation] = []

    def persiste(self, evaluation: Evaluation) -> None:
        self.evaluations.append(evaluation)

    def lit(self, id_evaluation: int | str) -> Evaluation | None:
        for evaluation in self.evaluations:
            if evaluation.id_experimentation == id_evaluation:
                return evaluation
        return None


def fabrique_entrepot_evaluation() -> EntrepotEvaluation:
    return EntrepotEvaluationMemoire()
