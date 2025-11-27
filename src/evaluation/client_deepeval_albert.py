import requests
from deepeval.models import DeepEvalBaseLLM

from configuration import recupere_configuration


class ClientDeepEvalAlbert(DeepEvalBaseLLM):
    def __init__(self):
        configuration = recupere_configuration()
        self.cle_api = configuration.albert.cle_api
        self.url_base = configuration.albert.url

    def load_model(self):
        return self

    def _appel_api_albert(self, prompt: str) -> str:
        en_tetes = {
            "Authorization": f"Bearer {self.cle_api}",
            "Content-Type": "application/json",
        }

        charge_utile = {
            "model": "albert-large",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800,
        }

        reponse = requests.post(
            f"{self.url_base}/chat/completions",
            headers=en_tetes,
            json=charge_utile,
            timeout=60,
        )

        if reponse.status_code == 200:
            return reponse.json()["choices"][0]["message"]["content"]

        raise RuntimeError(f"Erreur API Albert {reponse.status_code} : {reponse.text}")

    def generate(self, messages):
        return self._appel_api_albert(messages)

    async def a_generate(self, messages):
        return self.generate(messages)

    def get_model_name(self) -> str:
        return "albert-large"
