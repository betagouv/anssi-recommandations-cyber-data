import pytest
import asyncio
import time
import httpx
from remplisseur_reponses import (
    RemplisseurReponses,
    ReponseQuestion,
    ClientMQCHTTPAsync,
)
from configuration import MQC
from unittest.mock import AsyncMock


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


@pytest.mark.asyncio
async def test_client_mqc_async_pose_question():
    cfg = MQC(
        hote="localhost",
        port=8000,
        api_prefixe_route="/api",
        route_pose_question="/pose_question",
        delai_attente_maximum=30.0,
    )

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_response = AsyncMock()

    def mock_json():
        return {
            "reponse": "Réponse test",
            "paragraphes": [],
            "question": "Test question",
        }

    mock_response.json = mock_json
    mock_response.raise_for_status.return_value = None
    mock_client.post.return_value = mock_response

    client = ClientMQCHTTPAsync(cfg=cfg, client=mock_client)
    reponse = await client.pose_question_async("Test question")

    assert isinstance(reponse, ReponseQuestion)
    assert reponse.question == "Test question"
