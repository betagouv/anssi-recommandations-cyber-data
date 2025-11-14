import pytest
import asyncio
from remplisseur_reponses import RemplisseurReponses, ReponseQuestion
import time


class MockClientQuestions:
    def pose_question(self, question: str) -> ReponseQuestion:
        return ReponseQuestion(
            reponse=f"Réponse à {question}", paragraphes=[], question=question
        )

    async def pose_question_async(self, question: str) -> ReponseQuestion:
        await asyncio.sleep(0.01)
        return ReponseQuestion(
            reponse=f"Réponse à {question}", paragraphes=[], question=question
        )


@pytest.mark.asyncio
async def test_traite_lot_parallele():
    questions = ["Q1", "Q2", "Q3"]
    mock_client = MockClientQuestions()
    remplisseur = RemplisseurReponses(client=mock_client)

    debut = time.time()
    resultats = await remplisseur.traite_lot_parallele(questions, max_workers=3)
    duree_parallele = time.time() - debut

    assert len(resultats) == 3
    assert all("Réponse Bot" in resultat for resultat in resultats)
    assert duree_parallele < 0.02
