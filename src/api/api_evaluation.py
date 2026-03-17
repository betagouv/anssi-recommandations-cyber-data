import csv
from io import TextIOWrapper

from fastapi import APIRouter, UploadFile
from fastapi.params import Depends, File, Form
from pydantic import AnyHttpUrl

from adaptateurs.client_albert_reformulation_reel import (
    fabrique_client_albert_reformulation,
)
from adaptateurs.clients_albert import ClientAlbertReformulation
from evaluation.reformulation.evaluation import QuestionAEvaluer
from evaluation.service_evaluation import ServiceEvaluation
from evenement.bus import BusEvenement
from evenement.fabrique_bus_evenements import fabrique_bus_evenements
from infra.executeur_requete import ExecuteurDeRequete, fabrique_executeur_de_requete

api_evaluation = APIRouter(prefix="/evaluation")


@api_evaluation.post("/reformulation", status_code=201)
async def reformulation(
    file: UploadFile = File(...),  # type: ignore[assignment]
    url_prompt: AnyHttpUrl = Form(...),  # type: ignore[assignment]
    client_albert: ClientAlbertReformulation = Depends(  # type: ignore[assignment]
        fabrique_client_albert_reformulation
    ),
    bus_evenement: BusEvenement = Depends(fabrique_bus_evenements),  # type: ignore[assignment]
    service_evaluation: ServiceEvaluation = Depends(ServiceEvaluation),  # type: ignore[assignment]
    executeur_de_requete: ExecuteurDeRequete = Depends(fabrique_executeur_de_requete),  # type: ignore[assignment]
):
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
    service_evaluation.lance_reformulation(
        client_albert, bus_evenement, prompt, questions
    )
