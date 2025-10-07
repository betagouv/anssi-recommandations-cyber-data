from enum import Enum
from pathlib import Path
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


class Metriques:
    def recupere_depuis_fichier(self, chemin_fichier: Path) -> list[MetriqueEnum]:
        if not chemin_fichier.exists():
            raise FileNotFoundError(f"Le fichier {chemin_fichier} n'existe pas")

        with open(chemin_fichier, "r", encoding="utf-8") as f:
            config = json.load(f)

        metriques_str = config.get("metriques", [])

        return [MetriqueEnum(m) for m in metriques_str]
