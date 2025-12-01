import json
import logging
import re
from typing import Tuple, Optional, Type, Any
import requests
from deepeval.models import DeepEvalBaseLLM
from pydantic import BaseModel

from configuration import recupere_configuration

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


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
            donnees = json.loads(str(extrait_json(texte)))
            return schema(**donnees)
        except json.JSONDecodeError as exc:
            logging.error(
                "JSON invalide renvoyé par Albert après nettoyage, texte = %s, erreur = %s",
                texte,
                exc,
            )
            raise
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


def extrait_json(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        lignes = text.splitlines()
        lignes = lignes[1:]  # supprime l'ouverture
        if lignes and lignes[-1].strip().startswith("```"):
            lignes = lignes[:-1]
        text = "\n".join(lignes).strip()

    return text
