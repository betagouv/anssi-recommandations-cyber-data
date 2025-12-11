import json
import logging
import re
from typing import Tuple, Optional, Type, Any
import json_repair
import requests
from deepeval.models import DeepEvalBaseLLM
from pydantic import BaseModel
from configuration import recupere_configuration
import time


class ClientDeepEvalAlbert(DeepEvalBaseLLM):
    def __init__(
        self, configuration=recupere_configuration(), temps_attente: float = 60.0
    ):
        self.cle_api = configuration.albert.cle_api
        self.url_base = configuration.albert.url
        self.temps_attente = temps_attente

    def load_model(self):
        return self

    def _appel_api_albert(self, prompt: str, nombre_appels_restants: int = 3) -> str:
        en_tetes = {
            "Authorization": f"Bearer {self.cle_api}",
            "Content-Type": "application/json",
        }

        messages = [
            {"role": "system", "content": "Answer in JSON format strictly."},
            {"role": "user", "content": prompt},
        ]

        charge_utile = {
            "model": "albert-large",
            "messages": messages,
            "max_tokens": 800,
        }

        try:
            reponse = requests.post(
                f"{self.url_base}/chat/completions",
                headers=en_tetes,
                json=charge_utile,
                timeout=60,
            )
        except Exception as exc:
            logging.error("Erreur réseau lors de l'appel à Albert : %s", exc)
            raise

        if reponse.status_code == 500:
            time.sleep(self.temps_attente)
            logging.info("Erreur serveur 500, nouvelle tentative dans %s secondes", self.temps_attente)
            return self._appel_api_albert(
                prompt, nombre_appels_restants=nombre_appels_restants - 1
            )

        if reponse.status_code == 200:
            try:
                contenu = reponse.json()["choices"][0]["message"]["content"]
                _, reponse_nettoyee = separe_reflexion_reponse(contenu)
                return reponse_nettoyee
            except Exception as exc:
                logging.error("Échec extraction JSON Albert : %s", exc)
                raise RuntimeError(f"Réponse non conforme d’Albert : {reponse.text}")

        raise RuntimeError(f"Erreur API Albert {reponse.status_code} : {reponse.text}")

    def generate(
        self,
        prompt: str,
        schema: Optional[Type[BaseModel]] = None,
        **kwargs: Any,
    ) -> Any:
        texte = self._appel_api_albert(prompt)

        if schema is None:
            return texte

        try:
            donnees = json_repair.loads(texte)
        except json.JSONDecodeError as exc:
            logging.error(
                "JSON invalide renvoyé par Albert après nettoyage, texte = %s, erreur = %s",
                texte,
                exc,
            )
            raise

        try:
            return schema(**donnees)  # type: ignore
        except Exception as exc:
            logging.error(
                "Impossible d'instancier le schéma %s avec les données %s : %s",
                getattr(schema, "__name__", repr(schema)),
                donnees,
                exc,
            )
            raise

    async def a_generate(
        self,
        prompt: str,
        schema: Optional[Type[BaseModel]] = None,
        **kwargs: Any,
    ) -> Any:
        return self.generate(prompt, schema=schema, **kwargs)

    def get_model_name(self) -> str:
        return "albert-large"


def separe_reflexion_reponse(
    reponse: str, tokens_reflexion: tuple[str, ...] = ("</think>", "[/think]")
) -> Tuple[Optional[str], str]:
    for token in tokens_reflexion:
        pattern = re.escape(token)
        match = re.search(pattern, reponse, re.IGNORECASE)
        if match:
            start, end = match.span()
            reflexion = reponse[:end].strip()
            reponse = reponse[end:].strip()
            return reflexion, reponse
    return None, reponse.strip()
