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
        self.modele = configuration.albert.modele

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
            "model": self.modele,
            "messages": messages,
            "max_tokens": 4000,
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
            logging.info(
                "Erreur serveur 500, nouvelle tentative dans %s secondes",
                self.temps_attente,
            )
            return self._appel_api_albert(
                prompt, nombre_appels_restants=nombre_appels_restants - 1
            )

        if reponse.status_code == 200:
            try:
                corps = reponse.json()
                choix = corps["choices"][0]
                finish_reason = choix.get("finish_reason")
                message = choix["message"]
                if finish_reason and finish_reason != "stop":
                    logging.warning(
                        "Albert a terminé avec finish_reason=’%s’", finish_reason
                    )
                contenu = message.get("content")
                if contenu is None:
                    logging.warning(
                        "Albert a retourné un contenu None (finish_reason=%s)",
                        finish_reason,
                    )
                    return "{}"
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
        donnees = self._parse_json(texte)
        return self._instancie_schema(schema, donnees)

    def _parse_json(self, texte: str) -> dict[str, Any]:
        try:
            resultat = json_repair.loads(texte)
            return resultat if isinstance(resultat, dict) else {}
        except json.JSONDecodeError as exc:
            logging.error(
                "JSON invalide renvoyé par Albert, texte = %s, erreur = %s", texte, exc
            )
            raise

    def _instancie_schema(self, schema: Type[BaseModel], donnees: dict) -> BaseModel:
        try:
            return schema(**donnees)  # type: ignore
        except Exception as exc:
            nom = getattr(schema, "__name__", repr(schema))
            logging.error(
                "Impossible d'instancier le schéma %s avec les données %s : %s",
                nom,
                donnees,
                exc,
            )
            return self._instancie_schema_avec_fallback(schema, donnees, nom, exc)

    def _instancie_schema_avec_fallback(
        self, schema: Type[BaseModel], donnees: dict, nom: str, exc_originale: Exception
    ) -> BaseModel:
        if not donnees:
            logging.warning(
                "Le LLM a retourné un contenu vide ({}), schéma %s instancié avec des listes vides",
                nom,
            )
            return schema(
                **{
                    name: []
                    for name, field in schema.model_fields.items()
                    if getattr(field.annotation, "__origin__", None) is list
                }
            )  # type: ignore
        cleaned = self._filtre_items_invalides(schema, donnees, nom)
        try:
            return schema(**cleaned)  # type: ignore
        except Exception:
            raise exc_originale

    def _filtre_items_invalides(
        self, schema: Type[BaseModel], donnees: dict, nom_schema: str
    ) -> dict:
        cleaned = dict(donnees)
        for field_name, field_info in schema.model_fields.items():
            if getattr(field_info.annotation, "__origin__", None) is not list:
                continue
            args = getattr(field_info.annotation, "__args__", ())
            if not args or not hasattr(args[0], "model_fields"):
                continue
            item_type = args[0]
            items_valides: list[Any] = []
            items_invalides: list[Any] = []
            for item in cleaned.get(field_name, []):
                (
                    items_valides if _est_valide(item, item_type) else items_invalides
                ).append(item)
            for item in items_invalides:
                logging.warning(
                    "Item invalide écarté du champ '%s' (schéma %s) : %s",
                    field_name,
                    nom_schema,
                    item,
                )
            cleaned[field_name] = items_valides
        return cleaned

    async def a_generate(
        self,
        prompt: str,
        schema: Optional[Type[BaseModel]] = None,
        **kwargs: Any,
    ) -> Any:
        return self.generate(prompt, schema=schema, **kwargs)

    def get_model_name(self) -> str:
        return self.modele


def _est_valide(item: Any, type_: type) -> bool:
    try:
        type_(**item) if isinstance(item, dict) else item
        return True
    except Exception:
        return False


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
