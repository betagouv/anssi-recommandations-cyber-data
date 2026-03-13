import csv
from pathlib import Path

from evaluation.reformulation.evaluation import QuestionAEvaluer


class LecteurDatasetReformulation:
    def __init__(self, chemin: Path):
        self.chemin = chemin

    def charge_questions(self) -> list[QuestionAEvaluer]:
        questions = []
        with open(self.chemin, "r", encoding="utf-8") as fichier:
            lecteur_csv = csv.DictReader(fichier)
            for ligne in lecteur_csv:
                questions.append(
                    QuestionAEvaluer(
                        question=ligne["question_originale"],
                        reformulation_ideale=ligne["reformulation_ideale"],
                    )
                )
        return questions
