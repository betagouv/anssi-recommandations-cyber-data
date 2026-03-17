from adaptateurs.clients_albert import ClientAlbertReformulation
from evaluation.reformulation.evaluation import QuestionAEvaluer
from evenement.bus import BusEvenement


class ServiceEvaluation:
    def lance_reformulation(
        self,
        client_albert: ClientAlbertReformulation,
        bus_evenement: BusEvenement,
        prompt: str,
        questions: list[QuestionAEvaluer],
    ):
        pass
