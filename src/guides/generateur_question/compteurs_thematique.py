from abc import ABC, abstractmethod
from typing import Any

import numpy as np
from sklearn.cluster import AgglomerativeClustering  # type: ignore[import-untyped]

from guides.generateur_question.utils import _decoupe_en_phrases, _charge_encodeur


class CompteurThematiques(ABC):
    @abstractmethod
    def nombre_topics(self, paragraphe: str) -> int:
        raise NotImplementedError


class CompteursThematique(CompteurThematiques):
    def __init__(
        self,
        *,
        modele_hf: str = "BAAI/bge-m3",
        seuil_distance: float = 0.35,
        min_topics: int = 1,
        max_topics: int = 10,
        min_phrases: int = 2,
        encodeur: Any | None = None,
    ) -> None:
        self.modele_hf = modele_hf
        self.seuil_distance = seuil_distance
        self.min_topics = min_topics
        self.max_topics = max_topics
        self.min_phrases = min_phrases
        self.encodeur = encodeur

    def nombre_topics(self, paragraphe: str) -> int:
        phrases = _decoupe_en_phrases(paragraphe)
        if len(phrases) == 0:
            return 0
        if len(phrases) < self.min_phrases:
            return 1
        encodeur = (
            self.encodeur
            if self.encodeur is not None
            else _charge_encodeur(self.modele_hf)
        )
        vecteurs = encodeur.encode(
            phrases,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        ).astype(np.float32)

        distances = 1.0 - (vecteurs @ vecteurs.T)
        np.fill_diagonal(distances, 0.0)

        createur_de_cluster = AgglomerativeClustering(
            n_clusters=None,
            metric="precomputed",
            linkage="average",
            distance_threshold=self.seuil_distance,
        )
        etiquettes = createur_de_cluster.fit_predict(distances)

        n = int(len(set(etiquettes.tolist())))
        n = max(self.min_topics, min(self.max_topics, n))
        return n


def calcule_nombre_questions(
    paragraphe: str, compteur_thematiques: CompteurThematiques | None = None
) -> int:
    compteur = (
        compteur_thematiques
        if compteur_thematiques is not None
        else CompteursThematique()
    )
    n_topics = compteur.nombre_topics(paragraphe)
    if n_topics == 0:
        return 0
    return max(3, min(10, n_topics))
