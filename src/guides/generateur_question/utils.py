import json
import re
from functools import lru_cache
from pathlib import Path

import numpy as np


def _charge_prompt_systeme() -> str:
    racine_projet = Path(__file__).resolve().parents[3]
    chemin_prompt = racine_projet / "tempaltes" / "prompt_generateur_questions.txt"
    return chemin_prompt.read_text(encoding="utf-8").strip()


def _extrait_objet_json(texte: str) -> str:
    t = (texte or "").strip()
    t = re.sub(r"^\s*```(?:json)?\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s*```\s*$", "", t)
    t = t.lstrip("\ufeff")
    match = re.search(r"\{.*\}", t, flags=re.DOTALL)
    if not match:
        raise ValueError("Aucun objet JSON détecté dans la sortie du modèle.")
    return match.group(0)


def parse_questions_depuis_contenu(contenu: str) -> list[str]:
    bloc = _extrait_objet_json(contenu)
    obj = json.loads(bloc)
    questions = obj.get("questions", [])
    if not isinstance(questions, list):
        return []
    return [q.strip() for q in questions if isinstance(q, str) and q.strip()]


def _compte_mots(texte: str) -> int:
    return len(re.findall(r"\b\w+\b", texte, flags=re.UNICODE))


def _decoupe_en_phrases(texte: str) -> list[str]:
    texte = re.sub(r"\s+", " ", (texte or "").strip())
    if not texte:
        return []
    phrases = re.split(r"(?<=[.!?])\s+", texte)
    return [p.strip() for p in phrases if p.strip()]


def _compte_phrases(texte: str) -> int:
    phrases = re.split(r"[.!?]\s+", texte.strip())
    phrases = [p for p in phrases if p.strip()]
    return max(1, len(phrases))


def _normalise_l2(m: np.ndarray) -> np.ndarray:
    normes = np.linalg.norm(m, axis=1, keepdims=True) + 1e-12
    return m / normes


@lru_cache(maxsize=4)
def _charge_encodeur(modele_hf: str):
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(modele_hf)
