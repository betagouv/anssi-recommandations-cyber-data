from fastapi import APIRouter, BackgroundTasks
from fastapi.params import Depends
from pydantic import BaseModel

from jeopardy.service import fabrique_service_jeopardy, ServiceJeopardy

api_jeopardy = APIRouter(prefix="/jeopardy")


class RequeteJeopardy(BaseModel):
    id_collection: str
    nom_collection: str
    description_collection: str


@api_jeopardy.post("/", status_code=200)
def jeopardy(
    requete: RequeteJeopardy,
    background_tasks: BackgroundTasks,
    service_jeopardy: ServiceJeopardy = Depends(fabrique_service_jeopardy),  # type: ignore[assignment]
):
    background_tasks.add_task(
        service_jeopardy.jeopardyse,
        requete.nom_collection,
        requete.description_collection,
        requete.id_collection,
    )
    return {"message": "Jeopardy en cours d’exécution..."}
