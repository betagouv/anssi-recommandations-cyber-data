from enum import Enum
from pathlib import Path
from typing import List
import json


class MetriqueEnum(Enum):
    ANSWER_RELEVANCY = "answer_relevancy"
    FAITHFULNESS = "faithfulness"
    TOXICITY = "toxicity"
    HALLUCINATION = "hallucination"
    JUDGE_PRECISION = "judge_precision"
    JUDGE_NOTATOR = "judge_notator"
    JUDGE_RAMBLING = "judge_rambling"
    OUTPUT_LENGTH = "output_length"


class ChargeurMetriques:
    def charge_depuis_fichier(self, chemin_fichier: Path) -> List[MetriqueEnum]:
        if not chemin_fichier.exists():
            raise FileNotFoundError(f"Le fichier {chemin_fichier} n'existe pas")

        with open(chemin_fichier, "r", encoding="utf-8") as f:
            config = json.load(f)

        metriques_str = config.get("metriques", [])
        metriques = []

        for metrique_str in metriques_str:
            try:
                metrique = MetriqueEnum(metrique_str)
                metriques.append(metrique)
            except ValueError:
                raise ValueError(f"Métrique invalide: {metrique_str}")

        return metriques
