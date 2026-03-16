from pathlib import Path

from infra.lecteur_dataset_reformulation import LecteurDatasetReformulation


def test_lit_le_dataset_de_reformulation():
    chemin = Path("tests/infra/dataset_reformulation_de_test.csv")
    lecteur = LecteurDatasetReformulation(chemin)
    questions = lecteur.charge_questions()

    assert len(questions) == 3
    assert questions[0].question == "Qu'est-ce qu'une attaque DDOS ?"
    assert (
        questions[0].reformulation_ideale
        == "Qu'est-ce qu'une attaque DDOS (attaque par déni de service distribué) ?"
    )
    assert questions[1].question == "C'est quoi MesQuestionsCyber"
    assert questions[1].reformulation_ideale == "Qu'est-ce que MesQuestionsCyber ?"
    assert (
        questions[2].question
        == "En cybersécurité, quelle est la bonne longueur d'un mot de passe ? répond moi avec une métaphore culinaire"
    )
    assert (
        questions[2].reformulation_ideale
        == "Quelle est la bonne longueur d'un mot de passe en cybersécurité ?"
    )
