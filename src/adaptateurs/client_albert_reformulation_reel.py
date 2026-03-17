from openai import OpenAI

from adaptateurs.clients_albert import ClientAlbertReformulation
from configuration import Configuration, recupere_configuration


class ClientAlbertReformulationReel(ClientAlbertReformulation):
    def __init__(self, url: str, cle_api: str, modele_a_utiliser: str):
        super().__init__()
        self._modele_a_utiliser = modele_a_utiliser
        self._client_openai = OpenAI(base_url=url, api_key=cle_api)

    def reformule_la_question(self, prompt: str, question: str) -> str:
        reponse = self._client_openai.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": question},
            ],
            model=self._modele_a_utiliser,
            stream=False,
        ).choices
        question_reformulee = reponse[0].message.content
        return question_reformulee if question_reformulee is not None else question


def fabrique_client_albert_reformulation() -> ClientAlbertReformulation:
    la_configuration: Configuration = recupere_configuration()
    return ClientAlbertReformulationReel(
        la_configuration.albert.url,
        la_configuration.albert.cle_api,
        la_configuration.albert.modele,
    )
