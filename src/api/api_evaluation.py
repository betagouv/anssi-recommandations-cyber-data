import csv
import shutil
import uuid
from io import TextIOWrapper
from pathlib import Path

from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.params import Depends, File, Form
from pydantic import BaseModel, AnyHttpUrl

from adaptateurs.client_albert_reformulation_reel import (
    fabrique_client_albert_reformulation,
)
from adaptateurs.clients_albert import ClientAlbertReformulation
from evaluation.mqc.collecte_reponses_mqc import (
    CollecteurDeReponses,
    fabrique_collecteur_de_reponses,
)
from evaluation.reformulation.evaluation import QuestionAEvaluer
from evaluation.service_evaluation import ServiceEvaluation, fabrique_service_evaluation
from evenement.bus import BusEvenement
from evenement.fabrique_bus_evenements import fabrique_bus_evenements
from infra.executeur_requete import ExecuteurDeRequete, fabrique_executeur_de_requete

api_evaluation = APIRouter(prefix="/evaluation")


class ReponseEvaluationEnCours(BaseModel):
    id: uuid.UUID
    nombre_questions: int


@api_evaluation.post("/", status_code=200)
async def evaluation(
    fichier_evaluation: UploadFile = File(...),  # type: ignore[assignment]
    fichier_mapping: UploadFile = File(...),  # type: ignore[assignment]
    service_evaluation: ServiceEvaluation = Depends(fabrique_service_evaluation),  # type: ignore[assignment]
    collecteur_de_reponses: CollecteurDeReponses = Depends( # type: ignore[assignment]
        fabrique_collecteur_de_reponses
    ),
):
    chemin_evaluation = Path(f"/tmp/{fichier_evaluation.filename}")
    with chemin_evaluation.open("wb") as buffer:
        shutil.copyfileobj(fichier_evaluation.file, buffer)

    chemin_mapping = Path(f"/tmp/{fichier_mapping.filename}")
    with chemin_mapping.open("wb") as buffer:
        shutil.copyfileobj(fichier_mapping.file, buffer)

    await service_evaluation.lance_evaluation(
        chemin_evaluation, chemin_mapping, collecteur_de_reponses
    )


@api_evaluation.post(
    "/reformulation",
    status_code=201,
)
async def reformulation(
    file: UploadFile = File(...),  # type: ignore[assignment]
    url_prompt: AnyHttpUrl = Form(...),  # type: ignore[assignment]
    client_albert: ClientAlbertReformulation = Depends(  # type: ignore[assignment]
        fabrique_client_albert_reformulation
    ),
    bus_evenement: BusEvenement = Depends(fabrique_bus_evenements),  # type: ignore[assignment]
    service_evaluation: ServiceEvaluation = Depends(fabrique_service_evaluation),  # type: ignore[assignment]
    executeur_de_requete: ExecuteurDeRequete = Depends(fabrique_executeur_de_requete),  # type: ignore[assignment]
) -> ReponseEvaluationEnCours:
    lecteur_csv = csv.DictReader(TextIOWrapper(file.file, encoding="utf-8"))
    questions = [
        QuestionAEvaluer(
            question=ligne["question_originale"],
            reformulation_ideale=ligne["reformulation_ideale"],
        )
        for ligne in lecteur_csv
    ]
    executeur_de_requete.initialise_connexion()
    reponse = executeur_de_requete.recupere(str(url_prompt))
    prompt = reponse.text
    if reponse.status_code != 200:
        raise HTTPException(
            status_code=404,
            detail=f"Prompt introuvable à l’adresse : {url_prompt}",
        )
    evaluation_en_cours = service_evaluation.lance_reformulation(
        client_albert, bus_evenement, prompt, questions
    )
    return ReponseEvaluationEnCours(
        id=evaluation_en_cours.id, nombre_questions=len(questions)
    )
