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
from unittest.mock import AsyncMock, patch
from main_remplir_csv import traite_csv_par_lots_paralleles
from pathlib import Path


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


@pytest.mark.asyncio
async def test_main_lot_11_lignes_avec_taille_lot_5_ecrit_11_lignes():
    mock_lecteur = AsyncMock()

    mock_remplisseur = AsyncMock()
    mock_remplisseur.remplit_lot_lignes.side_effect = [
        [
            {"Réponse Bot": "R1"},
            {"Réponse Bot": "R2"},
            {"Réponse Bot": "R3"},
            {"Réponse Bot": "R4"},
            {"Réponse Bot": "R5"},
        ],  # Batch 1
        [
            {"Réponse Bot": "R6"},
            {"Réponse Bot": "R7"},
            {"Réponse Bot": "R8"},
            {"Réponse Bot": "R9"},
            {"Réponse Bot": "R10"},
        ],  # Batch 2
        [{"Réponse Bot": "R11"}],
        [],  # Fin
    ]

    mock_ecrivain = AsyncMock()
    mock_ecrivain.ecrit_ligne_depuis_lecteur_csv.return_value = Path("test_output.csv")

    with (
        patch("main_remplir_csv.LecteurCSV", return_value=mock_lecteur),
        patch("main_remplir_csv.RemplisseurReponses", return_value=mock_remplisseur),
        patch("main_remplir_csv.EcrivainSortie", return_value=mock_ecrivain),
        patch("main_remplir_csv.recupere_configuration"),
        patch("main_remplir_csv.ClientMQCHTTPAsync"),
    ):
        await traite_csv_par_lots_paralleles(
            Path("test.csv"), "test", Path("sortie"), taille_lot=5
        )

    assert mock_remplisseur.remplit_lot_lignes.call_count == 4
    assert mock_ecrivain.ecrit_ligne_depuis_lecteur_csv.call_count == 11


@pytest.mark.asyncio
async def test_main_lot_1_ligne_avec_taille_lot_5_ecrit_1_ligne():
    mock_lecteur = AsyncMock()
    mock_remplisseur = AsyncMock()
    mock_remplisseur.remplit_lot_lignes.side_effect = [
        [{"Réponse Bot": "R1"}],  # Batch 1
        [],
    ]

    mock_ecrivain = AsyncMock()
    mock_ecrivain.ecrit_ligne_depuis_lecteur_csv.return_value = Path("test_output.csv")

    with (
        patch("main_remplir_csv.LecteurCSV", return_value=mock_lecteur),
        patch("main_remplir_csv.RemplisseurReponses", return_value=mock_remplisseur),
        patch("main_remplir_csv.EcrivainSortie", return_value=mock_ecrivain),
        patch("main_remplir_csv.recupere_configuration"),
        patch("main_remplir_csv.ClientMQCHTTPAsync"),
    ):
        await traite_csv_par_lots_paralleles(
            Path("test.csv"), "test", Path("sortie"), taille_lot=5
        )

    assert mock_remplisseur.remplit_lot_lignes.call_count == 2
    assert mock_ecrivain.ecrit_ligne_depuis_lecteur_csv.call_count == 1
